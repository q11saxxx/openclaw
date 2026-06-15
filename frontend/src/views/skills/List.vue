<template>
  <div class="skills-page fade-in">
    <div class="page-header">
      <div>
        <h1 class="page-title">技能包管理</h1>
        <p class="page-subtitle">管理和查看所有已上传的技能包</p>
      </div>
      <upload-skill @uploaded="refresh" />
    </div>

    <!-- 搜索和过滤 -->
    <el-card class="filter-card" shadow="hover">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="搜索">
          <el-input 
            v-model="q" 
            placeholder="按名称/路径搜索" 
            class="search-input"
            clearable
            @keyup.enter="refresh"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="风险等级">
          <el-select v-model="riskFilter" placeholder="全部" class="filter-select" clearable @change="refresh">
            <el-option label="严重" value="critical">
              <span style="color:#dc2626">●</span> 严重
            </el-option>
            <el-option label="高危" value="high">
              <span style="color:#ea580c">●</span> 高危
            </el-option>
            <el-option label="中危" value="medium">
              <span style="color:#f59e0b">●</span> 中危
            </el-option>
            <el-option label="低危" value="low">
              <span style="color:#10b981">●</span> 低危
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="refresh" class="refresh-btn">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 技能包列表 -->
    <el-card class="table-card" shadow="hover" v-loading="store.loading">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon :size="20" style="color: var(--primary-color)"><FolderOpened /></el-icon>
            <span>技能包列表</span>
            <el-tag type="info" size="small" style="margin-left: 12px">{{ total }} 个技能包</el-tag>
          </div>
        </div>
      </template>
      
      <el-table :data="skills" class="modern-table" stripe>
        <el-table-column prop="name" label="技能包名称" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <div style="display:flex;align-items:center;gap:8px">
              <el-icon style="color: var(--primary-color)"><Document /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="version" label="版本" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="info" effect="plain">{{ row.version || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="author" label="开发者" width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <div v-if="row.author" style="display:flex;align-items:center;gap:6px">
              <el-avatar :size="24" style="background: var(--gradient-primary)">
                {{ row.author.charAt(0).toUpperCase() }}
              </el-avatar>
              <span>{{ row.author }}</span>
            </div>
            <span v-else style="color: var(--text-muted)">-</span>
          </template>
        </el-table-column>
        <el-table-column label="文件大小" width="120" align="center">
          <template #default="{ row }">
            <span style="font-weight: 500">{{ formatFileSize(row.size) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="风险等级" width="120" align="center">
          <template #default="{ row }">
            <risk-badge :level="row.risk_level" />
          </template>
        </el-table-column>
        <el-table-column prop="last_audit" label="最后审计时间" width="180">
          <template #default="{ row }">
            <span v-if="row.last_audit" style="color: var(--text-secondary)">
              {{ formatTime(row.last_audit) }}
            </span>
            <el-tag v-else size="small" type="info" effect="plain">未审计</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="上传时间" width="180">
          <template #default="{ row }">
            <span style="color: var(--text-secondary)">
              {{ formatTime(row.created_at) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="goDetail(row.id)">
              <el-icon><View /></el-icon>
              <span>详情</span>
            </el-button>
            <el-button type="success" link size="small" @click="startAudit(row.id)">
              <el-icon><VideoPlay /></el-icon>
              <span>审计</span>
            </el-button>
            <el-popconfirm
              title="确定删除该技能包？将移除列表记录并删除已上传文件，历史报告仍保留。"
              confirm-button-text="删除"
              cancel-button-text="取消"
              confirm-button-type="danger"
              width="280"
              @confirm="removeSkill(row)"
            >
              <template #reference>
                <el-button
                  type="danger"
                  link
                  size="small"
                  :loading="deletingId === row.id"
                  :disabled="deletingId !== null && deletingId !== row.id"
                >
                  <el-icon><Delete /></el-icon>
                  <span>删除</span>
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination 
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="onSizeChange"
          @current-change="onPageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useSkillStore } from '../../stores/skill'
import UploadSkill from '../../components/UploadSkill.vue'
import RiskBadge from '../../components/RiskBadge.vue'
import { useRouter } from 'vue-router'
import { Search, Refresh, FolderOpened, Document, View, VideoPlay, Delete } from '@element-plus/icons-vue'
import { runAudit } from '../../api/audit'
import { deleteSkill } from '../../api/skill'
import { ElMessage } from 'element-plus'

const store = useSkillStore()
const router = useRouter()

const q = ref('')
const riskFilter = ref('')
const page = ref(1)
const pageSize = ref(10)
const deletingId = ref<string | null>(null)

const skills = computed(() => store.skills)
const total = computed(() => store.total)

let searchTimer: any = null

// 搜索防抖
watch(q, () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    refresh()
  }, 500)
})

const refresh = async () => {
  await store.fetchSkills({ 
    page: page.value, 
    size: pageSize.value, 
    q: q.value,
    risk_level: riskFilter.value || undefined
  })
}

const onPageChange = (p: number) => { 
  page.value = p
  refresh() 
}

const onSizeChange = (size: number) => {
  pageSize.value = size
  page.value = 1
  refresh()
}

const goDetail = (id: string) => router.push(`/skills/${id}`)

const startAudit = async (id: string) => {
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

const removeSkill = async (row: { id: string }) => {
  deletingId.value = row.id
  try {
    await deleteSkill(row.id)
    ElMessage.success('已删除该技能包')
    await refresh()
    if (skills.value.length === 0 && page.value > 1) {
      page.value = Math.max(1, page.value - 1)
      await refresh()
    }
  } catch (e) {
    console.error('Delete skill failed:', e)
  } finally {
    deletingId.value = null
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
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => { refresh() })
</script>

<style scoped>
.skills-page {
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

.filter-card {
  margin-bottom: 24px;
}

.filter-form {
  margin: 0;
}

.search-input {
  width: 300px;
}

.filter-select {
  width: 150px;
}

.refresh-btn {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
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

.pagination-wrapper {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .filter-form {
    display: flex;
    flex-direction: column;
  }
  
  .search-input,
  .filter-select {
    width: 100%;
  }
}
</style>
