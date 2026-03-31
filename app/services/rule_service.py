"""规则服务。

规则描述：
- 用于统一管理规则装载、规则热更新和规则版本。
- 当前阶段可仅做占位，后续接 rules/rule_engine.py。
"""
class RuleService:
    def list_rules(self) -> list[dict]:
        return []
