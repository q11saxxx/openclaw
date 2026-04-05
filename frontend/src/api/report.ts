import api from './request'

export const getReport = (id: string) => api.get(`/reports/${id}`)
export const exportReport = (id: string, format = 'json') => api.get(`/reports/${id}/export`, { params: { format }, responseType: 'blob' })
