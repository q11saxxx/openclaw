"""摘要与签名工具。

规则描述：
- 可用于文件哈希、完整性校验和后续签名验证。
"""
import hashlib

def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
