"""ORM 基础。

规则描述：
- 正式阶段统一在此定义 Base。
- 避免模型各自创建 Base 导致元数据分裂。
"""
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
