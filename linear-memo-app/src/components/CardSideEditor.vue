<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
// Toast UI Editor
import Editor from '@toast-ui/editor'
import '@toast-ui/editor/dist/toastui-editor.css'

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

// 编辑器实例
let frontEditor: Editor | null = null
let backEditor: Editor | null = null

// 保存
const save = () => {
  const frontContent = frontEditor?.getHTML() || ''
  const backContent = backEditor?.getHTML() || ''
  emit('save', props.index, frontContent, backContent)
}

// 取消
const cancel = () => {
  emit('cancel')
}

// 初始化编辑器
onMounted(() => {
  // 初始化正面编辑器
  const frontEl = document.getElementById('front-editor')
  if (frontEl) {
    frontEditor = new Editor({
      el: frontEl,
      height: '200px',
      initialEditType: 'wysiwyg',
      initialValue: props.front || '',
      toolbarItems: [
        ['heading', 'bold', 'italic', 'strike'],
        ['hr', 'quote'],
        ['ul', 'ol', 'task', 'indent', 'outdent'],
        ['table', 'link'],
        ['code', 'codeblock'],
      ],
    })
  }

  // 初始化反面编辑器
  const backEl = document.getElementById('back-editor')
  if (backEl) {
    backEditor = new Editor({
      el: backEl,
      height: '200px',
      initialEditType: 'wysiwyg',
      initialValue: props.back || '',
      toolbarItems: [
        ['heading', 'bold', 'italic', 'strike'],
        ['hr', 'quote'],
        ['ul', 'ol', 'task', 'indent', 'outdent'],
        ['table', 'link'],
        ['code', 'codeblock'],
      ],
    })
  }
})
</script>

<template>
  <div class="card-side-editor">
    <div class="editor-section">
      <label>正面内容:</label>
      <div id="front-editor" class="editor-wrapper"></div>
    </div>

    <div class="editor-section">
      <label>反面内容:</label>
      <div id="back-editor" class="editor-wrapper"></div>
    </div>

    <div class="editor-actions">
      <button class="save-btn" @click="save">保存</button>
      <button class="cancel-btn" @click="cancel">取消</button>
    </div>
  </div>
</template>

<style scoped>
.card-side-editor {
  padding: 1rem;
  background-color: var(--card-bg);
  border-radius: 6px;
  color: var(--text-color);
}

.editor-section label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: var(--text-color);
}

.editor-wrapper {
  border: 1px solid var(--input-border);
  border-radius: 4px;
  overflow: hidden;
  background-color: var(--input-bg);
}

.save-btn,
.cancel-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.save-btn {
  background-color: var(--button-success);
  color: white;
}

.save-btn:hover {
  background-color: var(--button-success-hover);
}

.cancel-btn {
  background-color: var(--button-warning);
  color: white;
}

.cancel-btn:hover {
  background-color: var(--button-warning-hover);
}
</style>
