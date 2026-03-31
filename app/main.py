"""应用启动入口。

规则描述：
- 仅负责创建应用实例、注册路由、挂载中间件和启动时初始化。
- 不在本文件中编写复杂业务逻辑。
- 所有审计流程必须经由 service -> core -> agent 链路完成。
"""
from fastapi import FastAPI
from app.api.router import api_router
from app.config.settings import settings

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.include_router(api_router)

@app.get("/")
def root() -> dict:
    return {"message": settings.app_name, "status": "ok"}
