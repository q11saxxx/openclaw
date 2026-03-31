"""数据库会话。

规则描述：
- 所有数据库连接与 Session 工厂在这里统一创建。
- 路由层不要直接操作 engine。
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings

engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
