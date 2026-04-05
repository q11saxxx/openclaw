<template>
  <div>
    <el-card>
      <h3>Skill 详情</h3>
      <div style="margin-bottom:8px">
        <el-button type="primary" @click="startAudit">开始审计</el-button>
      </div>
      <p><strong>ID:</strong> {{ id }}</p>
      <p v-if="skill.name"><strong>名称:</strong> {{ skill.name }}</p>
      <p v-if="skill.filename"><strong>文件名:</strong> {{ skill.filename }}</p>
      <p v-if="skill.size"><strong>大小:</strong> {{ (skill.size/1024).toFixed(1) }} KB</p>
      <p v-if="skill.sha256"><strong>SHA256:</strong> {{ skill.sha256 }}</p>
      <p v-if="skill.created_at"><strong>上传时间:</strong> {{ skill.created_at }}</p>

      <div style="margin-top:12px">
        <h4>Manifest / 元数据</h4>
        <pre>{{ manifest }}</pre>
      </div>

      <div style="margin-top:12px">
        <h4>快速检测（Quick Check）</h4>
        <div v-if="quick_check">
          <p><strong>风险等级:</strong> {{ quick_check.level }}</p>
          <p><strong>发现总数:</strong> {{ quick_check.summary?.script?.total_findings || quick_check.findings?.length || 0 }}</p>
          <el-button size="small" @click="showQuick=true">查看快速检测证据</el-button>
        </div>
        <div v-else>
          <p>未执行快速检测或检测尚未完成。</p>
        </div>
        <el-dialog v-model:visible="showQuick" title="快速检测证据" width="70%">
          <pre style="max-height:60vh;overflow:auto">{{ JSON.stringify(quick_check, null, 2) }}</pre>
          <template #footer>
            <el-button @click="showQuick=false">关闭</el-button>
          </template>
        </el-dialog>
      </div>

      <div style="margin-top:12px">
        <h4>审计报告</h4>
        <div v-if="reports && reports.length">
          <el-table :data="reports" style="width:100%">
            <el-table-column prop="id" label="报告 ID" />
            <el-table-column prop="created_at" label="生成时间" />
            <el-table-column label="操作">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="viewReport(row.id)">查看</el-button>
                <el-button size="small" @click="downloadReport(row.id, 'md')">下载 MD</el-button>
                <el-button size="small" @click="downloadReport(row.id, 'json')">下载 JSON</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div v-else>
          <p>尚无可用报告（审计未运行或尚未完成）。</p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getSkill } from '../../api/skill'
import { exportReport } from '../../api/report'
import { runAudit } from '../../api/audit'

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
    const res = await getSkill(id)
    skill.value = res || {}
    manifest.value = res?.parsed?.parsed?.manifest ? JSON.stringify(res.parsed.parsed.manifest, null, 2) : (res?.parsed?.manifest ? JSON.stringify(res.parsed.manifest, null, 2) : JSON.stringify(res, null, 2))
    reports.value = res?.reports || []
    quick_check.value = res?.quick_check || null
  } catch (e) {
    manifest.value = '无法获取详情'
  }
})

const viewReport = (rid: string) => {
  router.push(`/report/${rid}`)
}

const downloadReport = async (rid: string, format: string) => {
  try {
    const blob = await exportReport(rid, format)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${rid}.${format === 'md' ? 'md' : 'json'}`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    // ignore
  }
}

const startAudit = async () => {
  try {
    const res = await runAudit({ skill_id: id, options: { semantic: true } })
    const auditId = res.audit_id || res.id
    if (auditId) router.push(`/audit/${auditId}/progress`)
  } catch (e) {
    // ignore
  }
}
</script>
