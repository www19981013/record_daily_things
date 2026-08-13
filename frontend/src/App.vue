<script setup>
import { onMounted, ref } from 'vue'
import { listEntries, createEntry, deleteEntry } from './api'
import EntryInput from './components/EntryInput.vue'
import EntryList from './components/EntryList.vue'
import SummaryView from './components/SummaryView.vue'

const entries = ref([])
const tab = ref('record')

async function refresh() {
  entries.value = await listEntries()
}

async function onCreate(content) {
  await createEntry(content)
  await refresh()
}

async function onDelete(id) {
  await deleteEntry(id)
  await refresh()
}

onMounted(refresh)
</script>

<template>
  <div class="app">
    <header class="header">
      <div class="brand">
        <h1>精力恢复记事本</h1>
        <p class="tagline">只记录完成的事，不计划，不评价</p>
      </div>
      <nav class="tabs">
        <button :class="{ active: tab === 'record' }" @click="tab = 'record'">记录</button>
        <button :class="{ active: tab === 'summary' }" @click="tab = 'summary'">小结</button>
      </nav>
    </header>
    <main>
      <template v-if="tab === 'record'">
        <EntryInput @created="onCreate" />
        <EntryList :entries="entries" @delete="onDelete" />
      </template>
      <SummaryView v-else />
    </main>
  </div>
</template>

<style scoped>
.app {
  max-width: 680px;
  margin: 0 auto;
  padding: 28px 20px 72px;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 8px 0 28px;
}

.brand h1 {
  font-size: 22px;
  font-weight: 600;
  margin: 0;
  letter-spacing: 0.5px;
}

.tagline {
  margin: 4px 0 0;
  font-size: 13px;
  color: var(--text-secondary);
}

.tabs {
  display: flex;
  gap: 4px;
  background: #eae4d9;
  border-radius: 999px;
  padding: 4px;
  flex-shrink: 0;
}

.tabs button {
  padding: 8px 20px;
  border-radius: 999px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 14px;
  transition: background 0.15s, color 0.15s;
}

.tabs button.active {
  background: #fff;
  color: var(--text);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

@media (max-width: 480px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 14px;
  }
}
</style>
