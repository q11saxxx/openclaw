// 本文件说明：扫描模块接口封装，供上传组件和任务页调用。
import { apiClient } from './client'

export const fetchScanDetail = (id: string) => apiClient.get(`/scans/${id}`)
