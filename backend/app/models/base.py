"""本文件说明：定义 SQLAlchemy Base，供所有数据模型继承。"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """本类说明：所有 ORM 模型的共同基类。"""
