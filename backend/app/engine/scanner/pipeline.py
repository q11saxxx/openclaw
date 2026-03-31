"""本文件说明：扫描流水线，编排文件预处理、自研规则、Trivy 与结果聚合。"""

from pathlib import Path
from app.engine.scanner.rule_engine import RuleEngine
from app.engine.trivy.client import TrivyClient


class ScanPipeline:
    """本类说明：把多种扫描能力串成统一流程，便于后续替换为异步任务。"""

    def __init__(self) -> None:
        self.rule_engine = RuleEngine()
        self.trivy_client = TrivyClient()

    def execute(self, artifact_path: Path) -> dict:
        """本方法说明：返回统一的扫描结果结构，前端和报告模块都依赖它。"""
        return {
            "artifact": str(artifact_path),
            "rule_findings": self.rule_engine.scan(artifact_path),
            "trivy": self.trivy_client.scan_filesystem(artifact_path),
            "summary": {"high": 0, "medium": 0, "low": 0}
        }
