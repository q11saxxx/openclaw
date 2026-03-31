"""审计模型。"""
from pydantic import BaseModel

class AuditRequest(BaseModel):
    skill_path: str

class AuditResponse(BaseModel):
    audit_id: str
    status: str
