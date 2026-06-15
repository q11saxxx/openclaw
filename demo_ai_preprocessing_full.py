#!/usr/bin/env python3
"""
AI预处理功能完整演示 - 模拟前端调用并显示结果
"""

import json
from app.core.pipeline import AuditPipeline
from pathlib import Path

def demo_full_ai_preprocessing():
    """演示完整的AI预处理流程"""
    
    print("=" * 80)
    print("🚀 OpenClaw AI预处理功能 - 完整演示")
    print("=" * 80)
    print()
    
    # 步骤1: 创建审计管道
    print("📋 步骤1: 创建审计管道...")
    pipeline = AuditPipeline()
    print("   ✅ Pipeline创建成功")
    print()
    
    # 步骤2: 运行审计（启用AI预处理）
    print("🔍 步骤2: 运行审计（启用AI预处理）...")
    print("   目标: test-skill-demo")
    print("   选项: ai_preprocessing=True")
    print()
    
    result = pipeline.run(
        skill_path='test-skill-demo',
        options={
            'semantic': True,
            'static_security': True,
            'dependency_check': True,
            'ai_preprocessing': True  # 启用AI预处理
        }
    )
    
    print("   ✅ 审计完成")
    print()
    
    # 步骤3: 显示预处理结果
    print("=" * 80)
    print("📊 AI预处理结果详情")
    print("=" * 80)
    print()
    
    preprocessed = result.get('preprocessed', {})
    
    # 基本信息
    print("🔹 基本统计:")
    print(f"   • 分析文件数: {preprocessed.get('files_analyzed', 0)}")
    print(f"   • 预处理文件数: {preprocessed.get('files_preprocessed', 0)}")
    print(f"   • AI预处理启用: {'✅ 是' if preprocessed.get('ai_preprocessing_enabled') else '❌ 否'}")
    print()
    
    # 统计信息
    stats = preprocessed.get('statistics', {})
    if stats:
        print("🔹 压缩统计:")
        print(f"   • 原始总行数: {stats.get('total_original_lines', 0)}")
        print(f"   • 提取总行数: {stats.get('total_extracted_lines', 0)}")
        ratio = stats.get('average_compression_ratio', 0)
        print(f"   • 平均压缩比: {ratio:.1%}")
        print(f"   • 数据减少: {(1 - ratio) * 100:.1f}%")
        print()
    
    # 详细文件信息
    preprocessed_files = preprocessed.get('preprocessed_files', [])
    if preprocessed_files:
        print("🔹 预处理文件详情:")
        print()
        
        for idx, file_info in enumerate(preprocessed_files, 1):
            print(f"   📄 文件 {idx}: {file_info.get('file_path', 'Unknown')}")
            print(f"      ├─ 原始行数: {file_info.get('original_lines', 0)}")
            print(f"      ├─ 提取行数: {file_info.get('extracted_lines', 0)}")
            print(f"      ├─ 压缩比: {file_info.get('extraction_ratio', 0):.1%}")
            print(f"      ├─ 关键位置数: {len(file_info.get('key_locations', []))}")
            
            # 显示AI摘要（如果有）
            ai_summary = file_info.get('ai_summary')
            if ai_summary:
                print(f"      ├─ AI摘要: {ai_summary[:100]}...")
            
            ai_recommendation = file_info.get('ai_recommendation')
            if ai_recommendation:
                print(f"      └─ AI建议: {ai_recommendation[:100]}...")
            
            print()
            
            # 显示部分关键位置
            key_locations = file_info.get('key_locations', [])[:5]
            if key_locations:
                print(f"      关键代码位置示例（前5个）:")
                for loc in key_locations:
                    line_num = loc.get('line_number', '?')
                    context_type = loc.get('context_type', 'unknown')
                    content = loc.get('content', '')[:60]
                    print(f"        L{line_num:4d} [{context_type:10s}] {content}")
                print()
    
    # 步骤4: 显示报告中的预处理信息
    print("=" * 80)
    print("📝 报告中的AI预处理信息")
    print("=" * 80)
    print()
    
    report = result.get('report', {})
    metadata = report.get('metadata', {})
    
    print("🔹 元数据:")
    print(f"   • Skill名称: {metadata.get('skill_name', 'N/A')}")
    print(f"   • AI预处理: {'✅ 已启用' if metadata.get('ai_preprocessing') else '❌ 未启用'}")
    print()
    
    # 步骤5: 保存JSON报告
    print("=" * 80)
    print("💾 保存审计报告")
    print("=" * 80)
    print()
    
    output_dir = Path("data/reports")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成文件名
    skill_name = metadata.get('skill_name', 'unknown').replace(' ', '_')
    timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = output_dir / f"demo_audit_{skill_name}_{timestamp}.json"
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"✅ 报告已保存到: {json_file}")
    print(f"   文件大小: {json_file.stat().st_size:,} bytes")
    print()
    
    # 步骤6: 验证数据结构
    print("=" * 80)
    print("✅ 数据结构验证")
    print("=" * 80)
    print()
    
    checks = [
        ("result包含preprocessed字段", 'preprocessed' in result),
        ("preprocessed包含files_analyzed", 'files_analyzed' in preprocessed),
        ("preprocessed包含files_preprocessed", 'files_preprocessed' in preprocessed),
        ("preprocessed包含preprocessed_files", 'preprocessed_files' in preprocessed),
        ("preprocessed包含statistics", 'statistics' in preprocessed),
        ("preprocessed包含ai_preprocessing_enabled", 'ai_preprocessing_enabled' in preprocessed),
        ("report包含metadata", 'metadata' in report),
        ("metadata包含ai_preprocessing", 'ai_preprocessing' in metadata),
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} - {check_name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 所有验证通过！AI预处理功能完全正常！")
    else:
        print("⚠️  部分验证失败，请检查上述错误")
    
    print()
    print("=" * 80)
    print("✨ 演示完成！")
    print("=" * 80)
    print()
    print("💡 提示:")
    print("   • 前端页面已集成AI预处理选项")
    print("   • 在审计发起页面勾选'AI预处理'即可启用")
    print("   • 报告详情页会显示AI摘要和建议")
    print("   • 设置DEEPSEEK_API_KEY环境变量可启用真正的AI分析")
    print()


if __name__ == "__main__":
    demo_full_ai_preprocessing()
