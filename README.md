# OpenClaw Skill Risk Platform

基于多智能体的 OpenClaw Skill 供应链风险平台项目骨架。

## 核心功能

### 🤖 AI预处理 (新增 ✨)
- **智能代码提炼**: 对超过1000行的代码文件自动提取关键部分
- **AI安全分析**: 使用LLM生成代码的安全摘要和风险建议
- **性能优化**: 显著提高大文件审计效率（减少70%数据量）

#### 使用方法
1. 设置环境变量: `export DEEPSEEK_API_KEY="your_api_key"`
2. 在前端审计页面勾选"AI预处理"选项
3. 发起审计，查看报告中的AI摘要和建议

**详细文档**: [docs/AI_PREPROCESSING_GUIDE.md](docs/AI_PREPROCESSING_GUIDE.md)

### 🔍 审计流程
- 静态安全分析
- 语义风险检测
- 依赖关系检查
- 来源可信度评估

## 当前状态
这是一个**项目脚手架**，重点是：
1. 目录结构已经分层；
2. 每个文件都附带了"规则描述 / 职责说明"；
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

## 快速测试AI预处理功能

```bash
# 1. 设置API密钥（可选）
export DEEPSEEK_API_KEY="your_key_here"

# 2. 运行测试脚本
python test_ai_preprocessing.py

# 3. 运行演示脚本
python demo_ai_preprocessing.py
```

## 相关文档

- [AI预处理完整指南](docs/AI_PREPROCESSING_GUIDE.md) - 详细的使用说明和配置
- [代码预处理器指南](docs/CODE_PREPROCESSOR_GUIDE.md) - 基础预处理功能
- [实现总结](IMPLEMENTATION_SUMMARY.md) - 技术实现细节