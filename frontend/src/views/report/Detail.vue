<template>
  <div>
    <h3>报告详情</h3>
    <div v-if="summary">
      <el-card>
        <div style="display:flex;align-items:center;justify-content:space-between">
          <div>
            <h2>{{ summary.level || '未知' }}</h2>
            <p>置信度: {{ summary.confidence || 0 }}%</p>
          </div>
          <div>
            <el-button @click="download('md')">导出 MD</el-button>
            <el-button @click="download('json')">导出 JSON</el-button>
          </div>
        </div>
      </el-card>
      <div style="margin-top:12px">
        <h4>风险分布</h4>
        <!-- ECharts 占位 -->
      </div>
      <div style="margin-top:12px">
        <h4>详细风险列表</h4>
        <el-collapse>
          <el-collapse-item v-for="(f,i) in findings" :key="i" :title="f.title">
            <div>
              <p>{{ f.description }}</p>
              <code-highlight :content="f.evidence || ''" />
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getReport, exportReport } from '../../api/report'
import CodeHighlight from '../../components/CodeHighlight.vue'

const route = useRoute()
const id = route.params.id as string
const summary = ref<any>(null)
const findings = ref<any[]>([])

onMounted(async () => {
  try {
    const res = await getReport(id)
    summary.value = res.summary || res
    findings.value = res.findings || []
  } catch (e) {
    // ignore
  }
})

const download = async (format: string) => {
  try {
    const blob = await exportReport(id, format)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `report_${id}.${format === 'md' ? 'md' : 'json'}`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    // ignore
  }
}
</script>
