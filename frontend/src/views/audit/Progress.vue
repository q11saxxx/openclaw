<template>
  <div class="audit-progress fade-in">
    <div class="page-header">
      <div>
        <h1 class="page-title">审计进度</h1>
        <p class="page-subtitle">实时跟踪审计任务执行状态</p>
      </div>
    </div>
    
    <el-card class="progress-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon :size="20" style="color: var(--primary-color)"><Loading /></el-icon>
            <span>任务执行</span>
            <el-tag :type="completed ? 'success' : 'warning'" size="small" style="margin-left: 12px">
              {{ completed ? '已完成' : '进行中' }}
            </el-tag>
          </div>
        </div>
      </template>
      
      <progress-steps :stage="stage" :logs="logs" :completed="completed" />

      <div class="notify-panel">
        <span class="notify-label">长耗时审计时可在后台做其他事：</span>
        <el-button
          v-if="notifyPermission !== 'granted'"
          size="small"
          type="primary"
          plain
          @click="enableDesktopNotify"
        >
          启用桌面完成通知
        </el-button>
        <el-tag v-else type="success" size="small" effect="plain">已启用桌面通知</el-tag>
        <span v-if="notifyPermission === 'denied'" class="notify-denied">（浏览器已拒绝通知权限）</span>
      </div>
      
      <div v-if="completed && reportId" class="completion-section">
        <div class="completion-content">
          <div class="completion-icon">
            <el-icon :size="64" color="#67c23a"><CircleCheckFilled /></el-icon>
          </div>
          <h2 class="completion-title">审计完成</h2>
          <p class="completion-subtitle">审计报告已生成，您可以查看详细结果</p>
          <div class="completion-actions">
            <el-button type="primary" @click="viewReport" size="large">
              <el-icon><Document /></el-icon>
              <span>查看报告</span>
            </el-button>
            <el-button @click="$router.push('/audit')" size="large">
              <el-icon><Back /></el-icon>
              <span>返回任务列表</span>
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import ProgressSteps from '../../components/ProgressSteps.vue'
import { useRoute, useRouter } from 'vue-router'
import { getAuditStatus } from '../../api/audit'
import { Loading, CircleCheckFilled, Document, Back } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const id = route.params.id as string

const stage = ref(0)
const logs = ref('')
const completed = ref(false)
const reportId = ref('')
const notifyPermission = ref(typeof Notification !== 'undefined' ? Notification.permission : 'denied')
const desktopNotifyOn = ref(false)

let timer: any = null
let notified = false

const enableDesktopNotify = async () => {
  if (typeof Notification === 'undefined') {
    return
  }
  try {
    const p = await Notification.requestPermission()
    notifyPermission.value = p
    if (p === 'granted') {
      desktopNotifyOn.value = true
    }
  } catch {
    notifyPermission.value = 'denied'
  }
}

const fireCompleteNotification = () => {
  if (!desktopNotifyOn.value || notifyPermission.value !== 'granted' || notified) {
    return
  }
  try {
    const rid = reportId.value || id
    new Notification('OpenClaw 审计已完成', {
      body: '点击查看报告详情',
      tag: `openclaw-audit-${rid}`
    })
    notified = true
  } catch {
    /* ignore */
  }
}

watch(
  () => completed.value,
  (done) => {
    if (done) {
      fireCompleteNotification()
    }
  }
)

const poll = async () => {
  try {
    const res: any = await getAuditStatus(id)
    const data = res.data || res
    
    console.log('Audit status response:', data) // 调试信息
    
    // 更新进度
    stage.value = data.progress || 100
    
    // 处理日志显示
    const logsArray = data.logs || []
    if (logsArray.length > 0) {
      logs.value = logsArray.join('\n')
    } else if (completed.value || data.completed) {
      logs.value = '审计流程已完成\n报告已生成并保存'
    } else {
      logs.value = '等待审计开始...'
    }
    
    // 检查是否完成 - 对于同步审计，如果有报告数据就认为完成
    const hasReport = data.report_id || data.id || data.findings
    completed.value = hasReport ? true : (data.completed || false)
    
    // 如果已完成，获取报告ID
    if (completed.value && !reportId.value) {
      reportId.value = data.report_id || data.id || id
    }
    
    // 如果未完成，继续轮询
    if (!completed.value) {
      timer = setTimeout(poll, 2000)
    }
  } catch (e) {
    console.error('Poll failed:', e)
    // 出错后继续尝试
    timer = setTimeout(poll, 3000)
  }
}

const viewReport = () => {
  if (reportId.value) {
    router.push(`/report/${reportId.value}`)
  } else {
    // 如果没有 reportId，使用当前审计 ID
    router.push(`/report/${id}`)
  }
}

onMounted(() => { poll() })

onUnmounted(() => {
  if (timer) {
    clearTimeout(timer)
  }
})
</script>

<style scoped>
.audit-progress {
  padding: 0;
}

.page-header {
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

.progress-card {
  border-radius: 16px;
  min-height: 500px;
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

.notify-panel {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  margin-top: 20px;
  padding: 12px 16px;
  background: var(--el-fill-color-light);
  border-radius: 10px;
}

.notify-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.notify-denied {
  font-size: 12px;
  color: var(--el-color-warning);
}

.completion-section {
  margin-top: 40px;
  padding-top: 40px;
  border-top: 2px solid var(--border-color);
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.completion-content {
  text-align: center;
  padding: 20px;
}

.completion-icon {
  margin-bottom: 24px;
  animation: scaleIn 0.5s ease-out;
}

@keyframes scaleIn {
  from {
    transform: scale(0);
  }
  to {
    transform: scale(1);
  }
}

.completion-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.completion-subtitle {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0 0 32px 0;
}

.completion-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.completion-actions .el-button {
  min-width: 140px;
}

@media (max-width: 768px) {
  .completion-actions {
    flex-direction: column;
  }
  
  .completion-actions .el-button {
    width: 100%;
  }
}
</style>
