# OpenClaw 前端 - 快速参考

## 🚀 一键启动

### Windows
```bash
双击 start-frontend.bat
```

### Linux/Mac
```bash
chmod +x start-frontend.sh
./start-frontend.sh
```

## 📍 访问地址
- **前端**: http://localhost:3000
- **后端API**: http://localhost:8000

## 📂 核心页面

| 页面 | 路径 | 功能 |
|------|------|------|
| Dashboard | `/` | 系统概览、统计数据 |
| Skill管理 | `/skills` | 查看、搜索、上传Skill |
| Skill详情 | `/skills/:id` | 详细信息、审计报告 |
| 发起审计 | `/audit/new` | 选择Skill、配置选项 |
| 审计任务 | `/audit` | 查看所有审计任务 |
| 审计进度 | `/audit/:id/progress` | 实时进度、日志 |
| 报告列表 | `/reports` | 所有审计报告 |
| 报告详情 | `/report/:id` | 详细风险、图表、导出 |
| 规则管理 | `/rules` | CRUD规则 |

## 🎨 主要特性

✅ 渐变紫色主题  
✅ ECharts数据可视化  
✅ 拖拽文件上传  
✅ 代码语法高亮  
✅ 响应式布局  
✅ TypeScript类型安全  
✅ 完整的CRUD功能  

## 🔧 常用命令

```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 生产构建
npm run build

# 代码检查
npm run lint

# 代码格式化
npm run format
```

## 📊 技术栈

- Vue 3 + TypeScript
- Element Plus UI
- Pinia 状态管理
- Vue Router 路由
- Axios HTTP客户端
- ECharts 图表
- Vite 构建工具

## 💡 提示

1. **首次运行**需要执行 `npm install` 安装依赖
2. **后端服务**需要先启动（http://localhost:8000）
3. **文件上传**支持 .zip, .tar.gz, .json 格式
4. **文件大小**限制为 50MB
5. **审计流程**包含6个步骤，可能需要几分钟

## 🐛 常见问题

**Q: 端口被占用？**  
A: 修改 `vite.config.ts` 中的 port

**Q: 无法连接后端？**  
A: 检查后端是否运行在 8000 端口

**Q: TypeScript报错？**  
A: 运行 `npm run lint` 查看详情

**Q: 依赖安装失败？**  
A: 清除缓存后重试
```bash
npm cache clean --force
npm install
```

## 📖 详细文档

查看完整文档：
- [README.md](frontend/README.md) - 详细使用说明
- [FRONTEND_COMPLETION_SUMMARY.md](FRONTEND_COMPLETION_SUMMARY.md) - 项目总结

---

**祝使用愉快！** 🎉
