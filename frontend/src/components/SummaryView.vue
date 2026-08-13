<script setup>
import { onMounted, ref } from 'vue'
import { listSummaries, generateSummary } from '../api'

const summaries = ref([])
const error = ref('')

async function refresh() {
  summaries.value = await listSummaries()
}

async function onGenerate(periodType) {
  error.value = ''
  try {
    await generateSummary(periodType)
    await refresh()
  } catch (e) {
    error.value = '小结生成失败，请稍后重试。'
  }
}

onMounted(refresh)
</script>

<template>
  <div class="summary-view">
    <div class="actions">
      <button @click="onGenerate('weekly')">生成本周小结</button>
      <button @click="onGenerate('monthly')">生成本月小结</button>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
    <article v-for="s in summaries" :key="s.id" class="summary-card">
      <h3>
        {{ s.period_type === 'weekly' ? '本周小结' : '本月小结' }}
        <small>{{ new Date(s.period_start).toLocaleDateString('zh-CN') }}</small>
      </h3>
      <pre class="content">{{ s.content }}</pre>
    </article>
  </div>
</template>
