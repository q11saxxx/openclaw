<template>
  <div>
    <el-steps :active="active" finish-status="success" align-center>
      <el-step title="解析中" description="技能包结构解析" />
      <el-step title="静态扫描" description="安全规则检测" />
      <el-step title="语义审计" description="大模型智能分析" />
      <el-step title="来源分析" description="依赖与来源验证" />
      <el-step title="决策评估" description="风险等级评定" />
      <el-step title="报告生成" description="审计报告生成" />
    </el-steps>
    
    <div style="margin-top:24px">
      <el-card>
        <template #header>
          <div style="display:flex;justify-content:space-between;align-items:center">
            <span>审计日志</span>
            <el-tag v-if="completed" type="success">已完成</el-tag>
            <el-tag v-else type="warning">进行中</el-tag>
          </div>
        </template>
        <pre 
          style="background:#1e1e1e;color:#d4d4d4;padding:16px;border-radius:6px;height:300px;overflow:auto;font-size:13px;line-height:1.6;margin:0"
        >{{ props.logs || '等待审计开始...' }}</pre>
      </el-card>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue'

const props = defineProps<{ 
  stage?: number
  logs?: string
  completed?: boolean
}>()

const active = computed(() => (props.stage || 0) + 1)
</script>
