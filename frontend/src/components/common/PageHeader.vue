<!-- 本文件说明：页面头部通用组件，减少重复标题区代码。 -->
<template>
  <div class="mb-6">
    <h2 class="text-2xl font-bold"><slot name="title" /></h2>
    <p class="text-slate-500"><slot name="description" /></p>
  </div>
</template>
