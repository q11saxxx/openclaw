<!-- 本文件说明：前端根组件，统一使用主布局承载各页面。 -->
<template>
  <MainLayout>
    <router-view />
  </MainLayout>
</template>

<script setup lang="ts">
import MainLayout from './layouts/MainLayout.vue'
</script>
