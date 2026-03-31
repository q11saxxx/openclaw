"""报告服务。

规则描述：
- 报告的构建、渲染、导出统一在这里完成。
- 可逐步扩展 HTML / Markdown / JSON 等输出格式。
"""
from typing import Any

class ReportService:
    def build_report(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "summary": "placeholder report",
            "decision": payload.get("decision", {}),
            "finding_count": len(payload.get("findings", [])),
        }

    def get_report(self, audit_id: str) -> dict:
        return {"audit_id": audit_id, "report": "placeholder"}
