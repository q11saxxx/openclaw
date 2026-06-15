<template>
  <div class="report-compare fade-in">
    <div class="page-header">
      <el-page-header @back="router.back()">
        <template #content>
          <div class="header-block">
            <span class="header-title">双报告对比</span>
            <span class="header-sub">并排查看两份审计结论与差异发现（创新视图，不修改原始报告）</span>
          </div>
        </template>
      </el-page-header>
    </div>

    <el-alert type="info" :closable="false" show-icon class="tip">
      适合同一技能包升级前后、或不同版本包的横向对比。差异按「标题+来源」近似匹配，仅供参考。
    </el-alert>

    <div v-loading="loading" class="compare-body">
      <template v-if="left && right">
        <el-row :gutter="20" class="summary-row">
          <el-col :xs="24" :md="12">
            <el-card shadow="hover" class="side-card left">
              <template #header>
                <span class="card-title">报告一（左侧）</span>
                <el-button type="primary" link size="small" @click="goReport(leftId)">打开详情</el-button>
              </template>
              <p class="mono-id">{{ leftId }}</p>
              <p><strong>技能包名称</strong> {{ meta(left).skill_name || '-' }}</p>
              <p>
                <strong>风险</strong>
                <risk-badge :level="riskOf(left)" style="margin-left: 8px" />
              </p>
              <p><strong>综合安全分</strong> {{ scoreLeft }}</p>
              <p><strong>发现数</strong> {{ findings(left).length }}</p>
            </el-card>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-card shadow="hover" class="side-card right">
              <template #header>
                <span class="card-title">报告二（右侧）</span>
                <el-button type="primary" link size="small" @click="goReport(rightId)">打开详情</el-button>
              </template>
              <p class="mono-id">{{ rightId }}</p>
              <p><strong>技能包名称</strong> {{ meta(right).skill_name || '-' }}</p>
              <p>
                <strong>风险</strong>
                <risk-badge :level="riskOf(right)" style="margin-left: 8px" />
              </p>
              <p><strong>综合安全分</strong> {{ scoreRight }}</p>
              <p><strong>发现数</strong> {{ findings(right).length }}</p>
            </el-card>
          </el-col>
        </el-row>

        <el-card shadow="hover" class="dim-card">
          <template #header>多维度得分对比</template>
          <el-table :data="dimCompareRows" border stripe size="small">
            <el-table-column prop="name" label="维度" min-width="140" />
            <el-table-column prop="scoreA" label="报告一得分" width="100" align="center" />
            <el-table-column prop="scoreB" label="报告二得分" width="100" align="center" />
            <el-table-column label="差值（一减二）" width="110" align="center">
              <template #default="{ row }">
                <span :class="deltaClass(row.delta)">{{ row.delta > 0 ? '+' : '' }}{{ row.delta }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-row :gutter="20" class="diff-row">
          <el-col :xs="24" :md="12">
            <el-card shadow="hover">
              <template #header>
                <span>仅在报告一中的发现</span>
                <el-tag size="small" type="warning">{{ onlyInLeft.length }}</el-tag>
              </template>
              <ul class="diff-list">
                <li v-for="(t, i) in onlyInLeftTitles" :key="'l'+i">{{ t }}</li>
                <li v-if="!onlyInLeft.length" class="muted">无独有项</li>
              </ul>
            </el-card>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-card shadow="hover">
              <template #header>
                <span>仅在报告二中的发现</span>
                <el-tag size="small" type="warning">{{ onlyInRight.length }}</el-tag>
              </template>
              <ul class="diff-list">
                <li v-for="(t, i) in onlyInRightTitles" :key="'r'+i">{{ t }}</li>
                <li v-if="!onlyInRight.length" class="muted">无独有项</li>
              </ul>
            </el-card>
          </el-col>
        </el-row>
      </template>

      <el-empty v-else-if="!loading" description="请从报告列表选择两条记录发起对比" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getReport } from '../../api/report'
import RiskBadge from '../../components/RiskBadge.vue'
import { buildDimensionRows, compositeScoreFromFindings } from '../../utils/reportMultiDimScore'

const route = useRoute()
const router = useRouter()

const leftId = computed(() => String(route.query.left || ''))
const rightId = computed(() => String(route.query.right || ''))

const loading = ref(false)
const left = ref<any>(null)
const right = ref<any>(null)

const findings = (raw: any) => (raw?.findings || []) as any[]
const meta = (raw: any) => raw?.metadata || {}
const summary = (raw: any) => raw?.summary || raw || {}

const riskOf = (raw: any) => {
  const s = summary(raw)
  return String(s.risk_level || s.level || '').toLowerCase()
}

const scoreLeft = computed(() => compositeScoreFromFindings(findings(left.value)))
const scoreRight = computed(() => compositeScoreFromFindings(findings(right.value)))

const dimCompareRows = computed(() => {
  const rowsA = buildDimensionRows(findings(left.value))
  const rowsB = buildDimensionRows(findings(right.value))
  return rowsA.map((ra, i) => {
    const rb = rowsB[i]
    return {
      name: ra.name,
      scoreA: ra.score,
      scoreB: rb?.score ?? 0,
      delta: ra.score - (rb?.score ?? 0)
    }
  })
})

const findingSig = (f: any) =>
  `${String(f.agent || '')}|||${String(f.title || f.reason || '')
    .trim()
    .toLowerCase()
    .slice(0, 220)}`

const onlyInLeft = computed(() => {
  const la = findings(left.value)
  const ra = findings(right.value)
  const rs = new Set(ra.map(findingSig))
  return la.filter((f) => !rs.has(findingSig(f)))
})

const onlyInRight = computed(() => {
  const la = findings(left.value)
  const ra = findings(right.value)
  const ls = new Set(la.map(findingSig))
  return ra.filter((f) => !ls.has(findingSig(f)))
})

const onlyInLeftTitles = computed(() =>
  onlyInLeft.value.map((f) => f.title || f.reason || findingSig(f)).slice(0, 80)
)
const onlyInRightTitles = computed(() =>
  onlyInRight.value.map((f) => f.title || f.reason || findingSig(f)).slice(0, 80)
)

const deltaClass = (d: number) => {
  if (d > 3) return 'delta-up'
  if (d < -3) return 'delta-down'
  return 'delta-flat'
}

const goReport = (rid: string) => router.push({ name: 'ReportDetail', params: { id: rid } })

const load = async () => {
  const a = leftId.value
  const b = rightId.value
  if (!a || !b || a === b) {
    left.value = null
    right.value = null
    return
  }
  loading.value = true
  try {
    const [la, ra] = await Promise.all([getReport(a), getReport(b)])
    left.value = la as any
    right.value = ra as any
  } catch (e) {
    console.error(e)
    ElMessage.error('加载报告失败')
    left.value = null
    right.value = null
  } finally {
    loading.value = false
  }
}

onMounted(() => load())
watch([leftId, rightId], () => load())
</script>

<style scoped>
.report-compare {
  padding: 0;
}

.page-header {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--border-color);
}

.header-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.header-title {
  font-size: 20px;
  font-weight: 700;
}

.header-sub {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 400;
}

.tip {
  margin-bottom: 20px;
  border-radius: 10px;
}

.compare-body {
  min-height: 200px;
}

.summary-row {
  margin-bottom: 20px;
}

.side-card :deep(.el-card__header) {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-weight: 600;
}

.mono-id {
  font-family: monospace;
  font-size: 11px;
  color: var(--text-muted);
  word-break: break-all;
}

.dim-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.diff-row {
  margin-bottom: 24px;
}

.diff-list {
  margin: 0;
  padding-left: 18px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-primary);
}

.diff-list .muted {
  list-style: none;
  margin-left: -18px;
  color: var(--text-muted);
}

.delta-up {
  color: #67c23a;
  font-weight: 600;
}
.delta-down {
  color: #f56c6c;
  font-weight: 600;
}
.delta-flat {
  color: var(--text-secondary);
}
</style>
