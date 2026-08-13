<script setup>
import { ref } from 'vue'

const emit = defineEmits(['created'])
const content = ref('')

async function submit() {
  if (!content.value.trim()) return
  emit('created', content.value.trim())
  content.value = ''
}
</script>

<template>
  <form class="entry-input" @submit.prevent="submit">
    <label class="label" for="entry-content">今天完成了什么？</label>
    <textarea
      id="entry-content"
      v-model="content"
      placeholder="例：读完了《XX》第三章、跑了 5 公里、整理好了季度数据……"
      rows="4"
      maxlength="2000"
      @keydown.enter.exact.prevent="submit"
    ></textarea>
    <div class="footer">
      <span class="count">{{ content.length }}/2000</span>
      <button type="submit" :disabled="!content.trim()">记录</button>
    </div>
  </form>
</template>

<style scoped>
.entry-input {
  background: var(--card);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 20px 20px 16px;
}

.label {
  display: block;
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
}

textarea {
  width: 100%;
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 15px;
  line-height: 1.6;
  resize: vertical;
  min-height: 96px;
  color: var(--text);
  background: #fdfcfa;
  transition: border-color 0.15s, box-shadow 0.15s;
}

textarea:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(107, 143, 113, 0.15);
}

.footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
}

.count {
  font-size: 12px;
  color: var(--text-faint);
}

.footer button {
  background: var(--primary);
  color: #fff;
  padding: 9px 26px;
  border-radius: 999px;
  font-size: 14px;
  transition: background 0.15s;
}

.footer button:hover:not(:disabled) {
  background: var(--primary-dark);
}

.footer button:disabled {
  background: #d8d2c6;
  cursor: not-allowed;
}
</style>
