// 本文件说明：项目模块接口封装，供项目页与表单组件调用。
import { apiClient } from './client'

export const fetchProjects = () => apiClient.get('/projects')
