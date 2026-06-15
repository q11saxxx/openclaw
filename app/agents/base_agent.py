"""Agent 基类。

规则描述：
- 所有 agent 必须继承本类并实现 `run(context)`。
- agent 只负责自己的职责边界，不跨层调用无关模块。
"""
from abc import ABC, abstractmethod
from app.core.context import AuditContext

class BaseAgent(ABC):
    name: str = "base"

    @abstractmethod
    def run(self, context: AuditContext) -> None:
        raise NotImplementedError
