"""Skill 相关模型。

规则描述：
- 统一定义 skill 元数据与结构化响应模型。
- 正式开发中所有接口入参/出参都应优先使用 schema。
"""
from pydantic import BaseModel

class SkillMeta(BaseModel):
    name: str | None = None
    version: str | None = None
    source: str | None = None
