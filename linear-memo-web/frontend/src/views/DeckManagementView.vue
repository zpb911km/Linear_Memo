<script setup lang="ts">
import { ref, onMounted } from 'vue'
import CardEditor from '../components/CardEditor.vue'
import {
  fetchDecks,
  createDeck,
  updateDeck,
  deleteDeck,
  fetchCards,
  addCard,
  updateCard,
  deleteCard,
  fetchArrangement,
} from '../utils/api'
import type { Card, Deck } from '@/utils/types'

// 卡组列表
const decks = ref<Deck[]>([])

// 弹窗状态
const showCardEditor = ref(false)
const editingDeck = ref<Deck | null>(null)
const editingDeckName = ref('')
const editingDeckFogetLine = ref(0)
const editingDeckOmega = ref(0)
const editingDeckMaxDelta = ref(0)
const editingDeckArrangement = ref(0)
const showDeckEditor = ref(false)

// 卡片列表
const cards = ref<Card[]>([])

// 获取所有卡组
const loadDecks = async () => {
  const response = await fetchDecks()
  if (response && response) {
    decks.value = response as unknown as Deck[]
  }
}

// 获取卡组的卡片
const loadCardsForDeck = async (deckId: number) => {
  const response = await fetchCards(deckId)
  if (response && response) {
    cards.value = response as unknown as Card[]
  }
}

// 添加新卡组
const addNewDeck = async () => {
  const deckName = prompt('请输入新卡组的名称:')
  if (deckName) {
    const response = await createDeck({
      name: deckName,
      forget_line: 0.4,
      omega: 0.9,
      max_delta: 365,
    })
    if (response && response) {
      await loadDecks()
    }
  }
}

// 删除卡组
const removeDeck = async (deckId: number) => {
  if (confirm('确定要删除这个卡组吗？此操作不可恢复。')) {
    const response = await deleteDeck(deckId)
    if (response && response) {
      // 重新加载卡组列表
      await loadDecks()
    }
  }
}

// 编辑卡组的卡片
const editDeckCards = async (deck: Deck) => {
  editingDeck.value = deck
  editingDeckName.value = deck.name

  // 加载该卡组的卡片
  await loadCardsForDeck(deck.id)
  showCardEditor.value = true
}

// 编辑卡组
const editDeck = async (deck: Deck) => {
  editingDeck.value = deck
  editingDeckName.value = deck.name
  editingDeckFogetLine.value = deck.forget_line
  editingDeckOmega.value = deck.omega
  editingDeckMaxDelta.value = deck.max_delta
  const arrangement = await fetchArrangement(deck.id)
  editingDeckArrangement.value = arrangement.count
  showDeckEditor.value = true
}

// 保存卡组
const saveDeck = async () => {
  if (editingDeck) {
    if (!editingDeck.value?.id) {
      alert('出错了')
      window.location.reload()
      return
    }
    const response = await updateDeck(editingDeck.value.id, {
      name: editingDeckName.value,
      forget_line: editingDeckFogetLine.value,
      omega: editingDeckOmega.value,
      max_delta: editingDeckMaxDelta.value,
      arrangement: editingDeckArrangement.value,
    })
    if (response && response) {
      // 重新加载卡组列表
      await loadDecks()
      showDeckEditor.value = false
    }
  }
}

const addCards = async (newCards: Card[]) => {
  if (editingDeck.value) {
    const deckId = editingDeck.value.id
    for (const card of newCards) {
      await addCard({
        deck_id: deckId,
        front: card.front,
        back: card.back,
      })
    }
    await loadCardsForDeck(deckId)
  }
  closeCardEditor()
}

const removeCards = async (cards: Card[]) => {
  if (editingDeck.value) {
    const deckId = editingDeck.value.id
    for (const card of cards) {
      await deleteCard(card.id)
    }
    await loadCardsForDeck(deckId)
  }
  closeCardEditor()
}

const updateCards = async (updatedCards: Card[]) => {
  if (editingDeck.value) {
    const deckId = editingDeck.value.id
    for (const card of updatedCards) {
      await updateCard(card.id, {
        front: card.front,
        back: card.back,
      })
    }
    await loadCardsForDeck(deckId)
  }
  closeCardEditor()
}

// 关闭卡片编辑器
const closeCardEditor = () => {
  showCardEditor.value = false
  editingDeck.value = null
  editingDeckName.value = ''
  cards.value = []
}

// 组件挂载时加载数据
onMounted(() => {
  loadDecks()
})
</script>

<template>
  <div class="deck-management">
    <h1>卡组管理</h1>

    <div class="deck-list">
      <div v-for="deck in decks" :key="deck.id" class="deck-item">
        <h3>{{ deck.name }}</h3>
        <div class="deck-actions">
          <button class="edit-details-btn" @click="editDeck(deck)">编辑卡组</button>
          <button class="edit-btn" @click="editDeckCards(deck)">编辑卡片</button>
          <button class="delete-btn" @click="removeDeck(deck.id)">删除</button>
        </div>
      </div>
    </div>

    <button class="add-deck-btn" @click="addNewDeck">添加新卡组</button>

    <!-- 卡片编辑器弹窗 -->
    <div v-if="editingDeck && showCardEditor" class="modal-overlay" @click="closeCardEditor">
      <div class="modal-content" @click.stop>
        <div class="modal-body">
          <CardEditor
            :cards="cards"
            :deck="editingDeck"
            :visible="showCardEditor"
            @add="addCards"
            @update="updateCards"
            @delete="removeCards"
            @cancel="closeCardEditor"
            @close="closeCardEditor"
          />
        </div>
      </div>
    </div>
    <!-- 卡组编辑器弹窗 -->
    <div v-if="showDeckEditor" class="modal-overlay" @click="showDeckEditor = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ editingDeck ? editingDeck.name : '' }} - 编辑卡组</h2>
          <button class="close-btn" @click="showDeckEditor = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label for="deck-name-input">卡组名称</label>
            <input
              type="text"
              id="deck-name-input"
              v-model="editingDeckName"
              class="form-control"
            />
          </div>
          <div class="form-group">
            <label for="arrangement-input">安排数量</label>
            <input
              type="number"
              id="arrangement-input"
              v-model="editingDeckArrangement"
              class="form-control"
            />
          </div>
          <div class="form-group">
            <label for="forget-line-input">遗忘阈值</label>
            <input
              type="number"
              id="forget-line-input"
              v-model="editingDeckFogetLine"
              class="form-control"
            />
          </div>
          <div class="form-group">
            <label for="omega-input">反馈置信度</label>
            <input type="number" id="omega-input" v-model="editingDeckOmega" class="form-control" />
          </div>
          <div class="form-group">
            <label for="max-delta-input">永久记忆阈值</label>
            <input
              type="number"
              id="max-delta-input"
              v-model="editingDeckMaxDelta"
              class="form-control"
            />
          </div>
        </div>
        <div class="modal-footer">
          <button class="save-btn" @click="saveDeck">保存</button>
          <button class="cancel-btn" @click="showDeckEditor = false">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.deck-management {
  padding: 2rem;
  background-color: var(--color-background);
  color: var(--color-text);
}

.deck-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}

.deck-item {
  padding: 1.5rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background-color: var(--color-card-background);
  box-shadow: 0 2px 4px var(--color-card-shadow);
}

.deck-item h3 {
  margin-top: 0;
  margin-bottom: 1rem;
}

.deck-actions {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  margin-top: 1rem;
}

.edit-details-btn,
.edit-name-btn,
.edit-btn,
.delete-btn {
  padding: 0.25rem 0.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.edit-details-btn,
.edit-name-btn {
  background-color: var(--color-button-primary);
  color: white;
}

.edit-details-btn:hover,
.edit-name-btn:hover {
  background-color: var(--color-button-primary-hover);
}

.edit-btn {
  background-color: var(--color-button-secondary);
  color: white;
}

.edit-btn:hover {
  background-color: var(--color-button-secondary-hover);
}

.delete-btn {
  background-color: var(--color-button-danger);
  color: white;
}

.delete-btn:hover {
  background-color: var(--color-button-danger-hover);
}

.add-deck-btn {
  padding: 0.5rem 1rem;
  background-color: var(--color-button-primary);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
}

.add-deck-btn:hover {
  background-color: var(--color-button-primary-hover);
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: var(--color-card-background);
  border-radius: 8px;
  box-shadow: 0 4px 12px var(--color-card-shadow);
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--color-border);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.deck-name-input {
  font-size: 1.2rem;
  font-weight: bold;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  padding: 0.5rem;
  flex: 1;
  margin-right: 1rem;
  background-color: var(--color-background);
  color: var(--color-text);
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--color-text-secondary);
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: var(--color-text);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 1.5rem;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--color-text);
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: var(--color-text);
}

.form-control {
  width: 100%;
  padding: 0.5rem;
  font-size: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background-color: var(--color-background);
  color: var(--color-text);
}

.modal-footer {
  display: flex;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--color-border);
}

.save-btn,
.cancel-btn {
  padding: 0.5rem 1rem;
  background-color: var(--color-button-primary);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.save-btn:hover {
  background-color: var(--color-button-primary-hover);
}

.cancel-btn {
  background-color: var(--color-button-danger);
}

.cancel-btn:hover {
  background-color: var(--color-button-danger-hover);
}
</style>
