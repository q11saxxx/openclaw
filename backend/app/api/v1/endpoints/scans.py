"""本文件说明：扫描任务接口，负责上传插件包、发起扫描、查询扫描结果。"""

from fastapi import APIRouter, UploadFile, File

router = APIRouter()


@router.post("/upload")
async def upload_and_scan(file: UploadFile = File(...)) -> dict:
    """本接口说明：上传 OpenClaw Skill zip 或依赖清单，后续调用 ScanService。"""
    return {"filename": file.filename, "message": "TODO: save and scan artifact"}


@router.get("/{scan_id}")
def get_scan(scan_id: str) -> dict:
    """本接口说明：根据 scan_id 查询扫描状态、原始结果和摘要。"""
    return {"scan_id": scan_id, "status": "pending", "message": "TODO: get scan detail"}
