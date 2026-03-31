"""总路由注册。

规则描述：
- 只负责聚合子路由，不写具体业务处理。
- 所有接口必须按版本归档到 `api/v1/`。
"""
from fastapi import APIRouter
from app.api.v1.skill_routes import router as skill_router
from app.api.v1.audit_routes import router as audit_router
from app.api.v1.report_routes import router as report_router
from app.api.v1.health_routes import router as health_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(skill_router, prefix="/skills", tags=["skills"])
api_router.include_router(audit_router, prefix="/audits", tags=["audits"])
api_router.include_router(report_router, prefix="/reports", tags=["reports"])
