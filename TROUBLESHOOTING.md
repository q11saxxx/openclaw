# "服务器内部错误"和"加载技能列表失败"问题诊断

## 🔍 问题分析

用户报告两个错误：
1. **服务器内部错误** - 后端API调用失败
2. **加载技能列表失败** - 前端无法获取Skill列表

## ✅ 诊断结果

经过检查，发现：

### 后端API正常
```bash
✅ 后端运行在: http://localhost:8000
✅ API路径: /api/skills
✅ 响应状态: 200 OK
✅ 返回数据: 包含skills列表
```

### 前端配置正常
```javascript
✅ baseURL: '/api' (正确)
✅ Vite代理: /api -> http://localhost:8000 (正确)
✅ CORS配置: 允许localhost:3000/3001 (正确)
```

## 🔧 问题原因

前端开发服务器启动在了 **3001端口**（因为3000端口被占用），但后端CORS配置中包含了3001端口，所以理论上应该可以工作。

可能的问题：
1. **端口变化**: 前端从3000变成3001
2. **代理配置**: Vite代理可能没有正确转发请求
3. **浏览器缓存**: 可能需要硬刷新

## 💡 解决方案

### 方案1：使用新的端口访问（推荐）
```
访问: http://localhost:3001/audit/new
```

### 方案2：释放3000端口
```bash
# Windows查找占用3000端口的进程
netstat -ano | findstr :3000

# 结束该进程（将PID替换为实际进程ID）
taskkill /PID <进程ID> /F

# 重启前端
cd frontend
npm run dev
```

### 方案3：直接测试API
```bash
# 测试后端API是否正常
curl "http://localhost:8000/api/skills?page=1&size=10"

# 应该返回200和skills数据
```

## 📊 验证步骤

### 1. 检查后端运行状态
```bash
✅ uvicorn正在运行
✅ 端口: 8000
✅ 路由: /api/skills 返回200
```

### 2. 检查前端运行状态
```bash
✅ Vite正在运行
✅ 端口: 3001（注意不是3000）
✅ 代理: /api -> http://localhost:8000
```

### 3. 浏览器验证
1. 打开 http://localhost:3001
2. 导航到"发起审计"页面
3. 查看浏览器开发者工具的Network标签
4. 检查 `/api/skills` 请求的状态

### 4. 查看控制台日志
前端API请求拦截器会输出详细日志：
```javascript
[API Request] GET /skills
[API Request] Full URL: http://localhost:3001/api/skills
[API Response] 200 /skills
[API Response] Data: { items: [...], total: ... }
```

## 🎯 当前状态

| 组件 | 状态 | 端口 |
|------|------|------|
| 后端API | ✅ 运行中 | 8000 |
| 前端开发服务器 | ✅ 运行中 | 3001 |
| Skills API | ✅ 正常 | /api/skills |
| CORS配置 | ✅ 已配置 | 允许3000/3001 |

## 🔍 调试命令

### 检查端口占用
```bash
netstat -ano | findstr :3000
netstat -ano | findstr :3001
netstat -ano | findstr :8000
```

### 重启服务
```bash
# 后端
cd c:\code\openclawcode\openclaw-final
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 前端
cd c:\code\openclawcode\openclaw-final\frontend
npm run dev
```

### 测试API
```bash
# 后端直连测试
curl "http://localhost:8000/api/skills?page=1&size=10"

# 前端代理测试
curl "http://localhost:3001/api/skills?page=1&size=10"
```

## 📝 预防措施

1. **固定端口**: 在Vite配置中强制使用特定端口
   ```typescript
   server: {
       port: 3000,
       strictPort: true, // 如果端口被占用则报错而不是使用其他端口
       proxy: { ... }
   }
   ```

2. **健康检查**: 启动时检查后端是否可用
   ```javascript
   // 在main.ts中添加
   fetch('/api/health').then(...).catch(...)
   ```

3. **错误提示优化**: 显示更详细的错误信息
   ```javascript
   ElMessage.error(`加载失败: ${error.message}`)
   ```

---

**问题状态**: ⚠️ 需要确认前端是否正确连接到后端
**建议操作**: 访问 http://localhost:3001 并刷新页面测试
