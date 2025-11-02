// 卡片类型
export interface Card {
  id: number
  deck_id: number
  front: string
  back: string
  last_review?: string | null
  stability?: number
  review_interval?: number
  status?: boolean
  user_id?: number
}

// 卡组类型
export interface Deck {
  id: number
  name: string
  user_id?: number
  forget_line: number
  omega: number
  max_delta: number
}

// 安排类型
export interface Arrangement {
  id: number
  deck_id: number
  count: number
  created_at: string
}

// 卡组详情类型
export interface DeckDetail extends Deck {
  cards_count: number
  new_count: number
  review_count: number
  overtime_count: number
  remembered_count: number
}

// 下一张卡片信息类型
export interface NextCardInfo {
  card: Card | null
  deck_id: number
  finished: boolean
  overtime_count: number
}

// 用户类型
export interface User {
  id: number
  username: string
  email: string | null
  created_at: string
}

// 注册信息类型
export interface AccessUserInfo {
  access_token: string
  refresh_token: string
  message: string
  user: User
}
