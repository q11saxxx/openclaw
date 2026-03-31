"""本文件说明：扫描业务编排层，负责保存文件、调用引擎、写回数据库。"""

from pathlib import Path
from app.engine.scanner.pipeline import ScanPipeline


class ScanService:
    """本类说明：承接上传扫描主流程，是 MVP 最重要的服务。"""

    def __init__(self) -> None:
        self.pipeline = ScanPipeline()

    def run_scan(self, artifact_path: Path) -> dict:
        """本方法说明：统一调用自研规则、Trivy 与报告聚合。"""
        return self.pipeline.execute(artifact_path)
