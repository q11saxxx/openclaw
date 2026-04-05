<template>
  <el-tag :type="tagType">{{ label }}</el-tag>
</template>

<script lang="ts" setup>
import { computed } from 'vue'
import { toRef } from 'vue'

const props = defineProps<{ level?: string }>()
const level = toRef(props, 'level')

const mapping: Record<string, { label: string; tagType: string }> = {
  critical: { label: '严重', tagType: 'danger' },
  high: { label: '高危', tagType: 'warning' },
  medium: { label: '中危', tagType: 'info' },
  low: { label: '低危', tagType: 'success' }
}

const label = computed(() => mapping[(level.value || '').toLowerCase()]?.label || '未知')
const tagType = computed(() => mapping[(level.value || '').toLowerCase()]?.tagType || 'info')
</script>
