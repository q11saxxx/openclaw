#!/usr/bin/env python3
"""
AI预处理功能演示脚本
"""

from app.analyzers.code_preprocessor import CodePreprocessor
import json
import os

def demo_ai_preprocessing():
    """演示AI预处理功能"""
    print("=== OpenClaw AI预处理功能演示 ===\n")

    # 检查API密钥
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("⚠️  警告: DEEPSEEK_API_KEY 环境变量未设置")
        print("   AI预处理功能将使用常规模式（不生成AI摘要）\n")
    
    # 初始化预处理器
    preprocessor = CodePreprocessor()

    # 测试常规预处理
    print("1. 常规预处理（不使用AI）:")
    result_regular = preprocessor.preprocess('test-skill-demo', use_ai=False)
    print(f"   - 分析文件数: {result_regular['files_analyzed']}")
    print(f"   - 预处理文件数: {result_regular['files_preprocessed']}")
    ratio = result_regular['statistics'].get('average_compression_ratio', 0)
    print(f"   - 平均压缩比: {ratio:.1%}")
    print(f"   - AI预处理: {result_regular.get('ai_preprocessing_enabled', False)}\n")

    # 测试AI预处理（需要API密钥）
    print("2. AI预处理（需要DEEPSEEK_API_KEY环境变量）:")
    result_ai = preprocessor.preprocess('test-skill-demo', use_ai=True)
    print(f"   - 分析文件数: {result_ai['files_analyzed']}")
    print(f"   - 预处理文件数: {result_ai['files_preprocessed']}")
    ratio_ai = result_ai['statistics'].get('average_compression_ratio', 0)
    print(f"   - 平均压缩比: {ratio_ai:.1%}")
    print(f"   - AI预处理: {result_ai.get('ai_preprocessing_enabled', False)}")

    if result_ai.get('preprocessed_files'):
        file_data = result_ai['preprocessed_files'][0]
        print("\n   - AI摘要:")
        print(f"     {file_data.get('ai_summary', '无摘要')}")
        if 'ai_recommendation' in file_data:
            print(f"   - AI建议: {file_data['ai_recommendation']}")
        if 'ai_suspicious' in file_data:
            print(f"   - 可疑性: {'是' if file_data['ai_suspicious'] else '否'}")

    print("\n=== 前端集成说明 ===")
    print("✓ 前端已添加AI预处理选项复选框")
    print("✓ 审计发起页面包含'AI预处理'选项")
    print("✓ 后端API支持ai_preprocessing参数")
    print("✓ 预处理结果包含AI摘要和建议")

    print("\n=== 使用方法 ===")
    print("1. 设置DEEPSEEK_API_KEY环境变量")
    print("   export DEEPSEEK_API_KEY=\"your_api_key_here\"")
    print("2. 在前端审计页面勾选'AI预处理'选项")
    print("3. 发起审计，系统会自动对大文件进行AI预处理")
    print("4. 查看审计报告中的AI摘要和建议")
    
    print("\n=== 数据流示例 ===")
    print("前端 → API (/audits/run) → AuditService → Orchestrator → Pipeline → ParserAgent → CodePreprocessor")
    print("options.ai_preprocessing=true → use_ai=True → LLMService.call_model()")

if __name__ == "__main__":
    demo_ai_preprocessing()
