"""权重配置。

规则描述：
- 放置不同证据源的基础权重。
- 不要把权重直接散落在打分函数里。
"""


# 证据来源权重 (Evidence Source Weights)
# 语义审计权重最高，因为大模型能理解深层意图
# 溯源权重次之，因为来源决定了信任基础
# 静态规则作为保底逻辑
SOURCE_WEIGHTS = {
    "static_security": 1.0,     # 静态扫描代理
    "semantic_audit": 1.2,      # 语义审计代理
    "provenance": 1.1,          # 来源溯源代理
    "parser": 0.5,              # 基础解析（通常作为参考）
}

# 风险严重程度分值 (Severity Base Scores)
SEVERITY_SCORES = {
    "critical": 50,
    "high": 25,
    "medium": 10,
    "low": 2,
    "info": 0
}

# 风险等级阈值 (Thresholds for Risk Levels)
# 最终得分超过多少分，判定为对应等级
RISK_THRESHOLD = {
    "CRITICAL": 45,
    "HIGH": 20,
    "MEDIUM": 8,
    "LOW": 0
}
