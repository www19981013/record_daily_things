<script setup>
import { computed } from 'vue'

const props = defineProps({ entries: { type: Array, default: () => [] } })
const emit = defineEmits(['delete'])

const grouped = computed(() => {
  const map = new Map()
  for (const e of props.entries) {
    const d = new Date(e.created_at).toLocaleDateString('zh-CN')
    if (!map.has(d)) map.set(d, [])
    map.get(d).push(e)
  }
  return [...map.entries()]
})
</script>

<template>
  <div v-if="grouped.length === 0" class="empty">还没有记录，写下今天完成的第一件事吧。</div>
  <section v-for="[day, items] in grouped" :key="day" class="day-group">
    <h3>{{ day }}</h3>
    <ul>
      <li v-for="e in items" :key="e.id">
        <span>{{ e.content }}</span>
        <button class="del" @click="emit('delete', e.id)">×</button>
      </li>
    </ul>
  </section>
</template>
