"""本文件说明：自研规则扫描引擎，后续支持文本规则、OpenClaw 专项规则和 AST 规则。"""

from pathlib import Path


class RuleEngine:
    """本类说明：先返回示例结果，后续接入 YAML 规则加载与多扫描器。"""

    def scan(self, artifact_path: Path) -> list[dict]:
        """本方法说明：扫描上传的插件包或项目目录。"""
        return []
