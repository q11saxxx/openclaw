import api from './request'

export const listSkills = (params: any) => api.get('/skills', { params })

export const uploadSkill = (file: File, runAudit = false) => {
    const form = new FormData()
    form.append('file', file)
    if (runAudit) form.append('run_audit', 'true')
    // Let the browser set the Content-Type (including boundary)
    return api.post('/skills/upload', form)
}

export const getSkill = (id: string) => api.get(`/skills/${id}`)
export const deleteSkill = (id: string) => api.delete(`/skills/${id}`)
