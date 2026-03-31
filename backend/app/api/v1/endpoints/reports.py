"""本文件说明：报告接口，后续承接中文报告预览、PDF/SARIF 导出。"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/{scan_id}")
def preview_report(scan_id: str) -> dict:
    """本接口说明：预览指定扫描任务的报告摘要。"""
    return {"scan_id": scan_id, "message": "TODO: report preview"}
