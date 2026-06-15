"""报告表模型。

规则描述：
- 当前为占位模型，正式阶段请补充字段、索引和外键关系。
"""
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class ReportRecord(Base):
    __tablename__ = "report_record"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
