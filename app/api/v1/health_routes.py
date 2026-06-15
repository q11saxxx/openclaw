"""健康检查接口。

规则描述：
- 仅提供存活探针与基础状态检查。
- 不要把复杂业务检查堆在此处，复杂依赖检查应拆分为单独诊断接口。
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def health() -> dict:
    return {"status": "ok"}
