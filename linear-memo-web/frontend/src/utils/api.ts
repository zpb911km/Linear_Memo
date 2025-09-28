// API交互模块
import { httpClient, type ApiResponse } from './httpClient'
import { useNotificationStore } from '../stores/notificationStore'
import type { Card, Deck, Arrangement, DeckDetail } from './types'

// API状态类型
interface ApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
  execute: () => Promise<void>
}

// 创建API状态的工厂函数
function createApiState<T>(
  apiCall: () => Promise<ApiResponse<T>>,
  initialValue: T | null = null,
): ApiState<T> {
  let data: T | null = initialValue
  let loading = false
  let error: string | null = null

  const execute = async () => {
    loading = true
    error = null

    try {
      const response = await apiCall()
      data = response.data
    } catch (err: any) {
      error = err.message || 'An error occurred'
    } finally {
      loading = false
    }
  }

  return {
    data,
    loading,
    error,
    execute,
  }
}

// 带反馈的API调用函数
async function callApiWithFeedback<T>(
  apiCall: () => Promise<ApiResponse<T>>,
  successMessage?: string,
  errorMessage?: string,
): Promise<T | null> {
  const notificationStore = useNotificationStore()

  // 显示进度条
  notificationStore.showProgressBar()

  try {
    const response = await apiCall()

    // 隐藏进度条
    notificationStore.hideProgressBar()

    // 显示成功消息
    if (successMessage) {
      notificationStore.showSuccess(successMessage)
    }

    return response.data
  } catch (error: any) {
    // 隐藏进度条
    notificationStore.hideProgressBar()

    // 显示错误消息
    const message = errorMessage || error.message || 'An error occurred'
    notificationStore.showError(message)

    return null
  }
}

// 卡组管理API
// 创建卡组
async function createDeck(deckData: Omit<Deck, 'id'>): Promise<any> {
  return callApiWithFeedback(
    () => httpClient.post<any>('/decks', deckData),
    '卡组创建成功',
    '创建卡组失败',
  ) as Promise<any>
}

interface ExtendedDeck extends Deck {
  arrangement: number
}

// 编辑卡组
async function updateDeck(deckId: number, deckData: Partial<ExtendedDeck>): Promise<any> {
  return callApiWithFeedback(
    () => httpClient.put<any>(`/decks/${deckId}`, deckData),
    '卡组更新成功',
    '更新卡组失败',
  ) as Promise<any>
}

// 删除卡组
async function deleteDeck(deckId: number): Promise<any> {
  return callApiWithFeedback(
    () => httpClient.delete<any>(`/decks/${deckId}`),
    '卡组删除成功',
    '删除卡组失败',
  ) as Promise<any>
}

// 获取所有卡组
async function fetchDecks(): Promise<Deck[]> {
  return callApiWithFeedback(
    () => httpClient.get<Deck[]>('/decks'),
    '卡组列表获取成功',
    '获取卡组列表失败',
  ) as unknown as Promise<Deck[]>
}

// 卡组详情
async function fetchDeckDetail(deckId: number): Promise<DeckDetail> {
  return callApiWithFeedback(
    () => httpClient.get<DeckDetail>(`/decks/${deckId}`),
    '卡组详情获取成功',
    '获取卡组详情失败',
  ) as unknown as Promise<DeckDetail>
}

// 卡片管理API
// 获取卡组的所有卡片
async function fetchCards(deckId: number): Promise<Card[]> {
  return callApiWithFeedback(
    () => httpClient.get<Card[]>(`/cards?deck_id=${deckId}`),
    '卡片列表获取成功',
    '获取卡片列表失败',
  ) as unknown as Promise<Card[]>
}

// 添加卡片
async function addCard(cardData: Omit<Card, 'id'>): Promise<any> {
  return callApiWithFeedback(
    () => httpClient.post<any>('/cards', cardData),
    '卡片添加成功',
    '添加卡片失败',
  ) as Promise<any>
}

// 更新卡片
async function updateCard(cardId: number, cardData: Partial<Card>): Promise<any> {
  return callApiWithFeedback(
    () => httpClient.put<any>(`/cards/${cardId}`, cardData),
    '卡片更新成功',
    '更新卡片失败',
  ) as Promise<any>
}

// 删除卡片
async function deleteCard(cardId: number): Promise<any> {
  return callApiWithFeedback(
    () => httpClient.delete<any>(`/cards/${cardId}`),
    '卡片删除成功',
    '删除卡片失败',
  ) as Promise<any>
}

// 获取卡组的待复习卡片
async function fetchReviewCards(deckId: number): Promise<Card[]> {
  return callApiWithFeedback(
    () => httpClient.get<Card[]>(`/cards/review?deck_id=${deckId}`),
    '待复习卡片列表获取成功',
    '获取待复习卡片列表失败',
  ) as unknown as Promise<Card[]>
}

async function fetchNextCard(deckId: number): Promise<Card | null> {
  return callApiWithFeedback(
    () => httpClient.get<Card | { message: string }>(`/next_card?deck_id=${deckId}`),
    '下一张卡片获取成功',
    '获取下一张卡片失败',
  ) as unknown as Promise<Card | null>
}

// 处理卡片复习反馈
async function reviewCard(cardId: number, feedback: number): Promise<any> {
  return callApiWithFeedback(
    () => httpClient.post<any>(`/cards/${cardId}/review`, { feedback }),
    '复习反馈处理成功',
    '处理复习反馈失败',
  ) as Promise<any>
}

// 搜索卡片
async function searchCards(deckId: number, keyword: string): Promise<Card[]> {
  return callApiWithFeedback(
    () => httpClient.get<Card[]>(`/cards/search?deck_id=${deckId}&keyword=${keyword}`),
    '卡片搜索成功',
    '卡片搜索失败',
  ) as unknown as Promise<Card[]>
}

// 安排管理API
// 创建安排
async function createArrangement(arrangementData: Omit<Arrangement, 'id'>): Promise<any> {
  return callApiWithFeedback(
    () => httpClient.post<any>('/arrangements', arrangementData),
    '安排创建成功',
    '创建安排失败',
  ) as Promise<any>
}

// 更新安排
async function updateArrangement(
  arrangementId: number,
  arrangementData: Partial<Arrangement>,
): Promise<any> {
  return callApiWithFeedback(
    () => httpClient.put<any>(`/arrangements/${arrangementId}`, arrangementData),
    '安排更新成功',
    '更新安排失败',
  ) as Promise<any>
}

// 删除安排
async function deleteArrangement(arrangementId: number): Promise<any> {
  return callApiWithFeedback(
    () => httpClient.delete<any>(`/arrangements/${arrangementId}`),
    '安排删除成功',
    '删除安排失败',
  ) as Promise<any>
}

// 获取卡组的安排
async function fetchArrangement(deckId: number): Promise<Arrangement> {
  return callApiWithFeedback(
    () => httpClient.get<Arrangement>(`/arrangements?deck_id=${deckId}`),
    '安排获取成功',
    '获取安排失败',
  ) as unknown as Promise<Arrangement>
}

// 导出API状态创建函数和API函数
export {
  createApiState,
  // 卡组管理
  createDeck,
  updateDeck,
  deleteDeck,
  fetchDecks,
  fetchDeckDetail,
  // 卡片管理
  fetchCards,
  addCard,
  updateCard,
  deleteCard,
  fetchReviewCards,
  reviewCard,
  searchCards,
  fetchNextCard,
  // 安排管理
  createArrangement,
  updateArrangement,
  deleteArrangement,
  fetchArrangement,
  type ApiState,
}
