"""应用启动入口。

规则描述：
- 仅负责创建应用实例、注册路由、挂载中间件和启动时初始化。
- 不在本文件中编写复杂业务逻辑。
- 所有审计流程必须经由 service -> core -> agent 链路完成。
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.config.settings import settings

# 禁用 FastAPI 的自动尾部斜杠重定向
app = FastAPI(
    title=settings.app_name, 
    debug=settings.debug,
    redirect_slashes=False  # ← 关键配置：禁用自动重定向
)

# 配置 CORS 允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
def root() -> dict:
    return {"message": settings.app_name, "status": "ok"}
