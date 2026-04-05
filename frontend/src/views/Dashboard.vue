<template>
  <div>
    <h2>Dashboard</h2>
    <div style="display:flex;gap:20px;margin-bottom:16px">
      <el-card style="flex:1">
        <h3>总 Skill 数</h3>
        <p style="font-size:24px">{{ totalSkills }}</p>
      </el-card>
      <el-card style="flex:1">
        <h3>审计报告数</h3>
        <p style="font-size:24px">{{ totalReports }}</p>
      </el-card>
    </div>

    <el-card>
      <h3>最近上传的 Skill</h3>
      <el-table :data="recentSkills">
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="filename" label="文件名" />
        <el-table-column prop="created_at" label="上传时间" />
      </el-table>
    </el-card>
    <div style="height:12px"></div>
    <el-card>
      <h3>最近报告</h3>
      <el-table :data="recentReports">
        <el-table-column prop="skill_name" label="Skill 名称" />
        <el-table-column prop="risk_level" label="风险等级" />
        <el-table-column prop="created_at" label="生成时间" />
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button size="small" @click="viewReport(row.id)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { useSkillStore } from '../stores/skill'
import { listAudits } from '../api/audit'
import { useRouter } from 'vue-router'

const store = useSkillStore()
const totalSkills = ref(0)
const totalReports = ref(0)
const recentSkills = ref([])
const recentReports = ref([])
const router = useRouter()

const fetch = async () => {
  await store.fetchSkills({ page: 1, size: 6 })
  totalSkills.value = store.total
  recentSkills.value = store.skills.slice(0, 6)

  const reps = await listAudits({})
  recentReports.value = reps.items ? reps.items.slice(0, 6) : (Array.isArray(reps) ? reps.slice(0,6) : [])
  totalReports.value = reps.total || (reps.items ? reps.items.length : recentReports.value.length)
}

const viewReport = (id: string) => router.push(`/report/${id}`)

onMounted(() => { fetch() })
</script>
