"""风险服务。

规则描述：
- 用于封装风险项转换、过滤、聚合等业务。
- 不直接替代 scoring 模块的评分职责。
"""
class RiskService:
    def normalize(self, findings: list[dict]) -> list[dict]:
        return findings
