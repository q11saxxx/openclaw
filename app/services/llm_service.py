"""LLM 调用封装。

规则描述：
- 所有模型调用必须从本服务进入，禁止在 agent 内直接散落调用。
- 必须保留模型输入摘要、输出摘要和失败回退逻辑。
"""
class LLMService:
    def semantic_review(self, skill_path: str) -> dict:
        return {
            "title": "semantic review placeholder",
            "level": "medium",
            "evidence": f"LLM mock review for {skill_path}",
        }
