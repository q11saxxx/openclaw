<template>
  <div class="dashboard-container fade-in">
    <div class="page-header">
      <div>
        <h1 class="page-title">仪表盘</h1>
        <p class="page-subtitle">实时监控您的技能包安全状态</p>
      </div>
      <el-button type="primary" size="large" @click="$router.push('/skills')">
        <el-icon><Upload /></el-icon>
        <span>上传技能包</span>
      </el-button>
    </div>

    <el-alert
      type="info"
      :closable="false"
      class="welcome-alert"
      show-icon
    >
      <template #title>
        <span style="font-weight: 600">欢迎使用 OpenClaw 技能包风险审计平台</span>
      </template>
      <template #default>
        <p>这是一个专业的技能包安全审计平台，通过多维度检测帮您识别第三方技能包的潜在安全风险。</p>
      </template>
    </el-alert>

    <div class="stats-grid">
      <el-card class="stat-card primary" shadow="hover">
        <div class="stat-icon">
          <el-icon :size="32"><FolderOpened /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">技能包总数</div>
          <div class="stat-value">{{ totalSkills }}</div>
          <div class="stat-trend">
            <span class="trend-label">累计上传</span>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card danger" shadow="hover">
        <div class="stat-icon">
          <el-icon :size="32"><Warning /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">高风险技能包</div>
          <div class="stat-value">{{ highRiskCount }}</div>
          <div class="stat-trend">
            <span class="trend-label">需重点关注</span>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card warning" shadow="hover">
        <div class="stat-icon">
          <el-icon :size="32"><DataAnalysis /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">今日审计</div>
          <div class="stat-value">{{ todayAudits }}</div>
          <div class="stat-trend">
            <span class="trend-label">今日已完成</span>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card success" shadow="hover">
        <div class="stat-icon">
          <el-icon :size="32"><DocumentChecked /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">审计报告</div>
          <div class="stat-value">{{ totalReports }}</div>
          <div class="stat-trend">
            <span class="trend-label">已生成报告</span>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card info clickable-card" shadow="hover" @click="$router.push('/statistics')">
        <div class="stat-icon">
          <el-icon :size="32"><TrendCharts /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">统计分析</div>
          <div class="stat-value">查看</div>
          <div class="stat-trend">
            <span class="trend-label">趋势与洞察 →</span>
          </div>
        </div>
      </el-card>
    </div>

    <div class="content-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <el-icon :size="20" style="margin-right: 8px; color: var(--primary-color)"><Folder /></el-icon>
              <span>最近上传的技能包</span>
            </div>
            <el-button text type="primary" @click="$router.push('/skills')">
              查看全部
              <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </template>
        <el-table :data="recentSkills" v-loading="!recentSkills.length" class="modern-table">
          <el-table-column prop="name" label="名称" min-width="150" show-overflow-tooltip />
          <el-table-column prop="filename" label="文件名" min-width="120" show-overflow-tooltip />
          <el-table-column label="大小" min-width="100">
            <template #default="{ row }">
              {{ formatSize(row.size) }}
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="上传时间" min-width="160">
            <template #default="{ row }">
              <el-icon><Clock /></el-icon>
              <span style="margin-left: 6px">{{ formatTime(row.created_at) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" min-width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.status === 'audited' ? 'success' : 'info'" size="small">
                {{ row.status === 'audited' ? '已审计' : '待审计' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right" align="center">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewSkill(row.id)">
                <el-icon><View /></el-icon>
                <span>详情</span>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="recentSkills.length === 0" description="暂无上传记录" :image-size="120">
          <el-button type="primary" @click="$router.push('/skills')">立即上传</el-button>
        </el-empty>
      </el-card>
    </div>

    <div class="content-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <el-icon :size="20" style="margin-right: 8px; color: var(--primary-color)"><Tickets /></el-icon>
              <span>最近审计报告</span>
            </div>
            <el-button text type="primary" @click="$router.push('/reports')">
              查看全部
              <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </template>
        <el-table :data="recentReports" v-loading="!recentReports.length" class="modern-table">
          <el-table-column prop="skill_name" label="技能包名称" min-width="150" show-overflow-tooltip />
          <el-table-column label="风险等级" width="120" align="center">
            <template #default="{ row }">
              <RiskBadge :level="row.risk_level" />
            </template>
          </el-table-column>
          <el-table-column label="发现数量" width="100" align="center">
            <template #default="{ row }">
              <el-tag type="info" size="small">{{ row.finding_count || 0 }} 项</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="生成时间" min-width="160">
            <template #default="{ row }">
              <el-icon><Clock /></el-icon>
              <span style="margin-left: 6px">{{ formatTime(row.created_at) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right" align="center">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewReport(row.id)">
                <el-icon><View /></el-icon>
                <span>查看</span>
              </el-button>
              <el-button type="success" link size="small" @click="downloadReport(row.id, 'md')">
                <el-icon><Download /></el-icon>
                <span>Markdown</span>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="recentReports.length === 0" description="暂无审计报告" :image-size="120">
          <el-button type="primary" @click="$router.push('/audit/new')">发起审计</el-button>
        </el-empty>
      </el-card>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Upload, FolderOpened, Warning, DataAnalysis, DocumentChecked, 
  Folder, Tickets, ArrowRight, View, Download, Clock, TrendCharts
} from '@element-plus/icons-vue'
import RiskBadge from '../components/RiskBadge.vue'
import api from '../api/request'

const router = useRouter()

const totalSkills = ref(0)
const totalReports = ref(0)
const highRiskCount = ref(0)
const todayAudits = ref(0)
const recentSkills = ref<any[]>([])
const recentReports = ref<any[]>([])

const viewSkill = (id: string) => router.push(`/skills/${id}`)
const viewReport = (id: string) => router.push(`/report/${id}`)

const downloadReport = async (id: string, format: string) => {
  try {
    const response = await api.get(`/reports/${id}/export`, {
      params: { format },
      responseType: 'blob'
    })
    const blob = response.data
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `report_${id}.${format}`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Download failed:', e)
  }
}

const formatSize = (bytes: number) => {
  if (!bytes) return '-'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

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

const fetchDashboardData = async () => {
  try {
    const res: any = await api.get('/audits/stats')
    const data = res.data || res
    totalSkills.value = data.total_skills || 0
    totalReports.value = data.total_reports || 0
    highRiskCount.value = data.high_risk_count || 0
    todayAudits.value = data.today_audits || 0
    recentSkills.value = data.recent_skills || []
    recentReports.value = data.recent_reports || []
  } catch (e) {
    console.error('Failed to fetch dashboard data:', e)
  }
}

onMounted(() => {
  fetchDashboardData()
})
</script>

<style scoped>
.dashboard-container {
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

.welcome-alert {
  margin-bottom: 28px;
  border-radius: 12px;
  border: none;
  box-shadow: var(--shadow-sm);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
  margin-bottom: 28px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
  border-radius: 16px;
  color: white;
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-card::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
  pointer-events: none;
}

.stat-card:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: var(--shadow-xl);
}

.stat-card.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-card.danger {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-card.warning {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stat-card.success {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-card.info {
  background: linear-gradient(135deg, #63b7af 0%, #8fd3f4 100%);
}

.stat-card.clickable-card:hover {
  cursor: pointer;
}

.stat-icon {
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  opacity: 0.95;
  margin-bottom: 8px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 40px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 8px;
  text-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.stat-trend {
  font-size: 12px;
  opacity: 0.85;
  font-weight: 500;
}

.content-section {
  margin-top: 28px;
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

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-card {
    padding: 20px;
  }
  
  .stat-value {
    font-size: 32px;
  }
}
</style>
