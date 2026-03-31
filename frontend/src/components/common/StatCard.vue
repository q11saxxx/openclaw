<!-- 本文件说明：仪表盘统计卡片组件，后续用于展示风险总数和项目数。 -->
<template>
  <div class="bg-white rounded-2xl shadow p-4">
    <div class="text-sm text-slate-500">{{ label }}</div>
    <div class="text-3xl font-bold mt-2">{{ value }}</div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ label: string; value: string | number }>()
</script>
