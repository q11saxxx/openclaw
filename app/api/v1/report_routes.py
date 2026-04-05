"""报告接口。

规则描述：
- 负责报告详情、导出、下载入口。
- 报告生成必须由 ReportService 完成。
"""
from fastapi import APIRouter, Depends
from app.api.deps import get_report_service
from app.services.report_service import ReportService
from fastapi.responses import FileResponse
from fastapi import HTTPException

router = APIRouter()

@router.get("/{audit_id}")
def get_report(audit_id: str, service: ReportService = Depends(get_report_service)) -> dict:
    return service.get_report(audit_id)


@router.get("/{audit_id}/export")
def export_report(audit_id: str, format: str = 'json', service: ReportService = Depends(get_report_service)):
    try:
        path = service.export_report(audit_id, fmt=format)
        media_type = 'text/markdown' if path.suffix == '.md' else 'application/json'
        return FileResponse(path, media_type=media_type, filename=path.name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='report not found')
