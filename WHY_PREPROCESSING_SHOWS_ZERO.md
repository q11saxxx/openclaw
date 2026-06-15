# 为什么AI预处理显示"分析文件数: 0"

## 🐛 问题现象

前端显示：
- ✅ 是否启用：**已启用**
- ❌ 分析文件数：**0**
- ❌ 预处理文件数：**0**
- ❌ 平均压缩比：**-**

## 🔍 根本原因

**你查看的Skill包中没有代码文件！**

从调试可以看到：
```
Skill包: e40fe0ae79d1167a40ac20c57b2a9197aedcd3bd_SKILL.md
内容: 只有SKILL.md文件，没有.py、.js等代码文件
结果: files_analyzed = 0（没有代码文件可分析）
```

**AI预处理器只会处理代码文件**（.py、.js、.ts等），不会处理配置文件（.md、.yaml等）。

## ✅ 解决方案

### 方案1：查看已有的测试报告

系统中已经有一个包含代码的测试报告：

**test-skill-demo**

访问地址：
```
http://localhost:5173/report/audit_test_skill_demo_20260510_001302
```

这个报告显示：
- ✅ 分析文件数: 2
- ✅ 预处理文件数: 1
- ✅ 原始总行数: 1726
- ✅ 提取总行数: 16

### 方案2：上传包含代码的Skill包

1. **准备一个包含代码文件的Skill包**
   - 必须包含 .py、.js、.ts 等代码文件
   - 至少有一个文件超过50行（当前阈值）

2. **上传并审计**
   - 访问 `http://localhost:5173/audit/new`
   - 上传Skill包（ZIP格式）
   - **勾选"AI预处理"** ✨
   - 点击"开始审计"

3. **查看报告**
   - 进入报告详情页
   - 现在应该能看到AI预处理数据了！

### 方案3：使用本地测试Skill包

项目中有个测试用的Skill包：`test-skill-demo`

你可以用它来测试预处理功能（已在后端测试过）。

##  什么样的Skill包会触发预处理？

### ✅ 会触发预处理的Skill包

```
my-skill.zip
├── SKILL.md
├── manifest.yaml
├── main.py          ← 超过50行的Python文件
├── utils/
│   ├── helper.py    ← 超过50行的Python文件
│   └── config.js    ← 超过50行的JavaScript文件
└── src/
    └── app.ts       ← 超过50行的TypeScript文件
```

### ❌ 不会触发预处理的Skill包

```
my-skill.zip
├── SKILL.md          ← 只有配置文件
└── manifest.yaml     ← 没有代码文件
```

或者：

```
my-skill.zip
├── SKILL.md
├── manifest.yaml
└── config.py         ← 只有10行代码（<50行阈值）
```

## 🔧 如何调整阈值？

如果你想让更小的文件也触发预处理，可以修改阈值：

**文件**: `app/analyzers/code_preprocessor.py`（第88行）

```python
# 当前值
LINE_THRESHOLD = 50

# 如果你想处理更小的文件，可以降低到20
LINE_THRESHOLD = 20

# 如果你想只处理大文件，可以提高到200
LINE_THRESHOLD = 200
```

**建议值**：
- `20` - 演示用，几乎所有文件都会触发
- `50` - 测试用（当前值）
- `200` - 实际使用
- `500` - 大型项目
- `1000` - 只处理大文件

## 📝 预处理器支持的文件类型

CodePreprocessor会处理以下类型的代码文件：

- **Python**: `.py`
- **JavaScript**: `.js`, `.jsx`
- **TypeScript**: `.ts`, `.tsx`
- **Java**: `.java`
- **C/C++**: `.c`, `.cpp`, `.h`, `.hpp`
- **Go**: `.go`
- **Rust**: `.rs`
- **Ruby**: `.rb`
- **PHP**: `.php`
- **Shell**: `.sh`, `.bash`
- **PowerShell**: `.ps1`
- 等等...

**不会处理的文件**：
- 配置文件: `.md`, `.yaml`, `.yml`, `.json`, `.xml`
- 文档: `.txt`, `.pdf`, `.doc`
- 资源: `.png`, `.jpg`, `.css`, `.html`

##  总结

你看到的"分析文件数: 0"是**正常的**，因为：
1. ✅ AI预处理功能**已经启用**（metadata.ai_preprocessing = true）
2. ✅ 预处理器**正常工作**
3. ❌ 但是你的Skill包**没有代码文件**，所以分析文件数为0

**下一步**：
- 查看 test-skill-demo 的报告（有预处理数据）
- 或上传一个包含代码文件的Skill包重新测试

---

**更新日期**: 2026年5月10日  
**状态**: ✅ 功能正常，需要包含代码的Skill包
