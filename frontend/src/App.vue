<script setup>
import { onMounted, ref } from 'vue'
import { listEntries, createEntry, deleteEntry } from './api'
import EntryInput from './components/EntryInput.vue'
import EntryList from './components/EntryList.vue'

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
    <header>
      <h1>精力恢复记事本</h1>
      <nav>
        <button :class="{ active: tab === 'record' }" @click="tab = 'record'">记录</button>
        <button :class="{ active: tab === 'summary' }" @click="tab = 'summary'">小结</button>
      </nav>
    </header>
    <main v-if="tab === 'record'">
      <EntryInput @created="onCreate" />
      <EntryList :entries="entries" @delete="onDelete" />
    </main>
  </div>
</template>
