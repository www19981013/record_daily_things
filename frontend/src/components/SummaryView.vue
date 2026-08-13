<script setup>
import { onMounted, ref } from 'vue'
import { listSummaries, generateSummary } from '../api'

const summaries = ref([])
const error = ref('')
const loading = ref('')

async function refresh() {
  try {
    summaries.value = await listSummaries()
  } catch (e) {
    error.value = '加载小结失败，请稍后重试。'
  }
}

async function onGenerate(periodType) {
  if (loading.value) return
  loading.value = periodType
  error.value = ''
  try {
    await generateSummary(periodType)
    await refresh()
  } catch (e) {
    error.value = '小结生成失败，请稍后重试。'
  } finally {
    loading.value = ''
  }
}

onMounted(refresh)
</script>

<template>
  <div class="summary-view">
    <div class="actions">
      <button :disabled="!!loading" @click="onGenerate('weekly')">
        {{ loading === 'weekly' ? '生成中…' : '生成本周小结' }}
      </button>
      <button :disabled="!!loading" @click="onGenerate('monthly')">
        {{ loading === 'monthly' ? '生成中…' : '生成本月小结' }}
      </button>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="!error && summaries.length === 0" class="empty">还没有小结，点击上方按钮生成。</p>
    <article v-for="s in summaries" :key="s.id" class="summary-card">
      <h3>
        {{ s.period_type === 'weekly' ? '本周小结' : '本月小结' }}
        <small>{{ new Date(s.period_start).toLocaleDateString('zh-CN') }}</small>
      </h3>
      <div class="content">{{ s.content }}</div>
    </article>
  </div>
</template>

<style scoped>
.actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.actions button {
  flex: 1;
  background: var(--card);
  color: var(--text);
  border: 1px solid var(--border);
  padding: 11px 0;
  border-radius: 999px;
  font-size: 14px;
  box-shadow: var(--shadow);
  transition: background 0.15s, border-color 0.15s, color 0.15s;
}

.actions button:hover:not(:disabled) {
  border-color: var(--primary);
  color: var(--primary-dark);
  background: #f2f7f2;
}

.actions button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  background: #f9ece8;
  color: var(--danger);
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 14px;
  margin: 0 0 16px;
}

.empty {
  text-align: center;
  color: var(--text-secondary);
  padding: 48px 0;
  font-size: 14px;
}

.summary-card {
  background: var(--card);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 20px 22px;
  margin-bottom: 16px;
}

.summary-card h3 {
  margin: 0 0 12px;
  font-size: 16px;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}

.summary-card h3 small {
  font-size: 12px;
  font-weight: 400;
  color: var(--text-faint);
}

.content {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 15px;
  line-height: 1.7;
  color: var(--text);
  border-top: 1px solid var(--border);
  padding-top: 14px;
}
</style>
