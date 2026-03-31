"""Skill 相关接口。

规则描述：
- 负责 skill 上传、基础解析、元数据查看。
- 路由层只做参数校验和 service 调用。
"""
from fastapi import APIRouter, Depends
from app.api.deps import get_skill_service
from app.services.skill_service import SkillService

router = APIRouter()

@router.get("/")
def list_skills() -> dict:
    return {"items": [], "message": "skill list placeholder"}

@router.post("/parse")
def parse_skill(path: str, service: SkillService = Depends(get_skill_service)) -> dict:
    return service.parse_skill(path)
