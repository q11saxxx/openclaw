// 本文件说明：项目状态仓库，后续集中管理项目列表和筛选状态。
import { defineStore } from 'pinia'

export const useProjectStore = defineStore('project', {
  state: () => ({
    items: [] as Array<Record<string, unknown>>
  })
})
