"""文件工具。

规则描述：
- 封装文件保存、读取、解压、哈希计算。
- 所有文件系统操作优先走本模块。
"""
from pathlib import Path

def ensure_dir(path: str) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
