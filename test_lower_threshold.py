#!/usr/bin/env python3
"""
测试降低阈值后的AI预处理功能
"""

import json
from pathlib import Path
from app.core.pipeline import AuditPipeline

def test_lower_threshold():
    """测试降低阈值后的效果"""
    
    print("=" * 80)
    print(" 测试降低阈值后的AI预处理功能")
    print("=" * 80)
    print()
    print(" LINE_THRESHOLD已降低到50行")
    print()
    
    # 运行审计
    print("运行审计...")
    pipeline = AuditPipeline()
    result = pipeline.run(
        skill_path='test-skill-demo',
        options={
            'semantic': True,
            'static_security': True,
            'dependency_check': True,
            'ai_preprocessing': True
        }
    )
    
    print(" 审计完成")
    print()
    
    # 检查结果
    preprocessed = result.get('preprocessed', {})
    
    print("=" * 80)
    print(" 预处理结果")
    print("=" * 80)
    print()
    print(f" files_analyzed: {preprocessed.get('files_analyzed', 0)}")
    print(f" files_preprocessed: {preprocessed.get('files_preprocessed', 0)}")
    print(f" ai_preprocessing_enabled: {preprocessed.get('ai_preprocessing_enabled', False)}")
    print()
    
    stats = preprocessed.get('statistics', {})
    if stats:
        print(f" 原始总行数: {stats.get('total_original_lines', 0)}")
        print(f" 提取总行数: {stats.get('total_extracted_lines', 0)}")
        ratio = stats.get('average_compression_ratio', 0)
        print(f" 平均压缩比: {ratio:.1%}")
        print()
    
    files = preprocessed.get('preprocessed_files', [])
    if files:
        print(f" 预处理了 {len(files)} 个文件:")
        print()
        for idx, file_info in enumerate(files[:5], 1):
            print(f"  {idx}. {file_info.get('file_path', 'Unknown')}")
            print(f"     行数: {file_info.get('extracted_lines', 0)}/{file_info.get('original_lines', 0)}")
            print(f"     压缩比: {file_info.get('extraction_ratio', 0):.1%}")
            print()
    else:
        print(" 没有文件需要预处理")
        print()
    
    # 保存报告
    report = result.get('report', {})
    metadata = report.get('metadata', {})
    
    output_dir = Path("data/reports")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    skill_name = metadata.get('skill_name', 'unknown').replace(' ', '_')
    timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = output_dir / f"test_lower_threshold_{skill_name}_{timestamp}.json"
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
    
    print("=" * 80)
    print(" 报告已保存")
    print("=" * 80)
    print(f" 文件: {json_file}")
    print()
    
    if preprocessed.get('files_preprocessed', 0) > 0:
        print(" 降低阈值成功！现在可以看到预处理效果了")
    else:
        print(" 仍然没有文件需要预处理，可能需要检查Skill包内容")


if __name__ == "__main__":
    test_lower_threshold()
