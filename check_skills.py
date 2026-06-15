import json
from pathlib import Path

# 读取 skills.json
data = json.loads(Path('data/skills.json').read_text(encoding='utf-8'))

print(f"Total skills: {len(data.get('items', []))}\n")

# 查看前3个skill
for i, skill in enumerate(data.get('items', [])[:3], 1):
    print(f"=== Skill {i} ===")
    print(f"Name: {skill.get('name')}")
    print(f"ID: {skill.get('id')}")
    print(f"Last Audit: {skill.get('last_audit')}")
    print(f"Quick Check: {skill.get('quick_check', {}).get('timestamp')}")
    print(f"Risk Level: {skill.get('risk_level')}")
    print()