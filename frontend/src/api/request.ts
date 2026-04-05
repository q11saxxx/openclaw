import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({ baseURL: '/api', timeout: 30000 })

// 请求拦截器 - 添加通用错误处理
api.interceptors.request.use(
    (config) => {
        console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`)
        console.log(`[API Request] Full URL: ${window.location.origin}${config.baseURL}${config.url}`)
        return config
    },
    (error) => {
        console.error('[API Request Error]:', error)
        return Promise.reject(error)
    }
)

// 响应拦截器 - 统一错误处理
api.interceptors.response.use(
    (response) => {
        console.log(`[API Response] ${response.status} ${response.config.url}`)
        console.log(`[API Response] Data:`, response.data)
        return response.data
    },
    (error) => {
        const status = error?.response?.status
        const message = error?.response?.data?.detail || error?.message || '请求失败'
        
        console.error(`[API Error] Status:`, status)
        console.error(`[API Error] Message:`, message)
        console.error(`[API Error] Full Error:`, error)
        console.error(`[API Error] Config:`, error.config)
        
        // 根据状态码显示不同的提示
        if (status === 404) {
            ElMessage.warning('资源不存在')
        } else if (status === 401) {
            ElMessage.error('未授权，请重新登录')
        } else if (status === 403) {
            ElMessage.error('权限不足')
        } else if (status === 500) {
            ElMessage.error('服务器内部错误')
        } else if (!status) {
            // 详细诊断信息
            console.warn('[Network Diagnostic]')
            console.warn('- Backend may not be running on http://localhost:8000')
            console.warn('- Check if CORS is configured in backend')
            console.warn('- Verify Vite proxy configuration')
            console.warn('- Check browser console for CORS errors')
            console.warn('- Try accessing http://localhost:8000/health directly')
            
            ElMessage.error({
                message: '网络连接失败，请检查后端服务是否启动',
                duration: 5000,
                showClose: true
            })
        } else {
            ElMessage.error(message)
        }
        
        return Promise.reject(error)
    }
)

export default api
