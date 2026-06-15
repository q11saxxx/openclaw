"""置信度计算器。

规则描述：
- 评估当前决策的可信程度。
- 后续可结合规则命中数、证据一致性、模型稳定性进行计算。
"""


class ConfidenceCalculator:
    def calculate(self, merged_data: dict) -> float:
        """
        计算结论的置信度。
        - 静态规则命中的权重最高 (0.95)
        - LLM 语义分析的权重中等 (0.85)
        - 如果多个 Agent 同时发现同一个风险，置信度增加
        """
        all_issues = (merged_data["critical_issues"] + 
                      merged_data["high_issues"] + 
                      merged_data["medium_issues"])
        
        if not all_issues:
            return 0.8  # 默认通过的置信度

        total_conf = 0
        for issue in all_issues:
            source = issue.get("source", "")
            if "static" in source or "pattern" in source:
                total_conf += 0.95
            elif "semantic" in source or "llm" in source:
                total_conf += 0.85
            else:
                total_conf += 0.70
        
        avg_conf = total_conf / len(all_issues)
        # 如果有多方证据交叉验证，提升置信度
        if len(all_issues) > 1:
            avg_conf = min(0.99, avg_conf + 0.05)
            
        return round(avg_conf, 2)
