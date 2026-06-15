"""时间工具。"""
from datetime import datetime

def now_iso() -> str:
    return datetime.utcnow().isoformat()
