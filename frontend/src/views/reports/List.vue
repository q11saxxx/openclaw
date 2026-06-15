<template>
  <div class="reports-list fade-in">
    <div class="page-header">
      <div>
        <h1 class="page-title">审计报告</h1>
        <p class="page-subtitle">查看和管理所有已生成的审计报告</p>
      </div>
      <el-button type="primary" size="large" @click="$router.push('/audit/new')">
        <el-icon><VideoPlay /></el-icon>
        <span>发起审计</span>
      </el-button>
    </div>
    
    <el-card class="table-card" shadow="hover" v-loading="loading">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon :size="20" style="color: var(--primary-color)"><Tickets /></el-icon>
            <span>报告列表</span>
            <el-tag type="info" size="small" style="margin-left: 12px">{{ filteredReports.length }} / {{ reports.length }} 个报告</el-tag>
          </div>
        </div>
      </template>

      <div v-if="reports.length" class="reports-toolbar">
        <el-input
          v-model="keyword"
          placeholder="按技能包名称筛选"
          clearable
          class="toolbar-search"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="riskFilter" placeholder="风险等级" clearable class="toolbar-risk">
          <el-option label="严重" value="critical" />
          <el-option label="高危" value="high" />
          <el-option label="中危" value="medium" />
          <el-option label="低危" value="low" />
          <el-option label="信息" value="info" />
        </el-select>
        <el-button
          :disabled="!selectedRows.length"
          :loading="batchLoading"
          @click="batchExport('md')"
        >
          <el-icon><Download /></el-icon>
          批量导出 Markdown
        </el-button>
        <el-button
          :disabled="!selectedRows.length"
          :loading="batchLoading"
          type="primary"
          plain
          @click="batchExport('json')"
        >
          <el-icon><Files /></el-icon>
          批量导出 JSON 数据
        </el-button>
        <el-tooltip content="需恰好选中 2 条报告" placement="top">
          <el-button
            :disabled="selectedRows.length !== 2"
            type="success"
            plain
            @click="goCompare"
          >
            双报告对比
          </el-button>
        </el-tooltip>
      </div>
      
      <el-table
        v-if="reports.length"
        :data="filteredReports"
        class="modern-table"
        stripe
        row-key="id"
        @selection-change="onSelectionChange"
      >
        <el-table-column type="selection" width="48" align="center" />
        <el-table-column prop="id" label="报告 ID" min-width="280" show-overflow-tooltip>
          <template #default="{ row }">
            <div style="display:flex;align-items:center;gap:8px">
              <el-icon style="color: var(--primary-color)"><Document /></el-icon>
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
        <el-table-column prop="created_at" label="生成时间" width="180">
          <template #default="{ row }">
            <div style="display:flex;align-items:center;gap:6px; color: var(--text-secondary)">
              <el-icon><Clock /></el-icon>
              <span>{{ formatTime(row.created_at) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="view(row.id)">
              <el-icon><View /></el-icon>
              <span>查看</span>
            </el-button>
            <el-button type="success" link size="small" @click="downloadOne(row.id, 'md')">
              <el-icon><Download /></el-icon>
              <span>Markdown</span>
            </el-button>
            <el-button type="warning" link size="small" @click="downloadOne(row.id, 'json')">
              <el-icon><Files /></el-icon>
              <span>JSON 数据</span>
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-alert
        v-if="reports.length && !filteredReports.length"
        type="warning"
        :closable="false"
        show-icon
        class="filter-empty-hint"
        title="当前筛选条件下没有匹配的报告，请调整关键词或风险等级。"
      />
      
      <el-empty v-if="!reports.length && !loading" description="暂无审计报告" :image-size="120">
        <el-button type="primary" @click="$router.push('/audit/new')">
          <el-icon><VideoPlay /></el-icon>
          <span>发起审计</span>
        </el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue'
import { listAudits } from '../../api/audit'
import { exportReport } from '../../api/report'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import RiskBadge from '../../components/RiskBadge.vue'
import { 
  VideoPlay, Tickets, Document, SuccessFilled, Clock, 
  View, Download, Files, Search
} from '@element-plus/icons-vue'

const reports = ref<any[]>([])
const loading = ref(false)
const router = useRouter()
const keyword = ref('')
const riskFilter = ref('')
const selectedRows = ref<any[]>([])
const batchLoading = ref(false)

const rowRiskLevel = (row: any) =>
  String(row.summary?.level || row.risk_level || '').toLowerCase()

const filteredReports = computed(() => {
  let list = reports.value
  const k = keyword.value.trim().toLowerCase()
  if (k) {
    list = list.filter((r: any) => (r.skill_name || '').toLowerCase().includes(k))
  }
  if (riskFilter.value) {
    list = list.filter((r: any) => rowRiskLevel(r) === riskFilter.value)
  }
  return list
})

const onSelectionChange = (rows: any[]) => {
  selectedRows.value = rows
}

const fetch = async () => {
  loading.value = true
  try {
    const res: any = await listAudits({})
    reports.value = res.items || []
  } catch (e) {
    console.error('Failed to fetch reports:', e)
    reports.value = []
  } finally {
    loading.value = false
  }
}

const view = (id: string) => router.push(`/report/${id}`)

const goCompare = () => {
  if (selectedRows.value.length !== 2) return
  const [a, b] = selectedRows.value
  router.push({
    name: 'ReportCompare',
    query: { left: a.id, right: b.id }
  })
}

const downloadOne = async (id: string, format: string) => {
  try {
    await download(id, format)
  } catch (e) {
    console.error('Download failed:', e)
    ElMessage.error('下载失败')
  }
}

const download = async (id: string, format: string) => {
  const res: any = await exportReport(id, format)
  const blob: Blob = res.data || res
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `report_${id}.${format === 'md' ? 'md' : 'json'}`
  a.click()
  URL.revokeObjectURL(url)
}

const batchExport = async (format: string) => {
  const rows = selectedRows.value
  if (!rows.length) return
  batchLoading.value = true
  try {
    for (const row of rows) {
      await download(row.id, format)
      await new Promise((r) => setTimeout(r, 280))
    }
    const fmtLabel = format === 'md' ? 'Markdown' : 'JSON'
    ElMessage.success(`已依次导出 ${rows.length} 个报告（${fmtLabel}）`)
  } catch (e) {
    console.error(e)
    ElMessage.error('批量导出中断，请重试或逐个下载')
  } finally {
    batchLoading.value = false
  }
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

onMounted(() => { fetch() })
</script>

<style scoped>
.reports-list {
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

.reports-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.toolbar-search {
  width: 240px;
  max-width: 100%;
}

.toolbar-risk {
  width: 140px;
}

.filter-empty-hint {
  margin-top: 12px;
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
