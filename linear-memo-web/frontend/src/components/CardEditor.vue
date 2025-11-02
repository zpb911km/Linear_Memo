<script setup lang="ts">
import { ref, watch, type PropType } from 'vue'
import CardSideEditor from './CardSideEditor.vue'
import type { Card, Deck } from '@/utils/types'
import { searchCards } from '@/utils/api'

const props = defineProps({
  cards: {
    type: Array as PropType<Card[]>,
    required: true,
  },
  deck: {
    type: Object as PropType<Deck>,
    required: true,
  },
  visible: {
    type: Boolean,
    required: true,
  },
})
const emit = defineEmits<{
  (e: 'update', cards: Card[]): void
  (e: 'add', card: Card[]): void
  (e: 'delete', card: Card[]): void
  (e: 'cancel'): void
  (e: 'update:visible', visible: boolean): void
}>()

// 创建本地副本以进行编辑
const localCards = ref<Card[]>(JSON.parse(JSON.stringify(props.cards)))
const editedCards = ref<Card[]>([])
const deletedCards = ref<Card[]>([])
const addedCards = ref<Card[]>([])
const editingCardIndex = ref<number | null>(null)
const keyword = ref('')

// watch(keyword, () => {
//   filterCards()
// })

// 过滤卡片
const filterCards = () => {
  searchCards(props.deck.id, keyword.value).then((res) => {
    localCards.value = (res as unknown as Card[]) || []
  })
}

// 添加新卡片
const addCard = () => {
  const newCard: Card = {
    id: -1,
    deck_id: props.deck.id,
    front: '',
    back: '',
  }
  localCards.value.push(newCard)
  addedCards.value.push(newCard)
  editingCardIndex.value = localCards.value.length - 1
}

// 删除卡片
const deleteCard = (index: number) => {
  deletedCards.value.push(localCards.value[index])
  localCards.value.splice(index, 1)
  if (editingCardIndex.value === index) {
    editingCardIndex.value = null
  } else if (editingCardIndex.value !== null && editingCardIndex.value > index) {
    editingCardIndex.value--
  }
}

// 保存卡片
const saveCard = (index: number, front: string, back: string) => {
  localCards.value[index].front = front
  localCards.value[index].back = back
  editedCards.value.push(localCards.value[index])
  editingCardIndex.value = null
}

// 取消编辑
const cancelEdit = () => {
  editingCardIndex.value = null
}

// 保存所有卡片
const saveAllCards = () => {
  if (addedCards.value.length > 0) {
    // console.log('save added cards', addedCards.value)
    emit('add', addedCards.value)
  }
  for (const card of editedCards.value) {
    if (card.id === -1) {
      editedCards.value.splice(editedCards.value.indexOf(card), 1)
    }
  }
  if (editedCards.value.length > 0) {
    // console.log('save edited cards', editedCards.value)
    emit('update', editedCards.value)
  }
  if (deletedCards.value.length > 0) {
    // console.log('delete cards', deletedCards.value)
    emit('delete', deletedCards.value)
  }
  localCards.value = JSON.parse(JSON.stringify(props.cards))
  addedCards.value = []
  editedCards.value = []
  deletedCards.value = []
  editingCardIndex.value = null
  emit('update:visible', false)
}

// 取消编辑所有卡片
const cancelAllCards = () => {
  localCards.value = JSON.parse(JSON.stringify(props.cards))
  editingCardIndex.value = null
  emit('cancel')
  emit('update:visible', false)
}

// 关闭弹窗
const closeDialog = () => {
  emit('cancel')
}
</script>

<template>
  <div v-if="visible" class="modal-overlay" @click="closeDialog">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>{{ deck.name }} - 卡片编辑</h2>
        <button class="close-btn" @click="closeDialog">×</button>
      </div>
      <div class="search-bar">
        <input type="text" placeholder="搜索..." v-model="keyword" />
        <button @click="filterCards">搜索</button>
      </div>
      <div class="modal-body">
        <div class="card-list">
          <p style="width: 100%; text-align: center" v-if="localCards.length === 0">
            ...没有找到卡片...
          </p>
          <div
            v-for="(card, index) in localCards"
            :key="card.id"
            class="card-item"
            :class="{ editing: editingCardIndex === index }"
          >
            <div v-if="editingCardIndex === index" class="card-edit-mode">
              <CardSideEditor
                :index="index"
                :front="card.front"
                :back="card.back"
                @save="saveCard"
                @cancel="cancelEdit"
              />
            </div>
            <div v-else class="card-view-mode">
              <div class="card-preview">
                <div class="card-front-preview" v-html="card.front || '(空白)'"></div>
                <div class="card-back-preview" v-html="card.back || '(空白)'"></div>
              </div>
              <div class="card-actions">
                <button class="edit-btn" @click="editingCardIndex = index">编辑</button>
                <button class="delete-btn" @click="deleteCard(index)">删除</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="add-card-btn" @click="addCard">添加卡片</button>
        <!-- <button class="add-card-btn" @click="batchEditCard">批量导出</button>
        <button class="add-card-btn" @click="batchAddCard">批量导入</button> -->
        <!-- TODO: 批量导出、批量导入功能 -->
        <div class="save-cancel-actions">
          <button class="save-btn" @click="saveAllCards">保存所有</button>
          <button class="cancel-btn" @click="cancelAllCards">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
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
  padding: 0.5rem 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h2 {
  margin: 0;
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
  padding: 0.5rem 1.5rem;
}

.search-bar {
  margin: 5% 5% 0 5%;
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
  width: 90%;
}

.search-bar input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background-color: var(--color-background);
  color: var(--color-text);
}

.search-bar button {
  padding: 0.5rem 1rem;
  background-color: var(--color-button-primary);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 0.5rem;
}

.search-bar button:hover {
  background-color: var(--color-button-primary-hover);
}

.card-list {
  margin: 0.5rem 0;
}

.card-item {
  margin-bottom: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  overflow: hidden;
  background-color: var(--color-card-background);
}

.card-item.editing {
  border-color: var(--color-button-primary);
}

.card-view-mode {
  padding: 0.5rem;
  background-color: var(--color-card-background);
}

.card-preview {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.card-front-preview,
.card-back-preview {
  padding: 0.5rem;
  border: 1px dashed var(--color-border);
  border-radius: 4px;
  color: var(--color-text);
  height: 200px;
  overflow-y: auto;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1.5rem;
  border-top: 1px solid var(--color-border);
}

.edit-btn,
.delete-btn {
  padding: 0.25rem 0.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
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

.add-card-btn {
  padding: 0.5rem 0.5rem;
  background-color: var(--color-button-primary);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
}

.add-card-btn:hover {
  background-color: var(--color-button-primary-hover);
}

.save-cancel-actions {
  display: flex;
  gap: 0.5rem;
}

.save-btn,
.cancel-btn {
  padding: 0.5rem 0.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
}

.save-btn {
  background-color: var(--color-button-primary);
  color: white;
}

.save-btn:hover {
  background-color: var(--color-button-primary-hover);
}

.cancel-btn {
  background-color: var(--color-button-secondary);
  color: white;
}

.cancel-btn:hover {
  background-color: var(--color-button-secondary-hover);
}
</style>
