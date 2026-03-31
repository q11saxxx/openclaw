"""报告模型。"""
from pydantic import BaseModel

class ReportSummary(BaseModel):
    audit_id: str
    level: str
    recommendation: str
