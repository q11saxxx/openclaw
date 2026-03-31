"""本文件说明：FastAPI 入口，负责挂载中间件、路由和健康检查。"""

from fastapi import FastAPI
from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/")
def health_check() -> dict:
    """本接口说明：提供最基础的服务存活检查。"""
    return {"message": f"{settings.app_name} is running"}
