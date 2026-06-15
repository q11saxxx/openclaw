<template>
  <div class="skill-detail fade-in">
    <div class="page-header">
      <el-page-header @back="$router.back()">
        <template #content>
          <div class="header-content">
            <span class="header-title">技能包详情</span>
            <span class="header-subtitle" v-if="skill.name">{{ skill.name }}</span>
          </div>
        </template>
      </el-page-header>
    </div>

    <el-row :gutter="24">
      <!-- 左侧：基本信息 -->
      <el-col :xs="24" :lg="16">
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon :size="20" style="color: var(--primary-color)"><FolderOpened /></el-icon>
                <span>基本信息</span>
              </div>
              <el-button type="primary" @click="startAudit" class="audit-btn">
                <el-icon><VideoPlay /></el-icon>
                <span>开始审计</span>
              </el-button>
            </div>
          </template>
          
          <el-descriptions :column="2" border class="skill-descriptions">
            <el-descriptions-item label="标识">
              <code class="id-code">{{ id }}</code>
            </el-descriptions-item>
            <el-descriptions-item label="名称">
              <span style="font-weight: 500">{{ skill.name || '-' }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="文件名">
              {{ skill.filename || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="版本">
              <el-tag size="small" type="info" effect="plain">{{ skill.version || '-' }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="开发者">
              <div v-if="skill.author" style="display:flex;align-items:center;gap:8px">
                <el-avatar :size="28" style="background: var(--gradient-primary)">
                  {{ skill.author.charAt(0).toUpperCase() }}
                </el-avatar>
                <span>{{ skill.author }}</span>
              </div>
              <span v-else style="color: var(--text-muted)">-</span>
            </el-descriptions-item>
            <el-descriptions-item label="文件大小">
              <span style="font-weight: 500">{{ formatFileSize(skill.size) }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="风险等级">
              <risk-badge :level="skill.risk_level" />
            </el-descriptions-item>
            <el-descriptions-item label="上传时间">
              <span style="color: var(--text-secondary)">{{ formatTime(skill.created_at) }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="SHA256" :span="2">
              <div class="hash-container">
                <el-text type="info" size="small" class="hash-text">
                  {{ skill.sha256 || '-' }}
                </el-text>
                <el-button 
                  v-if="skill.sha256" 
                  text 
                  size="small" 
                  @click="copyHash"
                  class="copy-btn"
                >
                  <el-icon><CopyDocument /></el-icon>
                  复制
                </el-button>
              </div>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- Manifest / 元数据 -->
        <el-card class="manifest-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon :size="20" style="color: var(--primary-color)"><Document /></el-icon>
                <span>清单（Manifest）与元数据</span>
              </div>
            </div>
          </template>
          <el-collapse>
            <el-collapse-item name="manifest">
              <template #title>
                <span style="font-weight:600">查看清单原文</span>
              </template>
              <div class="code-block">
                <pre>{{ manifest }}</pre>
              </div>
            </el-collapse-item>
          </el-collapse>
        </el-card>

        <!-- 快速检测 -->
        <el-card class="quick-check-card" shadow="hover" v-if="quick_check">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon :size="20" style="color: var(--primary-color)"><DataAnalysis /></el-icon>
                <span>快速检测结果</span>
              </div>
              <risk-badge :level="quick_check.level" />
            </div>
          </template>
          
          <el-descriptions :column="2" border class="quick-descriptions">
            <el-descriptions-item label="风险等级">
              <risk-badge :level="quick_check.level" />
            </el-descriptions-item>
            <el-descriptions-item label="发现总数">
              <el-tag type="info" effect="plain">
                {{ quick_check.summary?.script?.total_findings || quick_check.findings?.length || 0 }} 项
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
          
          <div style="margin-top:16px">
            <el-button size="small" @click="showQuick=true">
              <el-icon><View /></el-icon>
              <span>查看详细证据</span>
            </el-button>
          </div>
          
          <el-dialog v-model="showQuick" title="快速检测证据" width="70%" class="evidence-dialog">
            <div class="evidence-code">
              <pre>{{ JSON.stringify(quick_check, null, 2) }}</pre>
            </div>
          </el-dialog>
        </el-card>
      </el-col>

      <!-- 右侧：审计报告 -->
      <el-col :xs="24" :lg="8">
        <el-card class="reports-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon :size="20" style="color: var(--primary-color)"><Tickets /></el-icon>
                <span>审计报告</span>
              </div>
            </div>
          </template>
          
          <div v-if="reports && reports.length" class="reports-timeline">
            <el-timeline>
              <el-timeline-item 
                v-for="(report, index) in reports" 
                :key="index"
                placement="top"
              >
                <div class="timeline-content">
                  <div class="timeline-header">
                    <span class="timeline-title">报告 #{{ index + 1 }}</span>
                    <span class="timeline-time">{{ formatTime(report.created_at) }}</span>
                  </div>
                  <div class="timeline-id">
                    <el-icon><Document /></el-icon>
                    <span>{{ report.id }}</span>
                  </div>
                  <div class="timeline-actions">
                    <el-button type="primary" size="small" @click="viewReport(report.id)">
                      <el-icon><View /></el-icon>
                      <span>查看</span>
                    </el-button>
                    <el-button size="small" @click="downloadReport(report.id, 'md')">
                      <el-icon><Document /></el-icon>
                      <span>Markdown</span>
                    </el-button>
                    <el-button size="small" @click="downloadReport(report.id, 'json')">
                      <el-icon><Files /></el-icon>
                      <span>JSON 数据</span>
                    </el-button>
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>
          </div>
          <div v-else class="no-reports">
            <el-empty description="尚无可用报告" :image-size="100">
              <el-button type="primary" @click="startAudit">
                <el-icon><VideoPlay /></el-icon>
                <span>立即审计</span>
              </el-button>
            </el-empty>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getSkill } from '../../api/skill'
import { exportReport } from '../../api/report'
import { runAudit } from '../../api/audit'
import RiskBadge from '../../components/RiskBadge.vue'
import { ElMessage } from 'element-plus'
import { 
  VideoPlay, FolderOpened, Document, DataAnalysis, 
  View, CopyDocument, Tickets, Files 
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const id = route.params.id as string

const skill = ref<any>({})
const manifest = ref('')
const reports = ref<any[]>([])
const quick_check = ref<any>(null)
const showQuick = ref(false)

onMounted(async () => {
  try {
    const res: any = await getSkill(id)
    skill.value = res || {}
    
    // 解析 manifest
    if (res?.parsed?.parsed?.manifest) {
      manifest.value = JSON.stringify(res.parsed.parsed.manifest, null, 2)
    } else if (res?.parsed?.manifest) {
      manifest.value = JSON.stringify(res.parsed.manifest, null, 2)
    } else {
      manifest.value = JSON.stringify(res, null, 2)
    }
    
    reports.value = res?.reports || []
    quick_check.value = res?.quick_check || null
  } catch (e) {
    console.error('Failed to fetch skill detail:', e)
    manifest.value = '无法获取详情'
  }
})

const viewReport = (rid: string) => {
  router.push(`/report/${rid}`)
}

const downloadReport = async (rid: string, format: string) => {
  try {
    const res: any = await exportReport(rid, format)
    const blob: Blob = res.data || res
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `report_${rid}.${format === 'md' ? 'md' : 'json'}`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Download failed:', e)
  }
}

const startAudit = async () => {
  try {
    const res: any = await runAudit({ skill_id: id, options: { semantic: true } })
    const data = res.data || res
    const auditId = data.audit_id || data.report_id || data.id
    if (auditId) {
      router.push(`/audit/${auditId}/progress`)
    }
  } catch (e) {
    console.error('Audit failed:', e)
  }
}

const formatFileSize = (bytes: number) => {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(2) + ' MB'
}

const formatTime = (time: string) => {
  if (!time) return '-'
  const date = new Date(time)
  return date.toLocaleString('zh-CN', { 
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const copyHash = async () => {
  try {
    await navigator.clipboard.writeText(skill.value.sha256)
    ElMessage.success('SHA256 已复制到剪贴板')
  } catch (e) {
    ElMessage.error('复制失败')
  }
}
</script>

<style scoped>
.skill-detail {
  padding: 0;
}

.page-header {
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 2px solid var(--border-color);
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.header-title {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.info-card,
.manifest-card,
.quick-check-card,
.reports-card {
  border-radius: 16px;
  margin-bottom: 24px;
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

.audit-btn {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.skill-descriptions,
.quick-descriptions {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
  width: 120px;
}

.id-code {
  font-family: monospace;
  font-size: 12px;
  background: #f1f5f9;
  padding: 4px 8px;
  border-radius: 4px;
}

.hash-container {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.hash-text {
  flex: 1;
  word-break: break-all;
  font-family: monospace;
  font-size: 11px;
}

.copy-btn {
  flex-shrink: 0;
}

.code-block {
  background: #1e1e1e;
  border-radius: 8px;
  padding: 16px;
  max-height: 400px;
  overflow: auto;
}

.code-block pre {
  margin: 0;
  color: #d4d4d4;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.evidence-dialog :deep(.el-dialog) {
  border-radius: 16px;
}

.evidence-code {
  background: #1e1e1e;
  border-radius: 8px;
  padding: 16px;
  max-height: 60vh;
  overflow: auto;
}

.evidence-code pre {
  margin: 0;
  color: #d4d4d4;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.reports-timeline {
  max-height: 600px;
  overflow-y: auto;
  padding-right: 8px;
}

.timeline-content {
  background: linear-gradient(135deg, rgba(248, 250, 252, 0.8) 0%, rgba(241, 245, 249, 0.8) 100%);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid var(--border-color);
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.timeline-title {
  font-weight: 600;
  color: var(--text-primary);
}

.timeline-time {
  font-size: 12px;
  color: var(--text-muted);
}

.timeline-id {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 12px;
  font-family: monospace;
}

.timeline-actions {
  display: flex;
  gap: 8px;
}

.no-reports {
  padding: 20px 0;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .timeline-actions {
    flex-direction: column;
  }
  
  .timeline-actions .el-button {
    width: 100%;
  }
}
</style>
