from app.agents.base_agent import BaseAgent
from app.core.context import AuditContext
from app.analyzers.prompt_injection_detector import PromptInjectionDetector
from app.services.llm_service import LLMService

class SemanticAuditAgent(BaseAgent):
    """语义审计代理。

    规则描述：
    - 负责提示注入、越权诱导、社会工程类语义风险识别。
    - LLM 结果必须保留理由与证据摘要，不能只返回结论。
    """
    name = "semantic_audit"

  def __init__(self) -> None:
        super().__init__() # 建议加上这行，初始化父类
        self.detector = PromptInjectionDetector()
        self.llm = LLMService()
        print(f"[{self.name}] Agent 初始化成功，已加载探测器和LLM服务")

    def run(self, context: AuditContext) -> None:
        skill_path = context.skill_path
        print(f"[{self.name}] 开始分析路径: {skill_path}")

        # 1️⃣ 规则检测（第一道防线）
        rule_result = self.detector.detect(skill_path)

        if rule_result:
            print(f"[{self.name}] ⚡ 静态规则命中！正在启动强推理模型复核...")
            context.add_finding(rule_result)

            # 👉 有规则命中 → 直接走强模型复核
            llm_result = self.llm.semantic_review(
                skill_path,
                force_strong=True
            )
        else:
            print(f"[{self.name}] 🛡️ 静态规则未命中。启动轻量模型初筛...")
            # 👉 无规则命中 → 走“轻量模型初筛”
            llm_result = self.llm.semantic_review(
                skill_path,
                force_strong=False
            )

        if llm_result:
            print(f"[{self.name}] 🤖 LLM 审计完成，结果等级: {llm_result.get('risk_level')}")
            context.add_finding(llm_result)
        else:
            print(f"[{self.name}] ℹ️ LLM 未返回有效审计结果")
