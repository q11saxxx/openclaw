"""规则引擎。

规则描述：
- 规则统一从 builtin/ 和 custom/ 目录加载。
- 规则引擎只负责匹配与输出，不直接做最终风险裁决。
"""
class RuleEngine:
    def scan(self, path: str) -> list[dict]:
        return [
            {"title": "dangerous command rule placeholder", "level": "low", "evidence": path}
        ]
