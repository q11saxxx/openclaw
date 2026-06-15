<template>
  <div class="audit-tasks fade-in">
    <div class="page-header">
      <div>
        <h1 class="page-title">审计任务</h1>
        <p class="page-subtitle">跟踪和管理所有正在进行的审计任务</p>
      </div>
      <el-button type="primary" size="large" @click="$router.push('/audit/new')">
        <el-icon><CirclePlusFilled /></el-icon>
        <span>发起新审计</span>
      </el-button>
    </div>
    
    <el-card class="table-card" shadow="hover" v-loading="loading">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon :size="20" style="color: var(--primary-color)"><DataAnalysis /></el-icon>
            <span>任务列表</span>
            <el-tag type="info" size="small" style="margin-left: 12px">{{ tasks.length }} 个任务</el-tag>
          </div>
        </div>
      </template>
      
      <el-table :data="tasks" class="modern-table" stripe>
        <el-table-column prop="id" label="任务ID" min-width="280" show-overflow-tooltip>
          <template #default="{ row }">
            <div style="display:flex;align-items:center;gap:8px">
              <el-icon style="color: var(--primary-color)"><Operation /></el-icon>
              <span style="font-family: monospace; font-size: 12px">{{ row.id }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="skill_name" label="技能包名称" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <span style="font-weight: 500">{{ row.skill_name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="风险等级" width="120" align="center">
          <template #default="{ row }">
            <risk-badge :level="row.summary?.level || row.risk_level" />
          </template>
        </el-table-column>
        <el-table-column label="置信度" width="120" align="center">
          <template #default="{ row }">
            <div class="confidence-badge">
              <el-icon><SuccessFilled /></el-icon>
              <span>{{ row.confidence ? Math.round(row.confidence * 100) : 0 }}%</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="发现数量" width="120" align="center">
          <template #default="{ row }">
            <span style="font-weight: 600; color: var(--text-primary)">{{ row.finding_count || 0 }} 项</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : 'warning'" size="small">
              {{ row.status === 'completed' ? '已完成' : '进行中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            <div style="display:flex;align-items:center;gap:6px; color: var(--text-secondary)">
              <el-icon><Clock /></el-icon>
              <span>{{ formatTime(row.created_at) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="view(row.id)">
              <el-icon><VideoPlay /></el-icon>
              <span>进度</span>
            </el-button>
            <el-button type="success" link size="small" @click="viewReport(row.id)">
              <el-icon><Document /></el-icon>
              <span>报告</span>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-empty v-if="!tasks.length" description="暂无审计任务" :image-size="120">
        <el-button type="primary" @click="$router.push('/audit/new')">
          <el-icon><CirclePlusFilled /></el-icon>
          <span>发起新审计</span>
        </el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { listAudits } from '../../api/audit'
import { useRouter } from 'vue-router'
import RiskBadge from '../../components/RiskBadge.vue'
import { 
  CirclePlusFilled, DataAnalysis, Operation, SuccessFilled, 
  Clock, VideoPlay, Document 
} from '@element-plus/icons-vue'

const tasks = ref<any[]>([])
const loading = ref(false)
const router = useRouter()

const fetch = async () => {
  loading.value = true
  try {
    const res: any = await listAudits({})
    tasks.value = res.items || res || []
  } catch (e) {
    console.error('Failed to fetch audits:', e)
    tasks.value = []
  } finally {
    loading.value = false
  }
}

const view = (id: string) => router.push(`/audit/${id}/progress`)
const viewReport = (id: string) => router.push(`/report/${id}`)

const formatTime = (time: string) => {
  if (!time) return '-'
  const date = new Date(time)
  return date.toLocaleString('zh-CN', { 
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => { fetch() })
</script>

<style scoped>
.audit-tasks {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 2px solid var(--border-color);
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  margin: 0;
  color: var(--text-secondary);
  font-size: 15px;
}

.table-card {
  border-radius: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}

.modern-table {
  border-radius: 12px;
}

:deep(.el-table) {
  border: none;
  box-shadow: none;
}

:deep(.el-table th) {
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
}

:deep(.el-table td) {
  padding: 14px 0;
}

:deep(.el-table tr:hover > td) {
  background-color: rgba(102, 126, 234, 0.04) !important;
}

.confidence-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-radius: 20px;
  color: var(--primary-color);
  font-weight: 600;
  font-size: 13px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}
</style>
