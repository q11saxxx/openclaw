#!/usr/bin/env python3
"""
AI预处理功能 - 快速验证脚本
检查前后端集成是否完整
"""

import os
import sys
from pathlib import Path

def check_backend():
    """检查后端配置"""
    print("=" * 80)
    print("🔧 后端配置检查")
    print("=" * 80)
    print()
    
    checks = []
    
    # 1. 检查CodePreprocessor
    try:
        from app.analyzers.code_preprocessor import CodePreprocessor
        preprocessor = CodePreprocessor()
        checks.append(("✅", "CodePreprocessor导入成功"))
        
        # 检查preprocess方法签名
        import inspect
        sig = inspect.signature(preprocessor.preprocess)
        if 'use_ai' in sig.parameters:
            checks.append(("✅", "preprocess方法支持use_ai参数"))
        else:
            checks.append(("❌", "preprocess方法缺少use_ai参数"))
    except Exception as e:
        checks.append(("❌", f"CodePreprocessor导入失败: {e}"))
    
    # 2. 检查ParserAgent
    try:
        from app.agents.parser_agent import ParserAgent
        agent = ParserAgent()
        checks.append(("✅", "ParserAgent导入成功"))
        
        # 检查是否有code_preprocessor属性
        if hasattr(agent, 'code_preprocessor'):
            checks.append(("✅", "ParserAgent包含code_preprocessor"))
        else:
            checks.append(("❌", "ParserAgent缺少code_preprocessor"))
    except Exception as e:
        checks.append(("❌", f"ParserAgent导入失败: {e}"))
    
    # 3. 检查ReportService
    try:
        from app.services.report_service import ReportService
        service = ReportService()
        checks.append(("✅", "ReportService导入成功"))
        
        # 检查build_report方法
        if hasattr(service, 'build_report'):
            checks.append(("✅", "ReportService包含build_report方法"))
        else:
            checks.append(("❌", "ReportService缺少build_report方法"))
    except Exception as e:
        checks.append(("❌", f"ReportService导入失败: {e}"))
    
    # 4. 检查LLMService
    try:
        from app.services.llm_service import LLMService
        llm = LLMService()
        checks.append(("✅", "LLMService导入成功"))
        
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if api_key:
            checks.append(("✅", "DEEPSEEK_API_KEY已设置"))
        else:
            checks.append(("⚠️", "DEEPSEEK_API_KEY未设置（将使用降级模式）"))
    except Exception as e:
        checks.append(("❌", f"LLMService导入失败: {e}"))
    
    # 打印结果
    for status, message in checks:
        print(f"   {status} {message}")
    
    print()
    # DEEPSEEK_API_KEY未设置不算失败，只是警告
    return all(s in ["✅", "⚠️"] for s, _ in checks)


def check_frontend():
    """检查前端文件"""
    print("=" * 80)
    print("🎨 前端配置检查")
    print("=" * 80)
    print()
    
    frontend_root = Path("frontend/src")
    checks = []
    
    # 1. 检查审计发起页面
    new_audit_file = frontend_root / "views" / "audit" / "New.vue"
    if new_audit_file.exists():
        content = new_audit_file.read_text(encoding='utf-8')
        
        if 'ai_preprocessing' in content:
            checks.append(("✅", "审计发起页面包含ai_preprocessing字段"))
        else:
            checks.append(("❌", "审计发起页面缺少ai_preprocessing字段"))
        
        if 'AI 预处理' in content or 'AI预处理' in content:
            checks.append(("✅", "审计发起页面有AI预处理UI文本"))
        else:
            checks.append(("❌", "审计发起页面缺少AI预处理UI文本"))
        
        if 'options:' in content and 'ai_preprocessing:' in content:
            checks.append(("✅", "审计发起页面正确传递options参数"))
        else:
            checks.append(("❌", "审计发起页面未正确传递options参数"))
    else:
        checks.append(("❌", "审计发起页面文件不存在"))
    
    # 2. 检查报告详情页面
    report_detail_file = frontend_root / "views" / "report" / "Detail.vue"
    if report_detail_file.exists():
        content = report_detail_file.read_text(encoding='utf-8')
        
        if 'aiPreprocessingEnabled' in content:
            checks.append(("✅", "报告详情页包含aiPreprocessingEnabled计算属性"))
        else:
            checks.append(("❌", "报告详情页缺少aiPreprocessingEnabled"))
        
        if 'preprocessedFiles' in content:
            checks.append(("✅", "报告详情页包含preprocessedFiles计算属性"))
        else:
            checks.append(("❌", "报告详情页缺少preprocessedFiles"))
        
        if 'ai_summary' in content:
            checks.append(("✅", "报告详情页显示AI摘要"))
        else:
            checks.append(("❌", "报告详情页未显示AI摘要"))
        
        if 'ai_recommendation' in content:
            checks.append(("✅", "报告详情页显示AI建议"))
        else:
            checks.append(("❌", "报告详情页未显示AI建议"))
    else:
        checks.append(("❌", "报告详情页文件不存在"))
    
    # 打印结果
    for status, message in checks:
        print(f"   {status} {message}")
    
    print()
    return all(s == "✅" for s, _ in checks)


def check_data_flow():
    """检查数据流"""
    print("=" * 80)
    print("🔄 数据流检查")
    print("=" * 80)
    print()
    
    checks = []
    
    try:
        from app.core.pipeline import AuditPipeline
        
        # 运行一次完整的审计
        pipeline = AuditPipeline()
        result = pipeline.run(
            skill_path='test-skill-demo',
            options={'ai_preprocessing': True}
        )
        
        # 检查结果结构
        if 'preprocessed' in result:
            checks.append(("✅", "Pipeline返回结果包含preprocessed字段"))
            
            preprocessed = result['preprocessed']
            required_fields = ['files_analyzed', 'files_preprocessed', 'preprocessed_files', 'statistics']
            missing = [f for f in required_fields if f not in preprocessed]
            
            if not missing:
                checks.append(("✅", "preprocessed包含所有必需字段"))
            else:
                checks.append(("❌", f"preprocessed缺少字段: {', '.join(missing)}"))
        else:
            checks.append(("❌", "Pipeline返回结果缺少preprocessed字段"))
        
        # 检查report结构
        if 'report' in result:
            report = result['report']
            
            if 'metadata' in report:
                metadata = report['metadata']
                if 'ai_preprocessing' in metadata:
                    checks.append(("✅", "report.metadata包含ai_preprocessing字段"))
                else:
                    checks.append(("❌", "report.metadata缺少ai_preprocessing字段"))
            else:
                checks.append(("❌", "report缺少metadata字段"))
        else:
            checks.append(("❌", "结果缺少report字段"))
        
    except Exception as e:
        checks.append(("❌", f"数据流测试失败: {e}"))
    
    # 打印结果
    for status, message in checks:
        print(f"   {status} {message}")
    
    print()
    return all(s == "✅" for s, _ in checks)


def main():
    """主函数"""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "AI预处理功能 - 快速验证" + " " * 33 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    backend_ok = check_backend()
    frontend_ok = check_frontend()
    dataflow_ok = check_data_flow()
    
    print("=" * 80)
    print("📊 验证总结")
    print("=" * 80)
    print()
    print(f"   后端配置: {'✅ 通过' if backend_ok else '❌ 失败'}")
    print(f"   前端配置: {'✅ 通过' if frontend_ok else '❌ 失败'}")
    print(f"   数据流:   {'✅ 通过' if dataflow_ok else '❌ 失败'}")
    print()
    
    if backend_ok and frontend_ok and dataflow_ok:
        print("🎉 所有检查通过！AI预处理功能已完全集成！")
        print()
        print("💡 下一步:")
        print("   1. 启动后端: uvicorn app.main:app --reload")
        print("   2. 启动前端: cd frontend && npm run dev")
        print("   3. 访问: http://localhost:5173/audit/new")
        print("   4. 勾选'AI预处理'选项并开始审计")
        print()
        return 0
    else:
        print("⚠️  部分检查失败，请查看上述错误信息")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
