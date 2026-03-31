// 本文件说明：扫描结果类型定义，供任务页和图表组件复用。
export interface ScanSummary {
  scan_id: string
  status: string
  high: number
  medium: number
  low: number
}
