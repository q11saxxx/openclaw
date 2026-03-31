"""本文件说明：规则命中项模型，保存自研规则扫描结果。"""

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Finding(Base):
    """本类说明：后续用于展示恶意行为、权限滥用和配置问题。"""

    __tablename__ = "scan_findings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scan_task_id: Mapped[int] = mapped_column(Integer, index=True)
    severity: Mapped[str] = mapped_column(String(20), index=True)
    rule_id: Mapped[str] = mapped_column(String(50), index=True)
    file_path: Mapped[str] = mapped_column(String(255), default="")
    message: Mapped[str] = mapped_column(Text)
