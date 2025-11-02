import router from "@/router"

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

  // 通用请求方法
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    const url = this.buildUrl(endpoint)
    const token = localStorage.getItem('authToken')
    if (token) {  // 如果有保存的认证令牌，添加到请求头部
      this.setDefaultHeaders({
        'Authorization': `Bearer ${token}`
      })
    }
    const config: RequestInit = {
      ...options,
      headers: this.mergeHeaders(options.headers as Record<string, string>),
    }

    return (async () => {
      const response = await fetch(url, config)

      // 检查响应状态
      if (response.ok === false) {
        const text = await response.text()
        console.log('error:', text)
        if (text.includes('Token has expired')) {
          localStorage.removeItem('authToken')
          router.push('/login')
        }
        throw new HttpError(
          `HTTP error! status: ${response.status}`,
          response.status,
          text,
        )
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
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      headers,
      body: body ? JSON.stringify(body) : undefined,
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
// const httpClient = new HttpClient('http://103.151.217.252:65533/api')
const httpClient = new HttpClient('http://localhost:65533/api')


export type { ApiResponse, HttpError }
export { HttpClient, httpClient }