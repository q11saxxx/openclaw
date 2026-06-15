from app.agents.base_agent import BaseAgent
from app.core.context import AuditContext
from app.services.report_service import ReportService
import logging

logger = logging.getLogger(__name__)


class ReportAgent(BaseAgent):
    """报告生成代理。

    规则描述：
    - 将上下文转换成用户可读、机器可读的报告。
    - 输出格式必须稳定，便于前端展示和后续导出。
    
    功能特性：
    - 集成 scoring 模块（RiskModel、ConfidenceCalculator、EvidenceMerger）
    - 生成结构化的审计报告，包含风险评估、信心度、发现详情
    - 支持多源证据融合和可解释性追踪
    - 报告格式遵循 OpenClaw 供应链安全审计规范
    
    报告结构：
    {
        "metadata": {              # 审计元数据
            "skill_path": str,
            "total_findings": int,
            "weights": dict
        },
        "summary": {               # 汇总信息
            "risk_level": str,           # high/medium/low
            "recommendation": str,       # manual_review_or_block/manual_review/allow
            "confidence": float,         # 0-1 置信度
            "finding_count": int,
            "severity_distribution": dict
        },
        "merged_evidence": dict,   # 融合后的证据集合
        "decision": dict,          # 审计决策
        "findings": list,          # 格式化的详细发现
        "provenance": dict,        # 证据来源追踪
        "quality_metrics": dict    # 报告质量指标
    }
    """
    name = "report"

    def __init__(self) -> None:
        self.report_service = ReportService()

    def run(self, context: AuditContext) -> None:
        """执行报告生成。
        
        Args:
            context: 审计上下文，包含 findings、decision、provenance 等
            
        Side effects:
            - 将生成的报告写入 context.report
            - 输出格式：dict，包含用户可读和机器可读的信息
        """
        try:
            # 构建完整审计报告，集成 scoring 模块的分析结果
            context.report = self.report_service.build_report(context.to_dict())
            logger.info(
                f"Report generated for skill: {context.skill_path}, "
                f"Risk Level: {context.report.get('summary', {}).get('risk_level', 'unknown')}, "
                f"Findings: {context.report.get('summary', {}).get('finding_count', 0)}"
            )
        except Exception as e:
            logger.error(f"Failed to generate report: {str(e)}")
            # 返回错误报告而非抛出异常，保证管道继续执行
            context.report = {
                "error": str(e),
                "status": "failed",
                "summary": {
                    "risk_level": "unknown",
                    "recommendation": "manual_review",
                    "confidence": 0.0,
                }
            }
