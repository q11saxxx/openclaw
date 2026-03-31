// 本文件说明：前端路由配置，按功能模块拆分页面入口。
import { createRouter, createWebHistory } from 'vue-router'
import DashboardPage from '../pages/DashboardPage.vue'
import ProjectsPage from '../pages/ProjectsPage.vue'
import ScanTaskPage from '../pages/ScanTaskPage.vue'
import ReportPage from '../pages/ReportPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/dashboard' },
    { path: '/dashboard', component: DashboardPage },
    { path: '/projects', component: ProjectsPage },
    { path: '/scans/:id', component: ScanTaskPage },
    { path: '/reports/:id', component: ReportPage }
  ]
})

export default router
