// 本文件说明：报告模块接口封装，供报告页预览和导出按钮调用。
import { apiClient } from './client'

export const fetchReport = (id: string) => apiClient.get(`/reports/${id}`)
