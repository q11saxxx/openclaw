"""权重配置。

规则描述：
- 放置不同证据源的基础权重。
- 不要把权重直接散落在打分函数里。
"""
WEIGHTS = {
    "static": 1.0,
    "semantic": 1.2,
    "provenance": 1.1,
}
