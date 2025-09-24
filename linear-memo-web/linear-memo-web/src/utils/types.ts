interface Deck {
  id: number
  name: string
  forget_line: number
  omega: number
  max_delta: number
}

interface DeckDetail extends Deck {
  cards_count: number
  new_count: number
  overtime_count: number
  review_count: number
  remembered_count: number
}

interface Card {
  id: number
  deck_id: number
  front: string
  back: string
  last_review?: Date
  stability?: number
  review_interval?: number
  status?: boolean
}

interface Arrangement {
  id: number
  deck_id: number
  count: number
}

interface History {
  id: number
  card_id: number
  review_date: Date
  stability: number
}

export type { Deck, DeckDetail, Card, Arrangement, History }
