"""本文件说明：Trivy 客户端封装，后续负责 SBOM 生成、漏洞扫描和配置扫描。"""

from pathlib import Path


class TrivyClient:
    """本类说明：把命令行 Trivy 调用包装成 Python 方法。"""

    def scan_filesystem(self, target: Path) -> dict:
        """本方法说明：开发阶段先返回占位结构，后续替换为真实 subprocess 调用。"""
        return {"status": "todo", "target": str(target)}
