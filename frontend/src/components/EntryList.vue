<script setup>
import { computed } from 'vue'

const props = defineProps({ entries: { type: Array, default: () => [] } })
const emit = defineEmits(['delete'])

const WEEKDAYS = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

const grouped = computed(() => {
  const map = new Map()
  for (const e of props.entries) {
    const dt = new Date(e.created_at)
    const key = dt.toDateString()
    if (!map.has(key)) {
      const label = `${dt.getMonth() + 1}月${dt.getDate()}日 ${WEEKDAYS[dt.getDay()]}`
      map.set(key, { label, items: [] })
    }
    map.get(key).items.push(e)
  }
  return [...map.values()]
})
</script>

<template>
  <div v-if="grouped.length === 0" class="empty">
    <p class="empty-title">还没有记录</p>
    <p class="empty-sub">写下今天完成的第一件事吧</p>
  </div>
  <section v-for="g in grouped" :key="g.label" class="day-group">
    <h3 class="day-title">{{ g.label }}<span class="count">{{ g.items.length }} 件</span></h3>
    <ul class="items">
      <li v-for="e in g.items" :key="e.id" class="item">
        <span class="dot"></span>
        <span class="content">{{ e.content }}</span>
        <button class="del" @click="emit('delete', e.id)" title="删除">×</button>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.empty {
  text-align: center;
  padding: 64px 0;
}

.empty-title {
  font-size: 17px;
  margin: 0 0 6px;
  color: var(--text);
}

.empty-sub {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.day-group {
  margin-top: 26px;
}

.day-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 0 0 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.day-title .count {
  font-size: 12px;
  font-weight: 400;
  color: var(--text-faint);
}

.items {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: var(--card);
  border-radius: 12px;
  padding: 14px 16px;
  box-shadow: var(--shadow);
  transition: box-shadow 0.15s;
}

.item:hover {
  box-shadow: var(--shadow-hover);
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary);
  flex-shrink: 0;
  margin-top: 8px;
}

.content {
  flex: 1;
  font-size: 15px;
  white-space: pre-wrap;
  word-break: break-word;
}

.del {
  flex-shrink: 0;
  background: transparent;
  color: var(--text-faint);
  font-size: 18px;
  line-height: 1;
  padding: 2px 6px;
  border-radius: 6px;
  opacity: 0;
  transition: opacity 0.15s, color 0.15s;
}

.item:hover .del {
  opacity: 1;
}

.del:hover {
  color: var(--danger);
}

@media (hover: none) {
  .del {
    opacity: 1;
  }
}
</style>
