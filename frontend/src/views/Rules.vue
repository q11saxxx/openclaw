<template>
  <div class="rules-page fade-in">
    <div class="page-header">
      <div>
        <h1 class="page-title">规则管理</h1>
        <p class="page-subtitle">配置和管理安全审计规则</p>
      </div>
      <el-button type="primary" size="large" @click="showCreateDialog = true">
        <el-icon><CirclePlusFilled /></el-icon>
        <span>创建规则</span>
      </el-button>
    </div>
    
    <!-- 操作栏 -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-content">
        <div class="filter-left">
          <el-radio-group v-model="ruleType" @change="fetchRules" class="type-filter">
            <el-radio-button label="">
              <el-icon><Grid /></el-icon>
              <span>全部</span>
            </el-radio-button>
            <el-radio-button label="builtin">
              <el-icon><Lock /></el-icon>
              <span>内置规则</span>
            </el-radio-button>
            <el-radio-button label="custom">
              <el-icon><EditPen /></el-icon>
              <span>自定义规则</span>
            </el-radio-button>
          </el-radio-group>
        </div>
        <div class="filter-right">
          <el-tag type="info" size="small">{{ rules.length }} 条规则</el-tag>
        </div>
      </div>
    </el-card>

    <!-- 规则列表 -->
    <el-card class="table-card" shadow="hover" v-loading="loading">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon :size="20" style="color: var(--primary-color)"><DocumentCopy /></el-icon>
            <span>规则列表</span>
          </div>
        </div>
      </template>
      
      <el-table :data="rules" class="modern-table" stripe>
        <el-table-column prop="id" label="规则 ID" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <div style="display:flex;align-items:center;gap:8px">
              <el-icon style="color: var(--primary-color)"><Setting /></el-icon>
              <span style="font-family: monospace; font-size: 12px">{{ row.id }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="规则名称" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span style="font-weight: 500">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="row.type === 'builtin' ? 'success' : 'warning'" size="small" effect="dark">
              <el-icon><component :is="row.type === 'builtin' ? 'Lock' : 'EditPen'" /></el-icon>
              <span>{{ row.type === 'builtin' ? '内置' : '自定义' }}</span>
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="风险等级" width="120" align="center">
          <template #default="{ row }">
            <risk-badge :level="row.level" />
          </template>
        </el-table-column>
        <el-table-column prop="pattern" label="匹配模式" min-width="250" show-overflow-tooltip>
          <template #default="{ row }">
            <code class="pattern-code">{{ row.pattern }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="240" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewRule(row)">
              <el-icon><View /></el-icon>
              <span>查看</span>
            </el-button>
            <el-button 
              v-if="row.type === 'custom'" 
              type="warning" 
              link 
              size="small" 
              @click="editRule(row)"
            >
              <el-icon><Edit /></el-icon>
              <span>编辑</span>
            </el-button>
            <el-popconfirm
              v-if="row.type === 'custom'"
              title="确定删除此规则吗？"
              confirm-button-text="确定"
              cancel-button-text="取消"
              @confirm="deleteRule(row)"
            >
              <template #reference>
                <el-button type="danger" link size="small">
                  <el-icon><Delete /></el-icon>
                  <span>删除</span>
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      
      <el-empty v-if="!rules.length && !loading" description="暂无规则" :image-size="120">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><CirclePlusFilled /></el-icon>
          <span>创建第一条规则</span>
        </el-button>
      </el-empty>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog 
      v-model="showCreateDialog" 
      :title="editingRule ? '编辑规则' : '创建规则'"
      width="700px"
      class="rule-dialog"
    >
      <el-form :model="ruleForm" label-width="120px" class="rule-form">
        <el-form-item label="规则 ID" required v-if="!editingRule">
          <el-input v-model="ruleForm.id" placeholder="例如: detect_eval" />
          <div class="form-tip">唯一标识符，创建后不可修改</div>
        </el-form-item>
        <el-form-item label="规则名称" required>
          <el-input v-model="ruleForm.title" placeholder="例如: 禁用 eval 函数" />
        </el-form-item>
        <el-form-item label="匹配模式" required>
          <el-input v-model="ruleForm.pattern" placeholder="正则表达式，例如: eval\\s*\\(" />
          <div class="form-tip">使用正则表达式匹配代码内容</div>
        </el-form-item>
        <el-form-item label="风险等级" required>
          <el-select v-model="ruleForm.level" style="width:100%">
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
        <el-form-item label="描述">
          <el-input 
            v-model="ruleForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="规则详细描述，说明检测目标和风险影响" 
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveRule" :loading="submitting">
          <el-icon><Check /></el-icon>
          <span>{{ editingRule ? '更新' : '创建' }}</span>
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看规则详情对话框 -->
    <el-dialog v-model="showViewDialog" title="规则详情" width="700px" class="rule-dialog">
      <el-descriptions :column="1" border v-if="viewingRule" class="rule-descriptions">
        <el-descriptions-item label="规则 ID">
          <code>{{ viewingRule.id }}</code>
        </el-descriptions-item>
        <el-descriptions-item label="规则名称">{{ viewingRule.title }}</el-descriptions-item>
        <el-descriptions-item label="类型">
          <el-tag :type="viewingRule.type === 'builtin' ? 'success' : 'warning'" size="small" effect="dark">
            {{ viewingRule.type === 'builtin' ? '内置' : '自定义' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="风险等级">
          <risk-badge :level="viewingRule.level" />
        </el-descriptions-item>
        <el-descriptions-item label="匹配模式">
          <code class="pattern-code">{{ viewingRule.pattern }}</code>
        </el-descriptions-item>
        <el-descriptions-item label="描述">
          {{ viewingRule.description || '-' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  CirclePlusFilled, Grid, Lock, EditPen, DocumentCopy, 
  Setting, View, Edit, Delete, Check 
} from '@element-plus/icons-vue'
import RiskBadge from '../components/RiskBadge.vue'
import api from '../api/request'

const rules = ref<any[]>([])
const loading = ref(false)
const ruleType = ref('')
const showCreateDialog = ref(false)
const showViewDialog = ref(false)
const submitting = ref(false)
const editingRule = ref<any>(null)
const viewingRule = ref<any>(null)

const ruleForm = ref({
  id: '',
  title: '',
  pattern: '',
  level: 'medium',
  description: ''
})

const fetchRules = async () => {
  loading.value = true
  try {
    const params = ruleType.value ? { rule_type: ruleType.value } : {}
    const res: any = await api.get('/rules', { params })
    const data = res.data || res
    rules.value = data.rules || []
  } catch (e) {
    console.error('Failed to fetch rules:', e)
    rules.value = []
  } finally {
    loading.value = false
  }
}

const viewRule = (rule: any) => {
  viewingRule.value = rule
  showViewDialog.value = true
}

const editRule = (rule: any) => {
  editingRule.value = rule
  ruleForm.value = {
    id: rule.id,
    title: rule.title,
    pattern: rule.pattern,
    level: rule.level,
    description: rule.description || ''
  }
  showCreateDialog.value = true
}

const saveRule = async () => {
  // 验证必填字段
  if (!editingRule.value && !ruleForm.value.id) {
    ElMessage.warning('请输入规则 ID')
    return
  }
  if (!ruleForm.value.title) {
    ElMessage.warning('请输入规则名称')
    return
  }
  if (!ruleForm.value.pattern) {
    ElMessage.warning('请输入匹配模式')
    return
  }
  
  submitting.value = true
  try {
    if (editingRule.value) {
      // 更新规则
      await api.put(`/rules/${editingRule.value.id}`, {
        title: ruleForm.value.title,
        pattern: ruleForm.value.pattern,
        level: ruleForm.value.level,
        description: ruleForm.value.description
      })
      ElMessage.success('规则更新成功')
    } else {
      // 创建规则
      await api.post('/rules', ruleForm.value)
      ElMessage.success('规则创建成功')
    }
    
    showCreateDialog.value = false
    resetForm()
    fetchRules()
  } catch (e: any) {
    const errorMsg = e?.response?.data?.detail || '操作失败'
    ElMessage.error(errorMsg)
    console.error('Save rule failed:', e)
  } finally {
    submitting.value = false
  }
}

const deleteRule = async (rule: any) => {
  try {
    await api.delete(`/rules/${rule.id}`)
    ElMessage.success('规则删除成功')
    fetchRules()
  } catch (e: any) {
    const errorMsg = e?.response?.data?.detail || '删除失败'
    ElMessage.error(errorMsg)
    console.error('Delete rule failed:', e)
  }
}

const resetForm = () => {
  editingRule.value = null
  ruleForm.value = {
    id: '',
    title: '',
    pattern: '',
    level: 'medium',
    description: ''
  }
}

onMounted(() => { fetchRules() })
</script>

<style scoped>
.rules-page {
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

.filter-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-left {
  flex: 1;
}

.type-filter :deep(.el-radio-button) {
  margin-right: 8px;
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

.pattern-code {
  background: #f1f5f9;
  padding: 4px 8px;
  border-radius: 6px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 12px;
  color: var(--text-primary);
}

.rule-dialog :deep(.el-dialog) {
  border-radius: 20px;
}

.rule-form {
  padding: 8px 0;
}

.form-tip {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
  line-height: 1.5;
}

.rule-descriptions {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
  width: 120px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .filter-content {
    flex-direction: column;
    gap: 16px;
  }
}
</style>
