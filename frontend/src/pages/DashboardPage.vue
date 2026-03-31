<!-- 本文件说明：风险可视化首页，对应开题报告中的风险总览与图表分析模块。 -->
<template>
  <div>
    <PageHeader>
      <template #title>风险仪表盘</template>
      <template #description>展示项目总数、扫描总数和高危风险统计。</template>
    </PageHeader>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <StatCard label="项目数" :value="0" />
      <StatCard label="扫描任务" :value="0" />
      <StatCard label="高危风险" :value="0" />
    </div>
    <RiskOverviewChart />
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../components/common/PageHeader.vue'
import StatCard from '../components/common/StatCard.vue'
import RiskOverviewChart from '../components/dashboard/RiskOverviewChart.vue'
</script>
