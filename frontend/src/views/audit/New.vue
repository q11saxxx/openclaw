<template>
  <div class="new-audit fade-in">
    <div class="page-header">
      <div>
        <h1 class="page-title">发起审计</h1>
        <p class="page-subtitle">选择技能包进行安全审计分析</p>
      </div>
    </div>
    
    <el-row :gutter="24">
      <el-col :xs="24" :md="16" :lg="12">
        <el-card class="audit-form-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon :size="20" style="color: var(--primary-color)"><VideoPlay /></el-icon>
                <span>审计配置</span>
              </div>
            </div>
          </template>
          
          <el-form :model="form" class="audit-form">
            <el-form-item label="选择技能包" required>
              <el-select 
                v-model="form.skill_id" 
                placeholder="请选择要审计的技能包" 
                class="skill-select"
                filterable
                @change="onSkillChange"
              >
                <el-option 
                  v-for="s in skills" 
                  :key="s.id" 
                  :label="`${s.name || s.filename} (${s.version || '未知版本'})`" 
                  :value="s.id" 
                >
                  <div style="display:flex;align-items:center;gap:8px">
                    <el-icon style="color: var(--primary-color)"><Document /></el-icon>
                    <span>{{ s.name || s.filename }}</span>
                    <el-tag size="small" type="info" effect="plain">{{ s.version || '未知' }}</el-tag>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="基线对比（可选）">
              <el-select
                v-model="form.baseline_skill_id"
                placeholder="选择旧版或上一版技能包，用于目录/依赖差异分析"
                class="skill-select"
                filterable
                clearable
              >
                <el-option
                  v-for="s in baselineSkillOptions"
                  :key="s.id"
                  :label="`${s.name || s.filename} (${s.version || '未知版本'})`"
                  :value="s.id"
                >
                  <div style="display:flex;align-items:center;gap:8px">
                    <el-icon style="color: var(--el-color-info)"><Document /></el-icon>
                    <span>{{ s.name || s.filename }}</span>
                    <el-tag size="small" type="info" effect="plain">{{ s.version || '未知' }}</el-tag>
                  </div>
                </el-option>
              </el-select>
              <div class="field-hint">须与当前选中的技能包不同；后端会将基线包路径传入来源分析以做差异检测。</div>
            </el-form-item>
            
            <el-form-item label="审计选项">
              <div class="audit-options">
                <el-checkbox v-model="form.semantic" class="option-item">
                  <div class="option-content">
                    <div class="option-icon semantic">
                      <el-icon><MagicStick /></el-icon>
                    </div>
                    <div>
                      <div class="option-title">语义审计</div>
                      <div class="option-desc">使用大模型分析提示词注入等语义风险</div>
                    </div>
                  </div>
                </el-checkbox>
                <el-checkbox v-model="form.static_security" class="option-item">
                  <div class="option-content">
                    <div class="option-icon security">
                      <el-icon><Lock /></el-icon>
                    </div>
                    <div>
                      <div class="option-title">静态安全</div>
                      <div class="option-desc">检测危险命令、文件权限、敏感路径等</div>
                    </div>
                  </div>
                </el-checkbox>
                <el-checkbox v-model="form.dependency_check" class="option-item">
                  <div class="option-content">
                    <div class="option-icon dependency">
                      <el-icon><Connection /></el-icon>
                    </div>
                    <div>
                      <div class="option-title">依赖检查</div>
                      <div class="option-desc">分析依赖关系和第三方组件风险</div>
                    </div>
                  </div>
                </el-checkbox>
                <el-checkbox v-model="form.ai_preprocessing" class="option-item">
                  <div class="option-content">
                    <div class="option-icon semantic">
                      <el-icon><MagicStick /></el-icon>
                    </div>
                    <div>
                      <div class="option-title">AI 预处理</div>
                      <div class="option-desc">使用 AI 对大文件进行智能提炼和摘要，提高审计效率</div>
                    </div>
                  </div>
                </el-checkbox>
                <el-checkbox v-model="form.surface_intel" class="option-item">
                  <div class="option-content">
                    <div class="option-icon security">
                      <el-icon><Lock /></el-icon>
                    </div>
                    <div>
                      <div class="option-title">表面情报增强</div>
                      <div class="option-desc">扫描文本中的疑似密钥/令牌形态、外链与 file:// 暴露面（静态、确定性），默认开启</div>
                    </div>
                  </div>
                </el-checkbox>
              </div>
            </el-form-item>
            
            <el-form-item class="form-actions">
              <el-button 
                type="primary" 
                @click="start" 
                :loading="submitting"
                :disabled="!form.skill_id"
                size="large"
                class="submit-btn"
              >
                <el-icon><VideoPlay /></el-icon>
                <span>开始审计</span>
              </el-button>
              <el-button @click="$router.back()" size="large">取消</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :md="8" :lg="12">
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon :size="20" style="color: var(--primary-color)"><InfoFilled /></el-icon>
                <span>审计说明</span>
              </div>
            </div>
          </template>
          
          <div class="audit-info">
            <div class="info-item">
              <div class="info-icon">
                <el-icon><Timer /></el-icon>
              </div>
              <div class="info-content">
                <div class="info-title">审计时长</div>
                <div class="info-desc">通常 2～5 分钟，复杂技能包可能更长</div>
              </div>
            </div>
            
            <div class="info-item">
              <div class="info-icon">
                <el-icon><Setting /></el-icon>
              </div>
              <div class="info-content">
                <div class="info-title">审计内容</div>
                <div class="info-desc">静态分析、语义审计、依赖检查等多维度检测</div>
              </div>
            </div>
            
            <div class="info-item">
              <div class="info-icon">
                <el-icon><DocumentChecked /></el-icon>
              </div>
              <div class="info-content">
                <div class="info-title">审计报告</div>
                <div class="info-desc">自动生成详细的风险评估报告和改进建议</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue'
import { runAudit } from '../../api/audit'
import { useRouter } from 'vue-router'
import { useSkillStore } from '../../stores/skill'
import { ElMessage } from 'element-plus'
import { 
  VideoPlay, Document, MagicStick, Lock, Connection, 
  InfoFilled, Timer, Setting, DocumentChecked 
} from '@element-plus/icons-vue'

const router = useRouter()
const store = useSkillStore()

const form = ref({ 
  skill_id: '',
  baseline_skill_id: '' as string,
  semantic: true,
  static_security: true,
  dependency_check: true,
  ai_preprocessing: false,
  surface_intel: true
})

const baselineSkillOptions = computed(() =>
  skills.value.filter((s: any) => s.id && s.id !== form.value.skill_id)
)

const skills = ref<any[]>([])
const submitting = ref(false)

const onSkillChange = () => {
  if (form.value.baseline_skill_id === form.value.skill_id) {
    form.value.baseline_skill_id = ''
  }
}

onMounted(async () => {
  try {
    await store.fetchSkills({ page: 1, size: 100 })
    skills.value = store.skills
    console.log('Loaded skills:', skills.value)
  } catch (error) {
    console.error('Failed to load skills:', error)
    ElMessage.error('加载技能列表失败')
  }
})

const start = async () => {
  if (!form.value.skill_id) {
    ElMessage.warning('请选择要审计的技能')
    return
  }
  
  submitting.value = true
  try {
    const payload: Record<string, unknown> = {
      skill_id: form.value.skill_id,
      options: {
        semantic: form.value.semantic,
        static_security: form.value.static_security,
        dependency_check: form.value.dependency_check,
        ai_preprocessing: form.value.ai_preprocessing,
        surface_intel: form.value.surface_intel
      }
    }
    if (form.value.baseline_skill_id) {
      payload.baseline_skill_id = form.value.baseline_skill_id
    }
    const res: any = await runAudit(payload)
    const data = res.data || res
    const auditId = data.audit_id || data.report_id || data.id
    if (auditId) {
      ElMessage.success('审计任务已创建')
      router.push(`/audit/${auditId}/progress`)
    }
  } catch (e: any) {
    console.error('Audit failed:', e)
    ElMessage.error(e?.response?.data?.detail || '启动审计失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.new-audit {
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

.audit-form-card,
.info-card {
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

.audit-form {
  padding: 8px 0;
}

.skill-select {
  width: 100%;
}

.field-hint {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.audit-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.option-item {
  width: 100%;
  padding: 16px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  transition: all 0.3s;
  margin: 0 !important;
}

.option-item:hover {
  border-color: var(--primary-light);
  background: rgba(102, 126, 234, 0.02);
}

.option-item :deep(.el-checkbox__label) {
  width: 100%;
}

.option-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.option-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.option-icon.semantic {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.option-icon.security {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.option-icon.dependency {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.option-title {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.option-desc {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.form-actions {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.submit-btn {
  min-width: 140px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.audit-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: linear-gradient(135deg, rgba(248, 250, 252, 0.8) 0%, rgba(241, 245, 249, 0.8) 100%);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.info-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: var(--gradient-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.info-content {
  flex: 1;
}

.info-title {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
  font-size: 14px;
}

.info-desc {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}
</style>
