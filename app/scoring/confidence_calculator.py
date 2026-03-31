"""置信度计算器。

规则描述：
- 评估当前决策的可信程度。
- 后续可结合规则命中数、证据一致性、模型稳定性进行计算。
"""
class ConfidenceCalculator:
    def calculate(self, merged: dict) -> float:
        findings = len(merged.get("findings", []))
        return min(0.5 + findings * 0.1, 0.99)
