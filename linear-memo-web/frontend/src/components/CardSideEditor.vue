<script setup lang="ts">
import { queryDict } from '@/utils/api'
import { ref, onMounted, watch } from 'vue'
interface Props {
  index: number
  front: string
  back: string
}
const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'save', index: number, front: string, back: string): void
  (e: 'cancel'): void
}>()
// 编辑器状态
const frontRaw = ref(props.front || '')
const backRaw = ref(props.back || '')

// 保存
const save = () => {
  emit('save', props.index, frontRaw.value, backRaw.value)
}
// 取消
const cancel = () => {
  emit('cancel')
}
// 查词
const query = async () => {
  if (!frontRaw.value || frontRaw.value.trim() === '') {
    frontRaw.value = '请输入单词'
    return
  }
  const { front, back } = await queryDict(frontRaw.value)
  frontRaw.value = front
  backRaw.value = back
}
</script>
<template>
  <div class="card-side-editor">
    <div class="editor-grid">
      <!-- 正面编辑器 -->
      <div class="editor-section">
        <span>正面原始文本:</span>
        <textarea
          id="f"
          v-model="frontRaw"
          class="editor-wrapper raw-editor"
          placeholder="输入正面内容..."
        >
        </textarea>
      </div>
      <div class="editor-section">
        <span>正面预览:</span>
        <div class="editor-wrapper html-preview" v-html="frontRaw"></div>
      </div>

      <!-- 反面编辑器 -->
      <div class="editor-section">
        <span>反面原始文本:</span>
        <textarea
          id="b"
          v-model="backRaw"
          class="editor-wrapper raw-editor"
          placeholder="输入反面内容..."
        >
        </textarea>
      </div>
      <div class="editor-section">
        <span>反面预览:</span>
        <div class="editor-wrapper html-preview" v-html="backRaw"></div>
      </div>
    </div>

    <div style="display: flex">
      <div class="editor-addons">
        <button class="query" @click="query">简单查词</button>
      </div>
      <div class="editor-actions">
        <button class="save-btn" @click="save">暂存</button>
        <button class="cancel-btn" @click="cancel">取消</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.editor-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.raw-editor {
  width: 100%;
  font-family: monospace;
  resize: vertical;
  overflow: auto;
}

.html-preview {
  width: 100%;
  overflow: auto;
}

.card-side-editor {
  padding: 1rem;
  background-color: var(--color-background);
  border-radius: 6px;
  color: var(--color-text);
}

.editor-section {
  margin-bottom: 1rem;
}

.editor-section label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: var(--color-text);
}

.editor-wrapper {
  border: 1px solid var(--color-border);
  border-radius: 4px;
  /* overflow: hidden; */
  /* min-height: 200px; */
  height: 200px;
}

.editor-addons {
  display: flex;
  justify-content: flex-start;
  gap: 0.5rem;
  margin-top: 1rem;
  margin-right: auto;
}

.editor-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1rem;
}

.query .save-btn,
.cancel-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.query {
  background-color: var(--color-button-secondary);
  color: white;
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
