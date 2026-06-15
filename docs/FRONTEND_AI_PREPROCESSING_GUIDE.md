# AI预处理功能 - 前端集成指南

## 📋 概述

AI预处理功能已完全集成到OpenClaw前端页面中，用户可以通过简单的勾选操作启用该功能。

## ✅ 已完成的前端集成

### 1. 审计发起页面 (`/audit/new`)

**文件位置**: `frontend/src/views/audit/New.vue`

**功能特性**:
- ✅ AI预处理复选框
- ✅ 友好的UI提示
- ✅ 表单数据正确传递到后端

**代码示例**:
```vue
<el-checkbox v-model="form.ai_preprocessing" class="option-item">
  <div class="option-content">
    <div class="option-icon semantic">
      <el-icon><MagicStick /></el-icon>
    </div>
    <div>
      <div class="option-title">AI 预处理</div>
      <div class="option-desc">使用 AI 对大文件进行智能提炼和摘要，提高审计效率</div>
    </div>
  </div>
</el-checkbox>
```

**数据提交**:
```javascript
const res = await runAudit({ 
  skill_id: form.value.skill_id, 
  options: { 
    semantic: form.value.semantic,
    static_security: form.value.static_security,
    dependency_check: form.value.dependency_check,
    ai_preprocessing: form.value.ai_preprocessing  // ✅ 传递到后端
  } 
})
```

### 2. 报告详情页面 (`/report/:id`)

**文件位置**: `frontend/src/views/report/Detail.vue`

**功能特性**:
- ✅ 显示AI预处理统计信息
- ✅ 展示每个文件的AI摘要
- ✅ 展示AI建议
- ✅ 可折叠的文件列表

**显示内容**:

#### A. 预处理概览卡片
```vue
<el-card class="preprocess-card" shadow="hover">
  <template #header>
    <span>🤖 AI 预处理信息</span>
  </template>
  
  <!-- 统计信息 -->
  <el-row :gutter="24">
    <el-col :span="6">
      <div class="summary-item">
        <div class="label">是否启用</div>
        <div class="value">{{ aiPreprocessingEnabled ? '已启用' : '未启用' }}</div>
      </div>
    </el-col>
    <el-col :span="6">
      <div class="summary-item">
        <div class="label">分析文件数</div>
        <div class="value">{{ preprocessed.files_analyzed || 0 }}</div>
      </div>
    </el-col>
    <!-- ... 更多统计项 -->
  </el-row>
</el-card>
```

#### B. 预处理文件列表
```vue
<div v-if="preprocessedFiles.length" class="preprocess-files">
  <div class="file-list-title">预处理文件列表</div>
  <el-collapse>
    <el-collapse-item
      v-for="(file, idx) in preprocessedFiles"
      :key="file.file_path || idx"
      :name="idx"
    >
      <template #title>
        <div class="file-title">
          <span>{{ file.file_path }}</span>
          <el-tag size="small" type="success">
            {{ file.extracted_lines }}/{{ file.original_lines }} 行
          </el-tag>
        </div>
      </template>
      
      <div class="file-detail">
        <!-- AI摘要 -->
        <p class="file-summary">
          AI 摘要: {{ file.ai_summary || '无' }}
        </p>
        
        <!-- AI建议 -->
        <div v-if="file.ai_recommendation" class="file-recommendation">
          <strong>建议：</strong> {{ file.ai_recommendation }}
        </div>
        
        <!-- 预处理后的代码 -->
        <code-highlight 
          :content="file.preprocessed_content || ''" 
          language="plaintext" 
        />
      </div>
    </el-collapse-item>
  </el-collapse>
</div>
```

**数据获取**:
```javascript
// 计算属性
const preprocessed = computed(() => rawData.value?.preprocessed || {})
const aiPreprocessingEnabled = computed(() => 
  metadata.value?.ai_preprocessing || false
)
const preprocessedFiles = computed(() => 
  preprocessed.value?.preprocessed_files || []
)
```

## 🎯 用户使用流程

### 步骤1: 发起审计

1. 访问审计发起页面: `http://localhost:5173/audit/new`
2. 选择要审计的Skill
3. **勾选"AI预处理"选项** ✨
4. 点击"开始审计"

### 步骤2: 查看进度

- 系统会自动处理超过1000行的代码文件
- 如果设置了DEEPSEEK_API_KEY，会生成AI摘要
- 可以在进度页面查看审计状态

### 步骤3: 查看报告

1. 进入报告详情页面
2. 滚动到"🤖 AI 预处理信息"部分
3. 查看预处理统计
4. 展开文件列表查看每个文件的AI摘要和建议

## 📊 数据显示示例

### 预处理统计卡片

```
┌─────────────────────────────────────────────┐
│ 🤖 AI 预处理信息                             │
├─────────────────────────────────────────────┤
│ 是否启用:     已启用                         │
│ 分析文件数:   2                              │
│ 预处理文件数: 1                              │
│ 平均压缩比:   0.9%                           │
└─────────────────────────────────────────────┘
```

### 文件详情（展开后）

```
📄 test-skill-demo/large-code/main.py  [16/1726 行]

AI 摘要: 该代码片段包含动态命令执行功能，存在命令注入风险

建议: 建议使用subprocess模块替代os.system，并对输入进行严格验证

# L10: import os
# L11: import sys
# L12: import json
# L13: import requests
# L14: import subprocess
...
```

## 🔧 技术细节

### 数据流

```
用户勾选"AI预处理"
    ↓
前端表单提交 (ai_preprocessing=true)
    ↓
API调用: POST /api/v1/audits/run
    ↓
后端接收options参数
    ↓
ParserAgent读取options.ai_preprocessing
    ↓
CodePreprocessor.preprocess(use_ai=true)
    ↓
生成预处理结果
    ↓
存储在AuditContext.preprocessed
    ↓
ReportService.build_report()包含preprocessed字段
    ↓
保存到JSON报告文件
    ↓
前端GET /api/v1/reports/{audit_id}获取报告
    ↓
提取metadata.ai_preprocessing和preprocessed数据
    ↓
在报告详情页显示
```

### 关键字段映射

| 前端字段 | 后端来源 | 说明 |
|---------|---------|------|
| `aiPreprocessingEnabled` | `metadata.ai_preprocessing` | 是否启用了AI预处理 |
| `preprocessed.files_analyzed` | `preprocessed.files_analyzed` | 分析的总文件数 |
| `preprocessed.files_preprocessed` | `preprocessed.files_preprocessed` | 实际预处理的文件数 |
| `preprocessed.statistics.average_compression_ratio` | `preprocessed.statistics.average_compression_ratio` | 平均压缩比 |
| `preprocessedFiles[].ai_summary` | `preprocessed.preprocessed_files[].ai_summary` | AI生成的摘要 |
| `preprocessedFiles[].ai_recommendation` | `preprocessed.preprocessed_files[].ai_recommendation` | AI给出的建议 |
| `preprocessedFiles[].preprocessed_content` | `preprocessed.preprocessed_files[].preprocessed_content` | 提炼后的代码 |

## 💡 最佳实践

### 1. 何时启用AI预处理

✅ **推荐启用**:
- Skill包包含大型代码文件（>1000行）
- 需要深入理解代码语义
- 希望获得AI的安全建议

❌ **无需启用**:
- 所有文件都很小（<1000行）
- 只需要快速静态扫描
- 没有设置DEEPSEEK_API_KEY

### 2. 性能考虑

- **无API密钥**: 几乎无性能影响（仅常规预处理）
- **有API密钥**: 每个大文件增加2-12秒
- **压缩效果**: 减少约70%的数据量

### 3. 用户体验优化

- 在审计发起页面提供清晰的说明
- 在报告中使用可视化元素（图标、标签）
- 支持折叠/展开文件详情
- 显示压缩比等关键指标

## 🐛 故障排除

### 问题1: 前端显示"未启用"但已勾选

**原因**: 后端可能没有正确接收到options参数

**解决**:
1. 检查浏览器控制台的网络请求
2. 确认请求体中包含 `"ai_preprocessing": true`
3. 检查后端日志

### 问题2: AI摘要显示为"无"

**原因**: 
- 未设置DEEPSEEK_API_KEY
- LLM调用失败
- 文件未被预处理（<1000行）

**解决**:
1. 设置环境变量: `export DEEPSEEK_API_KEY="your_key"`
2. 检查后端日志中的LLM调用记录
3. 确认文件大小超过阈值

### 问题3: 预处理文件列表为空

**原因**: 没有文件超过1000行

**解决**:
- 这是正常行为
- 可以降低`LINE_THRESHOLD`阈值
- 或使用更大的Skill包测试

## 📝 开发笔记

### 添加新的AI字段

如果需要在前端显示更多AI分析结果：

1. **后端**: 在`CodePreprocessor._generate_ai_insight()`中添加新字段
2. **API**: 确保字段包含在返回的JSON中
3. **前端**: 在`Detail.vue`中添加显示逻辑

示例:
```javascript
// 后端返回
{
  "ai_summary": "...",
  "ai_recommendation": "...",
  "ai_suspicious": true,  // 新增字段
  "ai_confidence": 0.85   // 新增字段
}

// 前端显示
<p>可疑性: {{ file.ai_suspicious ? '是' : '否' }}</p>
<p>置信度: {{ (file.ai_confidence * 100).toFixed(0) }}%</p>
```

### 样式定制

所有AI预处理相关的UI组件都使用了Element Plus的标准组件，可以通过CSS自定义样式：

```css
.preprocess-card {
  border-left: 4px solid var(--primary-color);
}

.file-summary {
  color: var(--text-secondary);
  font-style: italic;
}

.file-recommendation {
  background: #f0f9ff;
  padding: 8px 12px;
  border-radius: 4px;
  margin: 8px 0;
}
```

## 🚀 未来改进

- [ ] 添加AI分析进度条
- [ ] 支持实时显示AI摘要生成过程
- [ ] 添加AI置信度评分显示
- [ ] 支持导出AI分析报告
- [ ] 添加AI分析历史对比

---

**最后更新**: 2026年5月9日  
**版本**: 1.0.0  
**状态**: ✅ 生产就绪
