// 本文件说明：扫描状态仓库，后续保存当前任务详情和风险统计。"""
import { defineStore } from 'pinia'

export const useScanStore = defineStore('scan', {
  state: () => ({
    current: null as Record<string, unknown> | null
  })
})
