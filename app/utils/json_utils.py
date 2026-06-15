"""JSON 工具。"""
import json

def dumps_pretty(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)
