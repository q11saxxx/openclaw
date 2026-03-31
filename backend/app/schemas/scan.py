"""本文件说明：扫描任务的响应模型，便于前端稳定接收数据。"""

from pydantic import BaseModel


class ScanSummary(BaseModel):
    """本模型说明：返回扫描状态和风险数量摘要。"""

    scan_id: str
    status: str
    high: int = 0
    medium: int = 0
    low: int = 0
