"""风险评分模型。

规则描述：
- 输入为融合后的证据集合，输出风险等级与处置建议。
- 正式阶段应把权重、阈值与解释逻辑拆分配置化。
"""


class RiskModel:
    def score(self, merged_data: dict) -> dict:
        """
        核心决策逻辑：
        1. 存在任何 CRITICAL 证据 -> 最终风险为 CRITICAL -> 拒绝安装 (Reject)
        2. 存在 HIGH 证据 -> 最终风险为 HIGH -> 强制人工复核 (Review)
        3. 仅有 MEDIUM 证据 -> 最终风险为 MEDIUM -> 警告并观察 (Warn)
        4. 仅有 LOW 或无证据 -> 最终风险为 LOW -> 允许运行 (Allow)
        """
        if merged_data["critical_issues"]:
            return {
                "final_risk_level": "CRITICAL",
                "disposal_suggestion": "REJECT",
                "reason": f"检测到 {len(merged_data['critical_issues'])} 项严重安全威胁，已直接拦截。"
            }
        
        if merged_data["high_issues"]:
            return {
                "final_risk_level": "HIGH",
                "disposal_suggestion": "MANUAL_REVIEW",
                "reason": f"存在 {len(merged_data['high_issues'])} 项高危风险，必须经安全员人工审计后方可发布。"
            }
        
        if merged_data["medium_issues"]:
            return {
                "final_risk_level": "MEDIUM",
                "disposal_suggestion": "WARN",
                "reason": "存在中等风险项，建议在受限沙箱环境中运行并开启监控。"
            }
            
        return {
            "final_risk_level": "LOW",
            "disposal_suggestion": "ALLOW",
            "reason": "未发现明显安全威胁，Skill 行为符合常规业务逻辑。"
        }
