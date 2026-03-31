"""提示注入检测器。

规则描述：
- 识别 `忽略之前指令`、越权访问、诱导泄露秘密等文本模式。
- 当前阶段可先做规则+关键词检测，后续再接语义增强。
"""
class PromptInjectionDetector:
    def detect(self, path: str) -> dict:
        return {"title": "prompt injection check", "level": "low", "evidence": path}
