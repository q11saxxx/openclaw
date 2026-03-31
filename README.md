# OpenClaw Skill 供应链安全审计平台（项目框架）

本仓库基于你们开题报告中的功能模块、技术路线和 8 周研发计划进行搭建，适合作为 VSCode 中直接打开开发的主仓库。

## 目标对应开题报告
- 围绕 7 个核心功能模块组织代码：项目管理、OpenClaw Skill 专项审计、SBOM 生成、多源漏洞匹配、风险可视化、修复指引、报告导出。
- 采用前后端分离：前端 Vue3 + Vite + Tailwind + ECharts，后端 FastAPI，核心引擎层对 Trivy 做二次封装，并预留自研规则与多源漏洞聚合扩展位。
- 开发阶段默认 SQLite，后续切换 MySQL。

## 推荐在 VSCode 的开发顺序
1. 先启动 `backend/` 的最小 API。
2. 再启动 `frontend/` 完成页面骨架。
3. 然后串联 `engine/trivy`、`engine/scanner`、`engine/reports`。
4. 最后补数据库、测试、Docker、演示数据。

## 快速开始
### 后端
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

## 目录导航
- `backend/`：FastAPI 后端与核心引擎适配层
- `frontend/`：Vue3 前端与可视化页面骨架
- `rules/`：自研规则文件
- `examples/`：演示用 OpenClaw Skill 与通用项目
- `docs/`：模块说明、接口规划、团队分工、迭代路线
- `deploy/`：Docker 与部署配置
- `.vscode/`：VSCode 推荐配置与调试任务
