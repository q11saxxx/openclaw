# OpenClaw Skill Risk Platform

基于多智能体的 OpenClaw Skill 供应链风险平台项目骨架。

## 项目目标
- 对 OpenClaw skill 包进行解析、静态安全审计、语义审计、来源与依赖分析。
- 通过多智能体协作生成风险评分与审计报告。
- 为后续扩展动态行为复核、签名校验、运行时治理预留接口。

## 当前状态
这是一个**项目脚手架**，重点是：
1. 目录结构已经分层；
2. 每个文件都附带了“规则描述 / 职责说明”；
3. 关键模块已放置最小可运行占位代码；
4. 你可以在此基础上逐步补全业务逻辑。

## 推荐启动顺序
1. 完善 `app/config/settings.py`
2. 完善 `app/schemas/*`
3. 完善 `app/analyzers/*`
4. 完善 `app/agents/*`
5. 完善 `app/core/pipeline.py`
6. 接通 `app/api/v1/*`
7. 增加测试与样本

## 运行（占位）
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
