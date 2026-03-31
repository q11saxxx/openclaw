"""本文件说明：报告预览与导出模块的响应模型。"""

from pydantic import BaseModel


class ReportPreview(BaseModel):
    """本模型说明：向前端报告页返回报告标题和摘要。"""

    scan_id: str
    title: str
    summary: str
