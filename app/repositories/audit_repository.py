"""审计记录仓储。

规则描述：
- 只处理审计数据的存取，不包含业务决策。
"""
class AuditRepository:
    def save(self, payload: dict) -> dict:
        return payload
