"""报告接口。

规则描述：
- 负责报告详情、导出、下载入口。
- 报告生成必须由 ReportService 完成。
"""
from fastapi import APIRouter, Depends
from app.api.deps import get_report_service
from app.services.report_service import ReportService

router = APIRouter()

@router.get("/{audit_id}")
def get_report(audit_id: str, service: ReportService = Depends(get_report_service)) -> dict:
    return service.get_report(audit_id)
