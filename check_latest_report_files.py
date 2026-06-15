#!/usr/bin/env python3
"""检查最新报告的文件结构"""

import json
from pathlib import Path

def check_latest_report():
    """检查最新报告"""
    reports_dir = Path("data/reports")
    if not reports_dir.exists():
        print("报告目录不存在")
        return
    
    # 获取最新报告
    json_files = sorted(reports_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not json_files:
        print("没有找到报告文件")
        return
    
    latest = json_files[0]
    print(f"最新报告: {latest.name}")
    print("=" * 80)
    
    with open(latest, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 基本信息
    metadata = data.get('metadata', {})
    print(f"\nSkill名称: {metadata.get('skill_name', 'Unknown')}")
    print(f"AI预处理启用: {metadata.get('ai_preprocessing', False)}")
    
    # 预处理数据
    preprocessed = data.get('preprocessed', {})
    print(f"\n=== 预处理数据 ===")
    print(f"分析文件数: {preprocessed.get('files_analyzed', 0)}")
    print(f"预处理文件数: {preprocessed.get('files_preprocessed', 0)}")
    
    # Skill包文件列表
    parsed = data.get('parsed_facts', {})
    structure = parsed.get('structure', {})
    files = structure.get('files', [])
    
    print(f"\n=== Skill包包含的文件 ({len(files)}个) ===")
    for idx, f in enumerate(files, 1):
        path = f.get('path', 'Unknown')
        size = f.get('size', 0)
        suffix = Path(path).suffix
        print(f"{idx:2d}. {path} ({size} bytes) [{suffix}]")
    
    # 统计代码文件
    code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.rb', '.php', '.sh'}
    code_files = [f for f in files if Path(f.get('path', '')).suffix in code_extensions]
    
    print(f"\n=== 代码文件统计 ===")
    print(f"代码文件数: {len(code_files)}")
    if code_files:
        for f in code_files:
            print(f"  - {f.get('path')}")
    else:
        print("️  没有找到代码文件！这就是为什么分析文件数为0")
        print("   AI预处理器只处理代码文件（.py, .js等），不会处理配置文件")
    
    print("\n" + "=" * 80)
    if len(code_files) == 0:
        print("💡 解决方案:")
        print("   1. 查看 test-skill-demo 的报告（有代码文件）")
        print("   2. 或上传包含代码文件的Skill包重新测试")
        print("   报告路径: http://localhost:5173/report/audit_test_skill_demo_20260510_001302")

if __name__ == "__main__":
    check_latest_report()
