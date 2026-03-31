"""审计任务接口。

规则描述：
- 负责触发审计、查询审计结果。
- 禁止在路由里直接调用 analyzer，必须通过 AuditService。
"""
from fastapi import APIRouter, Depends
from app.api.deps import get_audit_service
from app.services.audit_service import AuditService

router = APIRouter()

@router.post("/run")
def run_audit(skill_path: str, service: AuditService = Depends(get_audit_service)) -> dict:
    return service.run_audit(skill_path)

@router.get("/{audit_id}")
def get_audit(audit_id: str) -> dict:
    return {"audit_id": audit_id, "status": "placeholder"}
