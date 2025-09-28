// Tauri invoke 模块
import { invoke } from '@tauri-apps/api/core'
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
  apiCall: () => Promise<T>,
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
      data = response
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
  apiCall: () => Promise<T>,
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

    return response
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
async function createDeck(deckData: Omit<Deck, 'id'>): Promise<void> {
  return callApiWithFeedback(
    () => invoke('create_deck', { name: deckData.name }),
    '卡组创建成功',
    '创建卡组失败',
  ) as Promise<void>
}

interface ExtendedDeck extends Deck {
  arrangement: number
}

// 编辑卡组
async function updateDeck(deckId: number, deckData: Partial<ExtendedDeck>): Promise<void> {
  return callApiWithFeedback(
    () => invoke('update_deck', { 
      id: deckId, 
      name: deckData.name,
      forgetLine: deckData.forget_line,
      omega: deckData.omega,
      maxDelta: deckData.max_delta,
      arrangement: deckData.arrangement
    }),
    '卡组更新成功',
    '更新卡组失败',
  ) as Promise<void>
}

// 删除卡组
async function deleteDeck(deckId: number): Promise<void> {
  return callApiWithFeedback(
    () => invoke('delete_deck', { id: deckId }),
    '卡组删除成功',
    '删除卡组失败',
  ) as Promise<void>
}

// 获取所有卡组
async function fetchDecks(): Promise<Deck[]> {
  return callApiWithFeedback(
    () => invoke<Deck[]>('list_decks'),
    '卡组列表获取成功',
    '获取卡组列表失败',
  ) as unknown as Promise<Deck[]>
}

// 卡组详情
async function fetchDeckDetail(deckId: number): Promise<DeckDetail> {
  return callApiWithFeedback(
    () => invoke<DeckDetail>('get_deck_detail', { id: deckId }),
    '卡组详情获取成功',
    '获取卡组详情失败',
  ) as unknown as Promise<DeckDetail>
}

// 卡片管理API
// 获取卡组的所有卡片
async function fetchCards(deckId: number): Promise<Card[]> {
  return callApiWithFeedback(
    () => invoke<Card[]>('list_cards', { deckId }),
    '卡片列表获取成功',
    '获取卡片列表失败',
  ) as unknown as Promise<Card[]>
}

// 添加卡片
async function addCard(cardData: Omit<Card, 'id'>): Promise<void> {
  return callApiWithFeedback(
    () => invoke('create_card', { 
      deckId: cardData.deck_id, 
      front: cardData.front, 
      back: cardData.back 
    }),
    '卡片添加成功',
    '添加卡片失败',
  ) as Promise<void>
}

// 更新卡片
async function updateCard(cardId: number, cardData: Partial<Card>): Promise<void> {
  return callApiWithFeedback(
    () => invoke('update_card', { 
      id: cardId, 
      front: cardData.front, 
      back: cardData.back 
    }),
    '卡片更新成功',
    '更新卡片失败',
  ) as Promise<void>
}

// 删除卡片
async function deleteCard(cardId: number): Promise<void> {
  return callApiWithFeedback(
    () => invoke('delete_card', { id: cardId }),
    '卡片删除成功',
    '删除卡片失败',
  ) as Promise<void>
}

// 获取卡组的待复习卡片
async function fetchReviewCards(deckId: number): Promise<Card[]> {
  return callApiWithFeedback(
    () => invoke<Card[]>('list_review_cards', { deckId }),
    '待复习卡片列表获取成功',
    '获取待复习卡片列表失败',
  ) as unknown as Promise<Card[]>
}

async function fetchNextCard(deckId: number): Promise<Card | null> {
  return callApiWithFeedback(
    () => invoke<Card | null>('next_card', { deckId }),
    '下一张卡片获取成功',
    '获取下一张卡片失败',
  ) as unknown as Promise<Card | null>
}

// 处理卡片复习反馈
async function reviewCard(cardId: number, feedback: number): Promise<void> {
  return callApiWithFeedback(
    () => invoke('review_card', { id: cardId, feedback }),
    '复习反馈处理成功',
    '处理复习反馈失败',
  ) as Promise<void>
}

// 搜索卡片
async function searchCards(deckId: number, keyword: string): Promise<Card[]> {
  return callApiWithFeedback(
    () => invoke<Card[]>('search_cards', { deckId, keyword }),
    '卡片搜索成功',
    '卡片搜索失败',
  ) as unknown as Promise<Card[]>
}

// 安排管理API
// 创建安排
async function createArrangement(arrangementData: Omit<Arrangement, 'id'>): Promise<void> {
  return callApiWithFeedback(
    () => invoke('create_arrangement', { 
      deckId: arrangementData.deck_id, 
      count: arrangementData.count 
    }),
    '安排创建成功',
    '创建安排失败',
  ) as Promise<void>
}

// 更新安排
async function updateArrangement(
  arrangementId: number,
  arrangementData: Partial<Arrangement>,
): Promise<void> {
  return callApiWithFeedback(
    () => invoke('update_arrangement', { 
      id: arrangementId, 
      count: arrangementData.count 
    }),
    '安排更新成功',
    '更新安排失败',
  ) as Promise<void>
}

// 删除安排
async function deleteArrangement(arrangementId: number): Promise<void> {
  return callApiWithFeedback(
    () => invoke('delete_arrangement', { id: arrangementId }),
    '安排删除成功',
    '删除安排失败',
  ) as Promise<void>
}

// 获取卡组的安排
async function fetchArrangement(deckId: number): Promise<Arrangement> {
  return callApiWithFeedback(
    () => invoke<Arrangement>('list_arrangements', { deckId }),
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