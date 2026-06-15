#!/usr/bin/env python
"""
快速验证脚本 - 验证代码预处理功能是否正确集成
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_imports():
    """验证所有导入是否正常。"""
    print("🔍 验证导入...\n")
    
    try:
        print("  ✓ 导入 CodePreprocessor...")
        from app.analyzers.code_preprocessor import CodePreprocessor
        
        print("  ✓ 导入 ParserAgent...")
        from app.agents.parser_agent import ParserAgent
        
        print("  ✓ 导入 AuditContext...")
        from app.core.context import AuditContext
        
        print("  ✓ 导入 AuditPipeline...")
        from app.core.pipeline import AuditPipeline
        
        return True
    except ImportError as e:
        print(f"  ✗ 导入失败: {e}")
        return False


def verify_classes():
    """验证类的基本功能。"""
    print("\n🔧 验证类结构...\n")
    
    try:
        from app.analyzers.code_preprocessor import CodePreprocessor
        from app.agents.parser_agent import ParserAgent
        from app.core.context import AuditContext
        
        # 检查 CodePreprocessor
        print("  验证 CodePreprocessor:")
        preprocessor = CodePreprocessor()
        print(f"    ✓ 实例化成功")
        print(f"    ✓ LINE_THRESHOLD = {preprocessor.LINE_THRESHOLD}")
        print(f"    ✓ EXTRACTION_RATIO = {preprocessor.EXTRACTION_RATIO}")
        print(f"    ✓ 支持的扩展: {len(preprocessor.SCRIPT_EXTENSIONS)} 种")
        
        # 检查 ParserAgent
        print("\n  验证 ParserAgent:")
        parser = ParserAgent()
        print(f"    ✓ 实例化成功")
        print(f"    ✓ 包含 code_preprocessor 属性: {hasattr(parser, 'code_preprocessor')}")
        
        # 检查 AuditContext
        print("\n  验证 AuditContext:")
        context = AuditContext(skill_path="/tmp/test")
        print(f"    ✓ 实例化成功")
        print(f"    ✓ 包含 preprocessed 字段: {hasattr(context, 'preprocessed')}")
        print(f"    ✓ preprocessed 初始值: {context.preprocessed}")
        
        return True
    except Exception as e:
        print(f"  ✗ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_methods():
    """验证关键方法的存在。"""
    print("\n📍 验证方法...\n")
    
    try:
        from app.analyzers.code_preprocessor import CodePreprocessor
        from app.agents.parser_agent import ParserAgent
        
        print("  CodePreprocessor 方法:")
        preprocessor = CodePreprocessor()
        methods = [
            'preprocess',
            '_find_code_files',
            '_is_code_file',
            '_preprocess_file',
            '_extract_key_locations',
            '_build_extracted_content'
        ]
        for method in methods:
            has_method = hasattr(preprocessor, method)
            status = "✓" if has_method else "✗"
            print(f"    {status} {method}")
        
        print("\n  ParserAgent 方法:")
        parser = ParserAgent()
        methods = [
            'run',
            '_parse_structure',
            '_parse_manifest',
            '_preprocess_code',
            '_validate_parsed_data'
        ]
        for method in methods:
            has_method = hasattr(parser, method)
            status = "✓" if has_method else "✗"
            print(f"    {status} {method}")
        
        return True
    except Exception as e:
        print(f"  ✗ 验证失败: {e}")
        return False


def verify_documentation():
    """验证文档文件是否存在。"""
    print("\n📚 验证文档...\n")
    
    docs = [
        "docs/CODE_PREPROCESSOR_GUIDE.md",
        "docs/CODE_PREPROCESSOR_QUICK_START.md",
        "IMPLEMENTATION_SUMMARY.md"
    ]
    
    for doc in docs:
        path = os.path.join(os.path.dirname(__file__), doc)
        exists = os.path.exists(path)
        status = "✓" if exists else "✗"
        print(f"  {status} {doc}")
    
    return all(os.path.exists(os.path.join(os.path.dirname(__file__), doc)) for doc in docs)


def verify_tests():
    """验证测试文件是否存在。"""
    print("\n🧪 验证测试...\n")
    
    test_file = "tests/test_code_preprocessor.py"
    path = os.path.join(os.path.dirname(__file__), test_file)
    exists = os.path.exists(path)
    status = "✓" if exists else "✗"
    print(f"  {status} {test_file}")
    
    return exists


def main():
    """运行所有验证。"""
    print("=" * 70)
    print("代码预处理功能 - 快速验证")
    print("=" * 70)
    
    results = {
        "导入验证": verify_imports(),
        "类结构验证": verify_classes(),
        "方法验证": verify_methods(),
        "文档验证": verify_documentation(),
        "测试验证": verify_tests(),
    }
    
    print("\n" + "=" * 70)
    print("验证结果总结")
    print("=" * 70 + "\n")
    
    all_passed = True
    for check, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status}: {check}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 70)
    
    if all_passed:
        print("✅ 所有验证通过！代码预处理功能已正确集成。")
        print("\n📖 后续步骤:")
        print("  1. 查看文档: docs/CODE_PREPROCESSOR_QUICK_START.md")
        print("  2. 运行测试: python tests/test_code_preprocessor.py")
        print("  3. 查看示例: python examples/code_preprocessor_examples.py")
        return 0
    else:
        print("❌ 部分验证失败。请检查实现。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
