"""本文件说明：扫描任务表模型，跟踪上传文件、状态和结果摘要。"""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class ScanTask(Base):
    """本类说明：后续承载扫描生命周期管理。"""

    __tablename__ = "scan_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, index=True)
    status: Mapped[str] = mapped_column(String(30), default="pending")
    artifact_name: Mapped[str] = mapped_column(String(255), default="")
