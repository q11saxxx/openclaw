import api from './request'

export const runAudit = (payload: any) => api.post('/audits/run', payload)
export const getAuditStatus = (id: string) => api.get(`/audits/${id}`)
export const listAudits = (params: any) => api.get('/audits', { params })

// 统计分析相关接口
export const getAuditTrends = (days: number = 30) => api.get('/statistics/trends', { params: { days } })
export const getSkillComparison = (skillName: string) => api.get(`/statistics/skill-comparison/${skillName}`)
export const getInsights = () => api.get('/statistics/insights')
