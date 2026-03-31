"""枚举定义。

规则描述：
- 放置风险等级、任务状态、动作建议等常量枚举。
- 业务中不要散落硬编码字符串。
"""
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    FINISHED = "finished"
    FAILED = "failed"
