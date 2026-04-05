import api from './request'

export const runAudit = (payload: any) => api.post('/audits/run', payload)
export const getAuditStatus = (id: string) => api.get(`/audits/${id}`)
export const listAudits = (params: any) => api.get('/audits', { params })
