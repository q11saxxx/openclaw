<template>
  <div class="statistics-container fade-in">
    <el-alert 
      title="使用说明" 
      type="info" 
      :closable="false"
      show-icon
    >
      <template #default>
        <p>本页展示审计历史分布、频率与趋势；下方可输入技能包名称，对比同一技能多次审计结果。</p>
        <p>当前时间：{{ currentTime }}</p>
      </template>
    </el-alert>

    <div class="page-header">
      <div>
        <h1 class="page-title">审计统计分析</h1>
        <p class="page-subtitle">可视化展示审计历史趋势与智能洞察</p>
      </div>
      <el-button-group>
        <el-button :type="period === 7 ? 'primary' : 'default'" @click="changePeriod(7)">7天</el-button>
        <el-button :type="period === 30 ? 'primary' : 'default'" @click="changePeriod(30)">30天</el-button>
        <el-button :type="period === 90 ? 'primary' : 'default'" @click="changePeriod(90)">90天</el-button>
      </el-button-group>
    </div>

    <!-- 智能洞察卡片 -->
    <el-row :gutter="20" class="insights-section">
      <el-col :span="24">
        <el-card class="insights-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon :size="20" style="margin-right: 8px; color: var(--primary-color)"><Lightning /></el-icon>
              <span>智能洞察</span>
            </div>
          </template>
          <el-row :gutter="16">
            <el-col 
              v-for="(insight, index) in insights" 
              :key="index" 
              :xs="24" 
              :sm="12" 
              :md="8"
              :lg="6"
            >
              <div class="insight-item" :class="insight.type">
                <el-icon :size="32" class="insight-icon">
                  <component :is="getInsightIcon(insight.icon)" />
                </el-icon>
                <div class="insight-content">
                  <h4>{{ insight.title }}</h4>
                  <p>{{ insight.message }}</p>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <!-- 风险等级分布饼图 -->
    <el-row :gutter="20" class="charts-section">
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <el-icon :size="20" style="margin-right: 8px; color: var(--primary-color)"><PieChart /></el-icon>
              <span>风险等级分布</span>
            </div>
          </template>
          <div ref="severityChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <!-- 审计频率柱状图 -->
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <el-icon :size="20" style="margin-right: 8px; color: var(--primary-color)"><Histogram /></el-icon>
              <span>审计频率统计</span>
            </div>
          </template>
          <div ref="frequencyChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 趋势折线图 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <el-icon :size="20" style="margin-right: 8px; color: var(--primary-color)"><TrendCharts /></el-icon>
              <span>风险趋势分析（过去{{ period }}天）</span>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container-large"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 技能包版本对比查询 -->
    <el-row :gutter="20" class="comparison-section">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon :size="20" style="margin-right: 8px; color: var(--primary-color)"><Connection /></el-icon>
              <span>技能包版本对比</span>
            </div>
          </template>
          
          <el-form :inline="true" class="comparison-form">
            <el-form-item label="技能包名称">
              <el-input 
                v-model="comparisonSkillName" 
                placeholder="输入技能包名称" 
                style="width: 300px"
                clearable
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadComparison" :loading="comparisonLoading">
                <el-icon><Search /></el-icon>
                <span>查询对比</span>
              </el-button>
            </el-form-item>
          </el-form>

          <div v-if="comparisonData" class="comparison-result">
            <el-alert
              v-if="comparisonData.total_audits !== undefined"
              :title="`共找到 ${comparisonData.total_audits} 次审计记录`"
              :type="getTrendType(comparisonData.trend)"
              :closable="false"
              show-icon
              class="trend-alert"
            >
              <template #default>
                <p>风险趋势：{{ getTrendText(comparisonData.trend || 'unknown') }}</p>
              </template>
            </el-alert>
            <el-alert
              v-else
              title="未找到该技能包的审计记录"
              type="info"
              :closable="false"
              show-icon
              class="trend-alert"
            >
              <template #default>
                <p>请检查技能包名称是否正确，或尝试使用更短的关键词进行搜索</p>
              </template>
            </el-alert>

            <el-table v-if="comparisonData.versions && comparisonData.versions.length > 0" :data="comparisonData.versions" class="modern-table" stripe max-height="400">
              <el-table-column prop="version" label="版本" width="120" />
              <el-table-column prop="created_at" label="审计时间" width="180">
                <template #default="{ row }">
                  {{ formatTime(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="风险等级" width="120" align="center">
                <template #default="{ row }">
                  <risk-badge :level="row.risk_level" />
                </template>
              </el-table-column>
              <el-table-column label="置信度" width="120" align="center">
                <template #default="{ row }">
                  <span>{{ Math.round(row.confidence * 100) }}%</span>
                </template>
              </el-table-column>
              <el-table-column label="发现数量" width="120" align="center">
                <template #default="{ row }">
                  <el-tag size="small">{{ row.finding_count }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150" align="center">
                <template #default="{ row }">
                  <el-button 
                    type="primary" 
                    link 
                    size="small" 
                    @click="$router.push(`/report/${row.audit_id}`)"
                  >
                    查看报告
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-empty 
              v-else 
              description="该技能包暂无历史审计记录" 
              :image-size="100"
              style="padding: 20px 0;"
            />
          </div>

          <el-empty 
            v-else-if="!comparisonLoading" 
            description="请输入技能包名称以查询历史审计对比" 
            :image-size="100"
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { getAuditTrends, getInsights, getSkillComparison } from '../api/audit'
import RiskBadge from '../components/RiskBadge.vue'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'
import { 
  Lightning, PieChart, Histogram, TrendCharts, Search,
  Connection, Warning, SuccessFilled, InfoFilled
} from '@element-plus/icons-vue'

const period = ref(30)
const loading = ref(false)
const comparisonLoading = ref(false)
const comparisonSkillName = ref('')
const comparisonData = ref<any>(null)
const insights = ref<any[]>([])
const currentTime = ref(new Date().toLocaleString('zh-CN'))

const severityChartRef = ref<HTMLElement>()
const frequencyChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()

let severityChart: ECharts | null = null
let frequencyChart: ECharts | null = null
let trendChart: ECharts | null = null

// 加载趋势数据
const loadTrends = async () => {
  loading.value = true
  try {
    const res: any = await getAuditTrends(period.value)
    if (res.success && res.data) {
      renderSeverityChart(res.data.severity_distribution)
      renderFrequencyChart(res.data.trend_data)
      renderTrendChart(res.data.trend_data)
    }
  } catch (e) {
    console.error('Failed to load trends:', e)
  } finally {
    loading.value = false
  }
}

// 加载洞察
const loadInsights = async () => {
  try {
    const res: any = await getInsights()
    if (res.success && res.data) {
      insights.value = res.data.insights || []
    }
  } catch (e) {
    console.error('Failed to load insights:', e)
  }
}

// 加载Skill对比
const loadComparison = async () => {
  if (!comparisonSkillName.value.trim()) {
    return
  }
  
  comparisonLoading.value = true
  try {
    const res: any = await getSkillComparison(comparisonSkillName.value.trim())
    if (res.success && res.data) {
      comparisonData.value = res.data
    } else {
      comparisonData.value = null
    }
  } catch (e) {
    console.error('Failed to load comparison:', e)
    comparisonData.value = null
  } finally {
    comparisonLoading.value = false
  }
}

// 切换统计周期
const changePeriod = (days: number) => {
  period.value = days
  loadTrends()
}

// 渲染风险等级分布饼图
const renderSeverityChart = (distribution: any) => {
  if (!severityChartRef.value) return
  
  if (!severityChart) {
    severityChart = echarts.init(severityChartRef.value)
  }

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center'
    },
    series: [
      {
        name: '风险等级',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{c}'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: [
          { value: distribution.critical || 0, name: '严重', itemStyle: { color: '#f56c6c' } },
          { value: distribution.high || 0, name: '高危', itemStyle: { color: '#e6a23c' } },
          { value: distribution.medium || 0, name: '中危', itemStyle: { color: '#409eff' } },
          { value: distribution.low || 0, name: '低危', itemStyle: { color: '#67c23a' } }
        ]
      }
    ]
  }

  severityChart.setOption(option)
}

// 渲染审计频率柱状图
const renderFrequencyChart = (trendData: any[]) => {
  if (!frequencyChartRef.value) return
  
  if (!frequencyChart) {
    frequencyChart = echarts.init(frequencyChartRef.value)
  }

  const dates = trendData.map(item => item.date.slice(5)) // 只显示月-日
  const totals = trendData.map(item => item.total)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '审计次数'
    },
    series: [
      {
        name: '审计次数',
        type: 'bar',
        data: totals,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ])
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#764ba2' },
              { offset: 1, color: '#667eea' }
            ])
          }
        }
      }
    ]
  }

  frequencyChart.setOption(option)
}

// 渲染趋势折线图
const renderTrendChart = (trendData: any[]) => {
  if (!trendChartRef.value) return
  
  if (!trendChart) {
    trendChart = echarts.init(trendChartRef.value)
  }

  const dates = trendData.map(item => item.date.slice(5))
  const critical = trendData.map(item => item.critical)
  const high = trendData.map(item => item.high)
  const medium = trendData.map(item => item.medium)
  const low = trendData.map(item => item.low)

  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['严重', '高危', '中危', '低危']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '数量'
    },
    series: [
      {
        name: '严重',
        type: 'line',
        stack: 'Total',
        data: critical,
        smooth: true,
        lineStyle: { width: 3 },
        areaStyle: { opacity: 0.3 },
        itemStyle: { color: '#f56c6c' }
      },
      {
        name: '高危',
        type: 'line',
        stack: 'Total',
        data: high,
        smooth: true,
        lineStyle: { width: 3 },
        areaStyle: { opacity: 0.3 },
        itemStyle: { color: '#e6a23c' }
      },
      {
        name: '中危',
        type: 'line',
        stack: 'Total',
        data: medium,
        smooth: true,
        lineStyle: { width: 3 },
        areaStyle: { opacity: 0.3 },
        itemStyle: { color: '#409eff' }
      },
      {
        name: '低危',
        type: 'line',
        stack: 'Total',
        data: low,
        smooth: true,
        lineStyle: { width: 3 },
        areaStyle: { opacity: 0.3 },
        itemStyle: { color: '#67c23a' }
      }
    ]
  }

  trendChart.setOption(option)
}

// 获取洞察图标
const getInsightIcon = (iconName: string) => {
  const iconMap: any = {
    'TrendCharts': TrendCharts,
    'Warning': Warning,
    'SuccessFilled': SuccessFilled,
    'InfoFilled': InfoFilled
  }
  return iconMap[iconName] || TrendCharts
}

// 获取趋势类型
const getTrendType = (trend: string) => {
  const typeMap: any = {
    'improving': 'success',
    'worsening': 'error',
    'stable': 'info',
    'unknown': 'info'
  }
  return typeMap[trend] || 'info'
}

// 获取趋势文本
const getTrendText = (trend: string) => {
  const textMap: any = {
    'improving': '📈 风险状况正在改善',
    'worsening': '⚠️ 风险状况有所恶化',
    'stable': '➡️ 风险状况保持稳定',
    'unknown': '❓ 数据不足，无法判断趋势'
  }
  return textMap[trend] || '未知趋势'
}

// 格式化时间
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

// 窗口resize时重绘图表
const handleResize = () => {
  severityChart?.resize()
  frequencyChart?.resize()
  trendChart?.resize()
}

onMounted(() => {
  loadTrends()
  loadInsights()
  window.addEventListener('resize', handleResize)
})

watch(period, () => {
  loadTrends()
})

// 组件卸载时清理
import { onUnmounted } from 'vue'
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  severityChart?.dispose()
  frequencyChart?.dispose()
  trendChart?.dispose()
})
</script>

<style scoped>
.statistics-container {
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

.insights-section {
  margin-bottom: 24px;
}

.insights-card {
  border-radius: 16px;
}

.insight-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 16px;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.insight-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.insight-item.info {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border-color: #2196f3;
}

.insight-item.warning {
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
  border-color: #ff9800;
}

.insight-item.success {
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  border-color: #4caf50;
}

.insight-item.error {
  background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
  border-color: #f44336;
}

.insight-icon {
  flex-shrink: 0;
}

.insight-content h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.insight-content p {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.charts-section {
  margin-bottom: 24px;
}

.chart-card {
  border-radius: 16px;
  height: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}

.chart-container {
  height: 350px;
  width: 100%;
}

.chart-container-large {
  height: 450px;
  width: 100%;
}

.comparison-section {
  margin-top: 24px;
}

.comparison-form {
  margin-bottom: 24px;
}

.comparison-result {
  margin-top: 20px;
}

.trend-alert {
  margin-bottom: 20px;
  border-radius: 8px;
}

.modern-table {
  border-radius: 12px;
}

.fade-in {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
