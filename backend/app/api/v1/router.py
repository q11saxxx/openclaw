"""本文件说明：统一注册 v1 版本接口，避免 main.py 过重。"""

from fastapi import APIRouter
from app.api.v1.endpoints import dashboard, projects, reports, scans

api_router = APIRouter()
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(scans.router, prefix="/scans", tags=["scans"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
