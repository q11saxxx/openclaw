<template>
  <div>
    <el-steps :active="active">
      <el-step title="解析中" />
      <el-step title="静态扫描" />
      <el-step title="语义审计" />
      <el-step title="来源分析" />
      <el-step title="决策评估" />
      <el-step title="报告生成" />
    </el-steps>
    <div style="margin-top:12px">
      <pre style="background:#111;color:#0f0;padding:8px;height:160px;overflow:auto">{{ logs }}</pre>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue'
const props = defineProps<{ stage?: number; logs?: string }>()
const active = computed(() => (props.stage || 0) + 1)
const logs = props.logs || ''
</script>
