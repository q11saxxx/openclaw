"""风险项模型。"""
from pydantic import BaseModel

class RiskItem(BaseModel):
    title: str
    level: str
    evidence: str | None = None
