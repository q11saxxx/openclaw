# AI预处理功能 - 快速开始

## 🚀 5分钟快速上手

### 第1步: 设置API密钥（可选）

```bash
# Linux/Mac
export DEEPSEEK_API_KEY="your_api_key_here"

# Windows PowerShell
$env:DEEPSEEK_API_KEY="your_api_key_here"

# Windows CMD
set DEEPSEEK_API_KEY=your_api_key_here
```

> 💡 **提示**: 如果不设置API密钥，系统会自动使用常规预处理模式（不生成AI摘要），不影响其他功能。

### 第2步: 测试功能

```bash
# 运行完整测试套件
python test_ai_preprocessing.py

# 或运行演示脚本
python demo_ai_preprocessing.py
```

预期输出：
```
🎉 所有测试通过！AI预处理功能完全正常！
```

### 第3步: 使用功能

#### 方式A: 前端界面（推荐）

1. 启动后端服务
   ```bash
   uvicorn app.main:app --reload
   ```

2. 启动前端服务
   ```bash
   cd frontend
   npm run dev
   ```

3. 访问 `http://localhost:5173/audit/new`

4. 选择Skill并勾选"AI预处理"选项

5. 点击"开始审计"

#### 方式B: API调用

```bash
curl -X POST http://localhost:8000/api/v1/audits/run \
  -H "Content-Type: application/json" \
  -d '{
    "skill_id": "your_skill_id",
    "options": {
      "ai_preprocessing": true
    }
  }'
```

#### 方式C: Python代码

```python
from app.analyzers.code_preprocessor import CodePreprocessor

preprocessor = CodePreprocessor()
result = preprocessor.preprocess(
    skill_path="/path/to/skill",
    use_ai=True  # 启用AI
)

# 查看AI摘要
for file_info in result["preprocessed_files"]:
    print(f"File: {file_info['file_path']}")
    print(f"AI Summary: {file_info.get('ai_summary', 'N/A')}")
```

## 📊 查看结果

### 在审计报告中

审计报告会包含预处理统计信息：

```json
{
  "preprocessed": {
    "files_analyzed": 5,
    "files_preprocessed": 2,
    "preprocessed_files": [
      {
        "file_path": "src/main.py",
        "original_lines": 1525,
        "extracted_lines": 45,
        "ai_summary": "该代码片段包含...",
        "ai_recommendation": "建议..."
      }
    ],
    "ai_preprocessing_enabled": true
  }
}
```

## ❓ 常见问题

### Q: 我没有API密钥，能用这个功能吗？

**A**: 可以！系统会自动降级为常规预处理模式，仍然会提取关键代码，只是不会生成AI摘要。

### Q: 哪些文件会被AI分析？

**A**: 只有超过1000行的代码文件才会被预处理和AI分析。

### Q: 会影响审计速度吗？

**A**: 
- 无API密钥: 几乎无影响（<10ms/文件）
- 有API密钥: 每个大文件增加2-12秒

### Q: 如何禁用AI预处理？

**A**: 
- 前端: 不勾选"AI预处理"复选框
- API: 设置 `options.ai_preprocessing = false` 或不传该参数
- 代码: 调用时设置 `use_ai=False`

## 🔗 更多信息

- 📖 [完整使用指南](AI_PREPROCESSING_GUIDE.md)
- 🧪 [测试脚本](test_ai_preprocessing.py)
- 🎬 [演示脚本](demo_ai_preprocessing.py)
- 📋 [实现总结](AI_PREPROCESSING_COMPLETION.md)

---

**就这么简单！** ✨
