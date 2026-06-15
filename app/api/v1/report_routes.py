"""报告接口。

规则描述：
- 负责报告详情、导出、下载入口。
- 报告生成必须由 ReportService 完成。
"""
from fastapi import APIRouter, Depends
from app.api.deps import get_report_service
from app.services.report_service import ReportService
from fastapi.responses import FileResponse, StreamingResponse
from fastapi import HTTPException
import io

router = APIRouter()

@router.get("/{audit_id}")
def get_report(audit_id: str, service: ReportService = Depends(get_report_service)) -> dict:
    return service.get_report(audit_id)


@router.get("/{audit_id}/ci-summary")
def get_report_ci_summary(audit_id: str, service: ReportService = Depends(get_report_service)) -> dict:
    """供流水线 / 脚本使用的轻量 JSON（事实字段，不含 UI 状态）。"""
    try:
        return service.build_ci_summary(audit_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="report not found")


@router.get("/{audit_id}/export-bundle")
def export_report_bundle(audit_id: str, service: ReportService = Depends(get_report_service)):
    """答辩材料 ZIP：报告 JSON/MD、CI 摘要、创新洞察子集、API 指引。"""
    try:
        data = service.build_competition_bundle_zip(audit_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="report not found")
    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="openclaw_bundle_{audit_id}.zip"'
        },
    )


@router.get("/{audit_id}/export")
def export_report(audit_id: str, format: str = 'json', service: ReportService = Depends(get_report_service)):
    try:
        path = service.export_report(audit_id, fmt=format)
        media_type = 'text/markdown' if path.suffix == '.md' else 'application/json'
        return FileResponse(path, media_type=media_type, filename=path.name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='report not found')
