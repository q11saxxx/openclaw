import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    { path: '/', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
    { path: '/skills', name: 'Skills', component: () => import('../views/skills/List.vue') },
    { path: '/skills/:id', name: 'SkillDetail', component: () => import('../views/skills/Detail.vue') },
    { path: '/audit', name: 'Audit', component: () => import('../views/audit/Tasks.vue') },
    { path: '/audit/new', name: 'AuditNew', component: () => import('../views/audit/New.vue') },
    { path: '/audit/:id/progress', name: 'AuditProgress', component: () => import('../views/audit/Progress.vue') },
    { path: '/report/:id', name: 'ReportDetail', component: () => import('../views/report/Detail.vue') },
    { path: '/reports', name: 'Reports', component: () => import('../views/reports/List.vue') },
    {
      path: '/reports/compare',
      name: 'ReportCompare',
      component: () => import('../views/reports/Compare.vue')
    },
    { path: '/rules', name: 'Rules', component: () => import('../views/Rules.vue') },
    { path: '/statistics', name: 'Statistics', component: () => import('../views/Statistics.vue') }
]

const router = createRouter({ history: createWebHistory(), routes })
export default router
