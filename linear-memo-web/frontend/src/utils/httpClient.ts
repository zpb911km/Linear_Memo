import router from '@/router'
import { h } from 'vue'

// 自定义HTTP客户端
class HttpClient {
  private baseUrl: string
  private defaultHeaders: Record<string, string>

  constructor(baseUrl: string = '') {
    this.baseUrl = baseUrl
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    }

    // 如果有保存的认证令牌，自动添加到默认头部
    const token = localStorage.getItem('authToken')
    if (token) {
      this.defaultHeaders['Authorization'] = `Bearer ${token}`
    }
  }

  // 获取默认请求头的副本
  get headers(): Record<string, string> {
    return { ...this.defaultHeaders }
  }

  get url(): string {
    return this.baseUrl
  }

  // 设置默认请求头
  setDefaultHeaders(headers: Record<string, string>) {
    this.defaultHeaders = { ...this.defaultHeaders, ...headers }
  }

  // 合并请求头
  private mergeHeaders(headers?: Record<string, string>): Record<string, string> {
    return { ...this.defaultHeaders, ...headers }
  }

  // 构造完整URL
  private buildUrl(endpoint: string): string {
    if (endpoint.startsWith('http')) {
      return endpoint
    }
    return this.baseUrl + endpoint
  }

  // 专门用于文件上传的POST请求
  async postFile<T>(endpoint: string, formData: FormData): Promise<ApiResponse<T>> {
    // 对于文件上传，我们只保留认证头部，移除Content-Type以让浏览器自动设置
    const token = localStorage.getItem('authToken')
    const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {}

    return this.request<T>(endpoint, {
      method: 'POST',
      headers,
      body: formData,
    })
  }

  // 通用请求方法
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    const url = this.buildUrl(endpoint)
    const token = localStorage.getItem('authToken')
    const headers = this.mergeHeaders(options.headers as Record<string, string>)
    if (token) {
      // 如果有保存的认证令牌，添加到请求头部
      headers['Authorization'] = `Bearer ${token}`
    }

    // 如果不是FormData请求，确保Content-Type是application/json
    const isFormDataRequest = options.body instanceof FormData
    let config: RequestInit

    if (isFormDataRequest) {
      // FormData请求：使用提供的headers（可能已删除Content-Type）
      config = {
        ...options,
        headers: headers,
      }
      // 确保Authorization头被正确设置
      if (token && !config.headers) {
        config.headers = { Authorization: `Bearer ${token}` }
      }
      // else if (token && config.headers && !config.headers['Authorization']) {
      //   config.headers = { ...config.headers, Authorization: `Bearer ${token}` }
      // }
    } else {
      // 普通请求：使用JSON Content-Type
      config = {
        ...options,
        headers: this.mergeHeaders(options.headers as Record<string, string>),
      }
    }

    return (async () => {
      const response = await fetch(url, config)

      // // 检查响应状态
      // if (response.ok === false) {
      //   const json_resp = await response.json()
      //   if (json_resp.msg.includes('Token has expired')) {
      //     localStorage.removeItem('authToken')
      //     router.push('/login')
      //   }
      //   throw new HttpError(`HTTP error! status: ${response.status}`, response.status, json_resp.msg)
      // }

      // 401错误：认证令牌失效，跳转到登录页面
      if (response.status === 401) {
        localStorage.removeItem('authToken')
        router.push('/login')
        console.log('Unauthorized jumped')
        // throw new HttpError('Unauthorized', response.status, 'Authentication token has expired')
      }

      // 尝试解析JSON
      let data: T | null = null
      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        data = await response.json()
      }

      const result = {
        data,
        status: response.status,
        statusText: response.statusText,
        headers: response.headers,
      }

      return result
    })()
  }

  // GET请求
  async get<T>(endpoint: string, headers?: Record<string, string>): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'GET', headers })
  }

  // POST请求
  async post<T>(
    endpoint: string,
    body?: any,
    headers?: Record<string, string>,
    options: { isFormData?: boolean } = {},
  ): Promise<ApiResponse<T>> {
    const { isFormData = false } = options

    let processedBody = body
    let processedHeaders = headers

    if (isFormData) {
      // 如果是FormData，不进行JSON序列化，也不设置application/json头部
      processedBody = body
      // 如果没有提供自定义头部，不设置默认的Content-Type，让浏览器自动设置
      if (!headers) {
        processedHeaders = { ...this.defaultHeaders }
        delete processedHeaders['Content-Type'] // 允许浏览器自动设置Content-Type
      } else {
        processedHeaders = { ...headers }
      }
    } else {
      processedBody = body ? JSON.stringify(body) : undefined
      processedHeaders = headers
    }

    return this.request<T>(endpoint, {
      method: 'POST',
      headers: processedHeaders,
      body: processedBody,
    })
  }

  // PUT请求
  async put<T>(
    endpoint: string,
    body?: any,
    headers?: Record<string, string>,
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      headers,
      body: body ? JSON.stringify(body) : undefined,
    })
  }

  // DELETE请求
  async delete<T>(endpoint: string, headers?: Record<string, string>): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'DELETE',
      headers,
    })
  }
}

// Http错误类
class HttpError extends Error {
  status: number
  body: string

  constructor(message: string, status: number, body: string) {
    super(message)
    this.status = status
    this.body = body
  }
}

// API响应类型
interface ApiResponse<T> {
  data: T | null
  status: number
  statusText: string
  headers: Headers
}

// 创建默认的HTTP客户端实例
// const httpClient = new HttpClient('http://172.18.91.245:65533/api')
// const httpClient = new HttpClient('http://103.151.217.252:65533/api')
const httpClient = new HttpClient('http://localhost:65533/api')

export type { ApiResponse, HttpError }
export { HttpClient, httpClient }
