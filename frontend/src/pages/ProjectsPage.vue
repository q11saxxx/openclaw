<!-- 本文件说明：项目管理页面，对应开题报告中的项目与插件管理模块。 -->
<template>
  <div>
    <PageHeader>
      <template #title>项目与插件管理</template>
      <template #description>创建项目、区分 OpenClaw 插件和通用项目，并查看历史扫描。</template>
    </PageHeader>
    <ProjectTable />
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../components/common/PageHeader.vue'
import ProjectTable from '../components/project/ProjectTable.vue'
</script>
