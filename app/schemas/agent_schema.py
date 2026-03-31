"""Agent 通信模型。

规则描述：
- 定义 agent 输入输出的共享载荷结构。
- 减少 agent 之间直接传递松散 dict 带来的维护成本。
"""
from pydantic import BaseModel

class AgentResult(BaseModel):
    agent: str
    ok: bool = True
    payload: dict = {}
