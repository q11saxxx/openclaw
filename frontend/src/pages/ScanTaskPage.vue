<!-- 本文件说明：扫描任务详情页，对应上传扫描、自研规则命中与漏洞扫描结果页。 -->
<template>
  <div>
    <PageHeader>
      <template #title>扫描任务</template>
      <template #description>发起扫描并查看规则命中、漏洞结果和修复建议。</template>
    </PageHeader>
    <div class="space-y-4">
      <UploadPanel />
      <FindingList />
    </div>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../components/common/PageHeader.vue'
import UploadPanel from '../components/scan/UploadPanel.vue'
import FindingList from '../components/scan/FindingList.vue'
</script>
