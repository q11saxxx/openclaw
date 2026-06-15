<template>
  <pre><code :class="languageClass" ref="codeEl">{{ content }}</code></pre>
</template>

<script lang="ts" setup>
import { onMounted, ref, watch } from 'vue'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

const props = defineProps<{ content: string; language?: string }>()
const content = props.content || ''
const language = props.language || 'plaintext'
const codeEl = ref<HTMLElement | null>(null)
const languageClass = `language-${language}`

onMounted(() => {
  if (codeEl.value) hljs.highlightElement(codeEl.value)
})

watch(() => props.content, () => {
  if (codeEl.value) hljs.highlightElement(codeEl.value)
})
</script>
