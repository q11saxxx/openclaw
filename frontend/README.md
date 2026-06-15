# OpenClaw Frontend 使用说明

## 📋 目录

- [项目简介](#项目简介)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [功能模块](#功能模块)
- [页面说明](#页面说明)
- [API对接](#api对接)
- [开发指南](#开发指南)

## 项目简介

OpenClaw Skill Risk Platform 前端是一个基于 Vue 3 + Element Plus 构建的现代化 Web 应用，用于管理和审计 OpenClaw Skill 包的安全风险。

### 核心特性

✨ **专业美观的界面**
- 渐变紫色主题设计
- 响应式布局
- 平滑过渡动画
- 现代化卡片组件

🔒 **完整的安全审计流程**
- Skill 上传与解析
- 多维度安全检测
- 实时进度跟踪
- 详细报告生成

📊 **丰富的数据可视化**
- ECharts 风险分布图
- 统计卡片
- 时间线展示
- 代码高亮

## 技术栈

- **框架**: Vue 3.3+ (Composition API)
- **语言**: TypeScript 5.2+
- **UI库**: Element Plus 2.2+
- **图标**: @element-plus/icons-vue
- **状态管理**: Pinia 2.0+
- **路由**: Vue Router 4.2+
- **HTTP客户端**: Axios 1.4+
- **图表**: ECharts 5.4+
- **代码高亮**: Highlight.js 11.8+
- **构建工具**: Vite 5.1+

## 快速开始

### 环境要求

- Node.js >= 16.x
- npm >= 8.x

### 安装依赖

```bash
cd frontend
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

### 构建生产版本

```bash
npm run build
```

### 代码检查和格式化

```bash
npm run lint
npm run format
```

## 功能模块

### 1. Dashboard（仪表盘）

**路径**: `/`

**功能**:
- 显示系统概览统计信息
  - 总 Skill 数量
  - 审计报告数量
  - 高风险 Skill 数量
  - 今日审计次数
- 最近上传的 Skill 列表
- 最近生成的审计报告
- 快速导航到各功能模块

**特色**:
- 渐变色统计卡片
- 实时更新数据
- 一键查看详情

### 2. Skill 管理

**路径**: `/skills`

**功能**:
- Skill 列表展示（分页）
- 搜索过滤（按名称/路径）
- 风险等级筛选
- 上传新 Skill
- 查看 Skill 详情
- 快速发起审计

**操作**:
- 点击"上传 Skill"按钮上传文件
- 使用搜索框快速查找
- 点击"查看详情"进入详情页
- 点击"审计"直接开始审计流程

### 3. Skill 详情

**路径**: `/skills/:id`

**功能**:
- 基本信息展示（ID、名称、版本、开发者等）
- Manifest 元数据查看
- 快速检测结果
- 审计报告历史
- 下载审计报告

**布局**:
- 左侧：Skill 信息和检测结果
- 右侧：审计报告时间线

### 4. 发起审计

**路径**: `/audit/new`

**功能**:
- 选择要审计的 Skill
- 配置审计选项
  - 语义审计（LLM分析）
  - 静态安全扫描（默认启用）
  - 依赖分析（默认启用）
- 查看审计流程说明

**审计流程**:
1. Skill 解析
2. 静态安全扫描
3. 语义审计
4. 来源分析
5. 决策评估
6. 报告生成

### 5. 审计任务

**路径**: `/audit`

**功能**:
- 查看所有审计任务
- 查看任务状态
- 查看审计进度
- 跳转到报告详情

### 6. 审计进度

**路径**: `/audit/:id/progress`

**功能**:
- 实时显示审计进度（6个步骤）
- 显示审计日志
- 自动轮询更新状态
- 完成后跳转到报告

**特色**:
- 步骤条可视化
- 实时日志输出
- 完成提示和快捷操作

### 7. 审计报告

**路径**: `/reports`

**功能**:
- 所有审计报告列表
- 风险等级展示
- 置信度显示
- 发现数量统计
- 下载报告（MD/JSON格式）

### 8. 报告详情

**路径**: `/report/:id`

**功能**:
- 风险概览（等级、置信度、发现数）
- Skill 信息
- ECharts 风险分布饼图
- 详细风险列表（折叠面板）
  - 风险标题和描述
  - 证据代码高亮
  - 修复建议
- 导出报告（MD/JSON）

**特色**:
- 交互式图表
- 代码语法高亮
- 可折叠的风险详情
- 专业的报告布局

### 9. 规则管理

**路径**: `/rules`

**功能**:
- 查看所有规则（内置/自定义）
- 创建新规则
- 编辑自定义规则
- 删除自定义规则
- 查看规则详情

**规则字段**:
- 规则 ID（唯一标识）
- 规则名称
- 匹配模式（正则表达式）
- 风险等级（critical/high/medium/low）
- 描述

**操作**:
- 切换规则类型（全部/内置/自定义）
- 点击"创建规则"添加新规则
- 点击"编辑"修改自定义规则
- 点击"删除"移除规则（需确认）

## API对接

### 后端地址

开发环境通过 Vite 代理：
- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- 代理配置: `/api/*` → `http://localhost:8000/*`

### 主要接口

#### Skill 相关
```typescript
GET    /api/skills              // 列出 Skills（支持分页和搜索）
GET    /api/skills/:id          // 获取 Skill 详情
POST   /api/skills/upload       // 上传 Skill
POST   /api/skills/parse        // 解析 Skill
```

#### 审计相关
```typescript
POST   /api/audits/run          // 运行审计
GET    /api/audits              // 列出审计任务
GET    /api/audits/:id          // 获取审计状态/进度
```

#### 报告相关
```typescript
GET    /api/reports/:id         // 获取报告详情
GET    /api/reports/:id/export  // 导出报告（?format=json|md）
```

#### 规则相关
```typescript
GET    /api/rules               // 列出规则（?rule_type=builtin|custom）
GET    /api/rules/:id           // 获取规则详情
POST   /api/rules               // 创建规则
PUT    /api/rules/:id           // 更新规则
DELETE /api/rules/:id           // 删除规则
```

## 开发指南

### 项目结构

```
frontend/
├── src/
│   ├── api/              # API 接口封装
│   │   ├── request.ts    # Axios 实例和拦截器
│   │   ├── skill.ts      # Skill 相关 API
│   │   ├── audit.ts      # 审计相关 API
│   │   └── report.ts     # 报告相关 API
│   ├── components/       # 公共组件
│   │   ├── UploadSkill.vue      # Skill 上传组件
│   │   ├── RiskBadge.vue        # 风险等级标签
│   │   ├── ProgressSteps.vue    # 进度步骤
│   │   └── CodeHighlight.vue    # 代码高亮
│   ├── views/            # 页面组件
│   │   ├── Dashboard.vue
│   │   ├── Rules.vue
│   │   ├── skills/       # Skill 相关页面
│   │   ├── audit/        # 审计相关页面
│   │   ├── report/       # 报告详情
│   │   └── reports/      # 报告列表
│   ├── router/           # 路由配置
│   ├── stores/           # Pinia Store
│   │   └── skill.ts      # Skill 状态管理
│   ├── styles.css        # 全局样式
│   ├── App.vue           # 根组件
│   └── main.ts           # 入口文件
├── index.html
├── package.json
├── vite.config.ts        # Vite 配置
└── tsconfig.json         # TypeScript 配置
```

### 添加新页面

1. 在 `src/views/` 下创建新的 Vue 组件
2. 在 `src/router/index.ts` 中添加路由
3. 在 `src/App.vue` 的菜单中添加导航项（如需要）

### 添加新组件

1. 在 `src/components/` 下创建组件
2. 使用 `<script setup>` 语法
3. 定义 Props 和 Emits 类型
4. 添加必要的注释

### 样式规范

- 使用 scoped 样式避免污染
- 遵循 BEM 命名规范
- 优先使用 Element Plus 组件
- 自定义样式写在 `styles.css` 中

### 状态管理

使用 Pinia Store 管理全局状态：

```typescript
import { useSkillStore } from '../stores/skill'

const store = useSkillStore()
await store.fetchSkills({ page: 1, size: 10 })
```

### API 调用

使用封装好的 API 函数：

```typescript
import { listSkills } from '../api/skill'

const res = await listSkills({ page: 1, size: 10 })
```

### 错误处理

API 请求的错误已在 `request.ts` 中统一处理，会显示 ElMessage 提示。

## 常见问题

### Q: 前端无法连接后端？

A: 检查以下事项：
1. 后端是否运行在 http://localhost:8000
2. 后端是否配置了 CORS
3. Vite 代理配置是否正确（vite.config.ts）
4. 浏览器控制台是否有 CORS 错误

### Q: 如何修改主题色？

A: 修改 `src/styles.css` 中的渐变色定义：
```css
.el-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

### Q: 如何添加新的 API 接口？

A: 
1. 在 `src/api/` 下创建或修改 API 文件
2. 使用 `api` 实例进行请求
3. 在组件中导入并使用

### Q: 图表不显示？

A: 确保：
1. 已安装 echarts: `npm install echarts`
2. 容器有明确的高度
3. 在数据加载后调用 `renderChart()`

## 更新日志

### v0.1.0 (2026-04-21)

- ✨ 完成所有核心页面开发
- ✨ 实现完整的 CRUD 功能
- ✨ 添加 ECharts 数据可视化
- ✨ 优化 UI/UX 体验
- ✨ 完善 API 对接
- ✨ 添加代码高亮和文件上传
- ✨ 实现响应式布局

## 许可证

本项目遵循主项目许可证。
