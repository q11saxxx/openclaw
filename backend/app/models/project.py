"""本文件说明：项目表模型，保存项目分类、描述和创建时间。"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Project(Base):
    """本类说明：对应项目与插件管理模块的核心实体。"""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    project_type: Mapped[str] = mapped_column(String(50), default="openclaw-skill")
    description: Mapped[str] = mapped_column(String(255), default="")
