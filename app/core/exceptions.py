"""自定义异常。

规则描述：
- 将业务异常统一收口，便于 API 层做一致化错误响应。
"""
class AuditError(Exception):
    """审计过程基础异常。"""

class SkillParseError(AuditError):
    """Skill 解析失败。"""
