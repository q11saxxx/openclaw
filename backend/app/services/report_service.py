"""本文件说明：报告服务层，负责中文摘要、导出模板和报告落盘。"""

class ReportService:
    """本类说明：后续生成在线预览、PDF、SARIF 等多种报告格式。"""

    def build_preview(self, scan_id: str) -> dict:
        """本方法说明：返回报告页最小预览结构。"""
        return {"scan_id": scan_id, "title": "待生成", "summary": "TODO"}
