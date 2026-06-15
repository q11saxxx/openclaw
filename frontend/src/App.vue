<template>
  <el-container class="app-layout">
    <el-header height="64px">
      <div style="display:flex;align-items:center;gap:12px">
        <el-icon :size="28"><Lock /></el-icon>
        <span>OpenClaw 技能包风险审计平台</span>
      </div>
    </el-header>
    <el-container>
      <el-aside width="220px">
        <el-menu 
          :default-active="$route.path" 
          router
          :collapse="false"
        >
          <el-menu-item index="/">
            <el-icon><DataAnalysis /></el-icon>
            <span>仪表盘</span>
          </el-menu-item>
          <el-menu-item index="/skills">
            <el-icon><Files /></el-icon>
            <span>技能包管理</span>
          </el-menu-item>
          <el-menu-item index="/audit/new">
            <el-icon><VideoPlay /></el-icon>
            <span>发起审计</span>
          </el-menu-item>
          <el-menu-item index="/audit">
            <el-icon><List /></el-icon>
            <span>审计任务</span>
          </el-menu-item>
          <el-menu-item index="/reports">
            <el-icon><Document /></el-icon>
            <span>审计报告</span>
          </el-menu-item>
          <el-menu-item index="/rules">
            <el-icon><Setting /></el-icon>
            <span>规则管理</span>
          </el-menu-item>
          <el-menu-item index="/statistics">
            <el-icon><TrendCharts /></el-icon>
            <span>统计分析</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main>
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <div :key="$route.fullPath">
              <component :is="Component" />
            </div>
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script lang="ts" setup>
import { Lock, DataAnalysis, Files, VideoPlay, List, Document, Setting, TrendCharts } from '@element-plus/icons-vue'
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.app-layout {
  height: 100vh;
  overflow: hidden;
}

.app-layout > .el-header {
  position: sticky;
  top: 0;
  z-index: 100;
}

.app-layout > .el-container {
  height: calc(100vh - 64px);
}

.app-layout .el-aside {
  position: sticky;
  top: 64px;
  height: calc(100vh - 64px);
  overflow-y: auto;
}

.app-layout .el-main {
  height: calc(100vh - 64px);
  overflow-y: auto;
}
</style>
