"""本文件说明：仪表盘接口，给前端提供风险总览、趋势统计和图表数据。"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/overview")
def get_overview() -> dict:
    """本接口说明：返回风险总览卡片与统计值。"""
    return {
        "projects": 0,
        "scans": 0,
        "high_risks": 0,
        "message": "TODO: dashboard overview"
    }
