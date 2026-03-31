<!-- 本文件说明：审计报告页面，对应报告预览、导出和修复建议模块。 -->
<template>
  <div>
    <PageHeader>
      <template #title>审计报告</template>
      <template #description>生成全中文报告，并预留 PDF/SARIF 导出入口。</template>
    </PageHeader>
    <ReportPreview />
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../components/common/PageHeader.vue'
import ReportPreview from '../components/report/ReportPreview.vue'
</script>
