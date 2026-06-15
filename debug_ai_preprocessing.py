#!/usr/bin/env python3
"""
调试AI预处理功能 - 检查报告数据结构
"""

import json
from pathlib import Path

def debug_latest_report():
    """检查最新生成的报告"""
    
    print("=" * 80)
    print(" AI预处理功能调试")
    print("=" * 80)
    print()
    
    # 查找最新的报告文件
    reports_dir = Path("data/reports")
    if not reports_dir.exists():
        print("❌ 报告目录不存在")
        return
    
    json_files = sorted(reports_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if not json_files:
        print("❌ 没有找到报告文件")
        return
    
    latest_report = json_files[0]
    print(f"📄 最新报告: {latest_report.name}")
    print()
    
    # 读取报告
    with open(latest_report, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    # 检查metadata
    print("=" * 80)
    print("📋 metadata 字段检查")
    print("=" * 80)
    metadata = report.get('metadata', {})
    print(f"   ai_preprocessing: {metadata.get('ai_preprocessing', '❌ 字段不存在')}")
    print(f"   skill_name: {metadata.get('skill_name', 'N/A')}")
    print()
    
    # 检查preprocessed
    print("=" * 80)
    print("📦 preprocessed 字段检查")
    print("=" * 80)
    preprocessed = report.get('preprocessed', {})
    
    if not preprocessed:
        print("   ❌ preprocessed字段为空")
    else:
        print(f"   ✅ files_analyzed: {preprocessed.get('files_analyzed', 0)}")
        print(f"   ✅ files_preprocessed: {preprocessed.get('files_preprocessed', 0)}")
        print(f"   ✅ ai_preprocessing_enabled: {preprocessed.get('ai_preprocessing_enabled', False)}")
        
        stats = preprocessed.get('statistics', {})
        if stats:
            print(f"   ✅ 平均压缩比: {stats.get('average_compression_ratio', 0):.2%}")
        
        files = preprocessed.get('preprocessed_files', [])
        if files:
            print(f"   ✅ 预处理文件数: {len(files)}")
            for idx, file_info in enumerate(files[:3], 1):
                print(f"      {idx}. {file_info.get('file_path', 'Unknown')}")
                print(f"         行数: {file_info.get('extracted_lines', 0)}/{file_info.get('original_lines', 0)}")
                if file_info.get('ai_summary'):
                    print(f"         AI摘要: {file_info.get('ai_summary')[:80]}...")
    
    print()
    print("=" * 80)
    print("💡 诊断结果")
    print("=" * 80)
    print()
    
    if not metadata.get('ai_preprocessing'):
        print("❌ 问题: metadata.ai_preprocessing = False")
        print("   原因: 前端可能没有勾选'AI预处理'选项")
        print("   解决: 重新发起审计，确保勾选'AI预处理'复选框")
    elif not preprocessed:
        print("⚠️  问题: preprocessed字段为空")
        print("   原因: 没有文件超过1000行，不需要预处理")
        print("   解决: 这是正常行为，或者使用包含大文件的Skill包测试")
    elif not preprocessed.get('ai_preprocessing_enabled'):
        print("️  问题: ai_preprocessing_enabled = False")
        print("   原因: 虽然勾选了AI预处理，但没有API密钥，使用了降级模式")
        print("   解决: 设置DEEPSEEK_API_KEY环境变量以启用真正的AI分析")
    else:
        print("✅ AI预处理功能正常工作！")
    
    print()


if __name__ == "__main__":
    debug_latest_report()
