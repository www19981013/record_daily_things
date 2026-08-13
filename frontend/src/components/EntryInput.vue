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
    <textarea
      v-model="content"
      placeholder="今天完成了什么？"
      rows="3"
      @keydown.enter.exact.prevent="submit"
    ></textarea>
    <button type="submit" :disabled="!content.trim()">记录</button>
  </form>
</template>
