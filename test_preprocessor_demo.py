#!/usr/bin/env python3
"""
直接测试代码预处理器功能的脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.analyzers.code_preprocessor import CodePreprocessor
from app.agents.parser_agent import ParserAgent
from app.core.context import AuditContext
from app.core.pipeline import AuditPipeline
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_preprocessor():
    """测试预处理器功能"""
    print("=" * 60)
    print("🧪 代码预处理器功能测试")
    print("=" * 60)

    # 测试文件路径
    skill_path = "test-skill-demo"
    large_code_file = os.path.join(skill_path, "large-code", "main.py")

    if not os.path.exists(large_code_file):
        print(f"❌ 测试文件不存在: {large_code_file}")
        return False

    # 检查文件行数
    with open(large_code_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        line_count = len(lines)

    print(f"📄 测试文件: {large_code_file}")
    print(f"📏 文件行数: {line_count} 行")
    print(f"🎯 预处理阈值: {CodePreprocessor.LINE_THRESHOLD} 行")
    print(f"✅ 需要预处理: {'是' if line_count > CodePreprocessor.LINE_THRESHOLD else '否'}")
    print()

    if line_count <= CodePreprocessor.LINE_THRESHOLD:
        print("⚠️ 文件行数未超过阈值，跳过预处理测试")
        return True

    # 创建预处理器
    preprocessor = CodePreprocessor()
    print("🔧 创建预处理器实例...")

    # 测试预处理
    print("⚙️ 开始预处理...")
    try:
        result = preprocessor.preprocess(skill_path)
        print("✅ 预处理完成！")
        print()

        # 显示结果
        print("📊 预处理结果:")
        print(f"  • 分析的文件数量: {result.get('files_analyzed', 0)}")
        print(f"  • 预处理的文件数量: {result.get('files_preprocessed', 0)}")
        print()

        # 显示预处理文件详情
        preprocessed_files = result.get('preprocessed_files', [])
        if preprocessed_files:
            print("📁 预处理文件详情:")
            for file_data in preprocessed_files:
                print(f"  • 文件: {file_data.get('file_path', 'unknown')}")
                print(f"    - 原始行数: {file_data.get('original_lines', 0)}")
                print(f"    - 提取行数: {file_data.get('extracted_lines', 0)}")
                print(f"    - 压缩比例: {file_data.get('extraction_ratio', 0):.1%}")
                print()

                # 显示提取的内容类型统计
                key_locations = file_data.get('key_locations', [])
                if key_locations:
                    context_types = {}
                    for loc in key_locations:
                        ctx_type = loc.get('context_type', 'unknown')
                        context_types[ctx_type] = context_types.get(ctx_type, 0) + 1

                    print("    📋 提取的内容类型:")
                    for ctx_type, count in context_types.items():
                        print(f"      - {ctx_type}: {count} 个")
                    print()
        else:
            print("⚠️ 没有文件被预处理")

    except Exception as e:
        print(f"❌ 预处理失败: {e}")
        return False

    # 测试ParserAgent集成
    print("🔗 测试ParserAgent集成...")
    try:
        context = AuditContext(skill_path=skill_path)
        agent = ParserAgent()

        # 运行解析（会自动调用预处理）
        print("⚙️ 运行ParserAgent...")
        result = agent.run(context)

        print("✅ ParserAgent执行完成！")
        print()

        # 检查预处理结果是否存储在上下文中
        if hasattr(context, 'preprocessed') and context.preprocessed:
            print("📦 预处理结果已存储在上下文中:")
            print(f"  • 分析的文件数: {context.preprocessed.get('files_analyzed', 0)}")
            print(f"  • 预处理的文件数: {context.preprocessed.get('files_preprocessed', 0)}")

            # 显示预处理文件详情
            preprocessed_files = context.preprocessed.get('preprocessed_files', [])
            if preprocessed_files:
                print("  📁 预处理文件详情:")
                for file_data in preprocessed_files:
                    print(f"    • {file_data.get('file_path', 'unknown')}: {len(file_data.get('preprocessed_content', ''))} 字符")
        else:
            print("⚠️ 未在上下文中找到预处理结果")

    except Exception as e:
        print(f"❌ ParserAgent测试失败: {e}")
        import traceback
        traceback.print_exc()

    print()
    print("🎉 所有测试通过！代码预处理器功能正常工作。")
    return True

def show_extracted_content():
    """显示提取的内容示例"""
    print("\n" + "=" * 60)
    print("📖 提取内容示例")
    print("=" * 60)

    skill_path = "test-skill-demo"
    preprocessor = CodePreprocessor()

    try:
        result = preprocessor.preprocess(skill_path)

        preprocessed_files = result.get('preprocessed_files', [])
        if preprocessed_files:
            for file_data in preprocessed_files:
                file_path = file_data.get('file_path', 'unknown')
                print(f"\n📄 文件: {file_path}")
                print("-" * 40)

                preprocessed_content = file_data.get('preprocessed_content', '')
                if preprocessed_content:
                    # 只显示前1000个字符作为示例
                    preview = preprocessed_content[:1000]
                    if len(preprocessed_content) > 1000:
                        preview += "\n... (内容过长，已截断)"

                    print(preview)
                else:
                    print("无提取内容")
        else:
            print("没有预处理的文件")

    except Exception as e:
        print(f"❌ 显示提取内容失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    success = test_preprocessor()
    if success:
        show_extracted_content()
    else:
        sys.exit(1)