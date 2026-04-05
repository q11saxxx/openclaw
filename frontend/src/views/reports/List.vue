<template>
  <div>
    <h3>报告列表</h3>
    <el-table :data="reports">
      <el-table-column prop="id" label="ID" />
      <el-table-column prop="metadata.skill_name" label="Skill" />
      <el-table-column prop="summary.level" label="Level" />
      <el-table-column prop="summary.confidence" label="Confidence" />
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button size="small" @click="view(row.id)">查看</el-button>
          <el-button size="small" @click="download(row.id)">下载</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { listAudits } from '../../api/audit'
import { useRouter } from 'vue-router'

const reports = ref<any[]>([])
const router = useRouter()

const fetch = async () => {
  try {
    const res = await listAudits({})
    reports.value = res.items || []
  } catch (e) {
    reports.value = []
  }
}

const view = (id: string) => router.push(`/report/${id}`)
const download = async (id: string) => {
  // use existing export API
  import('../../api/report').then(({ exportReport }) => exportReport(id, 'json'))
}

onMounted(() => { fetch() })
</script>
