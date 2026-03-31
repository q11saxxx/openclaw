"""路径工具。

规则描述：
- 统一处理安全路径拼接与归一化。
- 需要特别防范目录穿越问题。
"""
from pathlib import Path

def normalize(path: str) -> str:
    return str(Path(path).resolve())
