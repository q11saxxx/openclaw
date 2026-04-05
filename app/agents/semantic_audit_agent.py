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
        super().__init__()  # 建议加上这行，初始化父类
        self.detector = PromptInjectionDetector()
        self.llm = LLMService()
        print(f"[{self.name}] Agent 初始化成功，已加载探测器和LLM服务")

    def run(self, context: AuditContext) -> None:
        skill_path = context.skill_path
        print(f"[{self.name}] 开始分析路径: {skill_path}")
        # 可通过 context.options 控制是否启用语义审计（例如在发起审计时传入 options: { semantic: false }）
        if isinstance(getattr(context, 'options', None), dict) and context.options.get('semantic') is False:
            print(f"[{self.name}] 语义审计已被禁用（options.semantic=False），跳过 LLM 分析")
            return

        # 1️⃣ 规则检测（第一道防线）
        rule_result = self.detector.detect(skill_path)

        if rule_result:
            print(f"[{self.name}] ⚡ 静态规则命中！正在启动强推理模型复核...")
            # 静态规则命中通常都是 High，所以必须记录为风险项
            context.add_finding(rule_result)

            # 👉 有规则命中 → 直接走强模型复核
            llm_result = self.llm.semantic_review(
                skill_path,
                force_strong=True,
            )
        else:
            print(f"[{self.name}] 🛡️ 静态规则未命中。启动轻量模型初筛...")
            # 👉 无规则命中 → 走“轻量模型初筛”
            llm_result = self.llm.semantic_review(
                skill_path,
                force_strong=False,
            )

        # 2️⃣ 智能处理 LLM 结果
        if llm_result:
            risk_level = str(llm_result.get("risk_level", "low")).lower()
            print(f"[{self.name}] 🤖 LLM 审计完成，模型判定等级: {risk_level}")

            # 💡 关键逻辑修改：
            # 只有当风险等级是 medium, high 或 critical 时，才作为“风险项”记录
            if risk_level in ["medium", "high", "critical"]:
                print(f"[{self.name}] ⚠️ 检测到语义风险，已加入审计报告。")
                context.add_finding(llm_result)
            else:
                # 如果是 low，我们认为该 Skill 是安全的
                # 不执行 context.add_finding，这样汇总时就不会显示“发现潜在风险项”
                print(f"[{self.name}] ✅ 审计通过：风险较低，不计入高危发现。")
        else:
            print(f"[{self.name}] ℹ️ LLM 未返回有效审计结果")
