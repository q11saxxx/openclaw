#!/usr/bin/env python3
"""
查找包含代码的Skill包报告
"""

import json
from pathlib import Path
from datetime import datetime, timedelta

def find_reports_with_code():
    """查找包含代码文件的审计报告"""
    
    print("=" * 80)
    print(" 查找包含代码文件的Skill包报告")
    print("=" * 80)
    print()
    
    reports_dir = Path("data/reports")
    if not reports_dir.exists():
        print("❌ 报告目录不存在")
        return
    
    # 获取最近30分钟的报告
    now = datetime.now()
    thirty_min_ago = now - timedelta(minutes=30)
    
    found = []
    
    for json_file in sorted(reports_dir.glob("audit_*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        file_time = datetime.fromtimestamp(json_file.stat().st_mtime)
        
        if file_time < thirty_min_ago:
            break
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            preprocessed = data.get('preprocessed', {})
            files_analyzed = preprocessed.get('files_analyzed', 0)
            files_preprocessed = preprocessed.get('files_preprocessed', 0)
            skill_name = data.get('metadata', {}).get('skill_name', 'Unknown')
            
            if files_analyzed > 0 or files_preprocessed > 0:
                found.append({
                    'file': json_file.name,
                    'skill_name': skill_name,
                    'files_analyzed': files_analyzed,
                    'files_preprocessed': files_preprocessed,
                    'time': file_time.strftime('%H:%M:%S')
                })
        except Exception as e:
            continue
    
    if found:
        print(f"✅ 找到 {len(found)} 个包含代码的Skill包报告：\n")
        for idx, report in enumerate(found, 1):
            print(f"{idx}. {report['skill_name']}")
            print(f"   文件: {report['file']}")
            print(f"   时间: {report['time']}")
            print(f"   分析文件数: {report['files_analyzed']}")
            print(f"   预处理文件数: {report['files_preprocessed']}")
            print()
        
        print(" 建议:")
        print("   在前端查看这些报告，应该能看到AI预处理信息")
        print()
    else:
        print("❌ 没有找到包含代码的Skill包报告")
        print()
        print(" 可能的原因:")
        print("   1. 你选择的Skill包只有SKILL.md文件，没有代码文件")
        print("   2. 需要使用包含.py、.js等代码文件的Skill包")
        print()
        print("💡 解决方案:")
        print("   1. 上传一个包含代码文件的Skill包（ZIP格式）")
        print("   2. 或使用 test-skill-demo 进行测试")
        print()


if __name__ == "__main__":
    find_reports_with_code()
