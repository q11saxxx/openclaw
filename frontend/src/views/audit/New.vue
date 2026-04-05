<template>
  <div>
    <h3>发起审计</h3>
    <el-form :model="form">
      <el-form-item label="选择 Skill">
        <el-select v-model="form.skill_id" placeholder="选择 Skill">
          <el-option v-for="s in skills" :key="s.id" :label="s.name || s.filename" :value="s.id" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-switch v-model="form.semantic" active-text="启用语义审计" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="start">开始审计</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { runAudit } from '../../api/audit'
import { useRouter } from 'vue-router'
import { useSkillStore } from '../../stores/skill'

const router = useRouter()
const store = useSkillStore()
const form = ref({ skill_id: '', semantic: true })
const skills = ref<any[]>([])

onMounted(async () => {
  await store.fetchSkills({ page: 1, size: 50 })
  skills.value = store.skills
})

const start = async () => {
  try {
    const res = await runAudit({ skill_id: form.value.skill_id, options: { semantic: form.value.semantic } })
    const auditId = res.audit_id || res.id
    if (auditId) router.push(`/audit/${auditId}/progress`)
  } catch (e) {
    // ignore
  }
}
</script>
