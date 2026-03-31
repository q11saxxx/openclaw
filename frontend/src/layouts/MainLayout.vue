<!-- 本文件说明：前端主布局，包含侧边导航和页面容器。 -->
<template>
  <div class="min-h-screen flex">
    <aside class="w-64 bg-slate-900 text-white p-4 space-y-3">
      <h1 class="text-xl font-bold">OpenClaw Audit</h1>
      <nav class="space-y-2">
        <RouterLink to="/dashboard">仪表盘</RouterLink><br />
        <RouterLink to="/projects">项目管理</RouterLink>
      </nav>
    </aside>
    <main class="flex-1 p-6">
      <slot />
    </main>
  </div>
</template>
