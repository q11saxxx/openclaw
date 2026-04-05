<template>
  <div>
    <h3>审计任务</h3>
    <el-table :data="tasks">
      <el-table-column prop="id" label="任务ID" />
      <el-table-column prop="skill_name" label="Skill 名称" />
      <el-table-column prop="status" label="状态" />
      <el-table-column prop="risk_level" label="风险等级" />
      <el-table-column prop="duration" label="耗时" />
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button size="small" @click="view(row.id)">查看进度</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { listAudits } from '../../api/audit'
import { useRouter } from 'vue-router'

const tasks = ref([])
const router = useRouter()

const fetch = async () => {
  const res = await listAudits({})
  tasks.value = res.items || res
}

const view = (id: string) => router.push(`/audit/${id}/progress`)

onMounted(() => { fetch() })
</script>
