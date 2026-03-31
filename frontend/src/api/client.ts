// 本文件说明：Axios 实例配置，后续统一处理 baseURL、超时与错误拦截。
import axios from 'axios'

export const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1',
  timeout: 10000
})
