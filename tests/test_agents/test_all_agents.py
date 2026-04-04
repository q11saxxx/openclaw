import os
import json
import logging
from dotenv import load_dotenv

# 导入核心组件
from app.core.context import AuditContext
# 导入所有 Agent
from app.agents.parser_agent import ParserAgent
from app.agents.static_security_agent import StaticSecurityAgent
from app.agents.semantic_audit_agent import SemanticAuditAgent
from app.agents.provenance_agent import ProvenanceAgent
from app.agents.decision_agent import DecisionAgent
from app.agents.report_agent import ReportAgent

# 配置日志，方便看到 Agent 内部的 logger.info 输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("IntegrationTest")

# 加载环境变量
load_dotenv()

def run_full_audit(target_path: str):
    logger.info(f"开始全链路安全审计演示")
    logger.info(f"目标 Skill 路径: {target_path}")
    print("\n" + "="*70)

    # 1. 初始化上下文
    # 确保你的 AuditContext 已经支持 .parsed 字典和 .findings 列表
    context = AuditContext(skill_path=target_path)
    
    # 模拟初始化 context 中的一些必要属性
    if not hasattr(context, "parsed"):
        context.parsed = {} 

    # 2. 构造流水线
    # 严格按照：解析 -> 扫描 -> 审计 -> 溯源 -> 决策 的逻辑
    pipeline = [
        ParserAgent(),            # 负责提取 SKILL.md 和 manifest 事实
        StaticSecurityAgent(),    # 负责扫描代码级漏洞
        SemanticAuditAgent(),     # 负责语义级意图识别 (DeepSeek 驱动)
        ProvenanceAgent(),        # 负责供应链/依赖分析
        DecisionAgent(),          # 负责汇总所有 Agent 的 Findings 并给出判决
        ReportAgent()             # 负责生成最终的审计报告（Markdown/HTML）
    ]

    # 3. 顺序执行 Agent
    print(f"{'智能体名称':<25} | {'状态':<10} | {'操作说明'}")
    print("-" * 70)
    
    for agent in pipeline:
        try:
            agent.run(context)
            status = "✅ 成功"
            note = f"已完成 {agent.name} 任务"
            print(f"{agent.name:<28} | {status:<10} | {note}")
        except Exception as e:
            print(f"{agent.name:<28} | ❌ 失败     | 错误: {str(e)}")

    # 4. 展示决策中心 (DecisionAgent) 的产出
    print("\n" + "="*70)
    print("🏆 最终审计决策报告 (Final Decision Report)")
    print("="*70)

    if hasattr(context, "decision"):
        d = context.decision
        print(f"【最终风险等级】: {d['risk_level']}")
        print(f"【系统处置建议】: {d['suggestion']}")
        print(f"【判定理由汇总】: {d['summary']}")
        print(f"【审计置信评分】: {d['confidence']}")
        print(f"【风险项统计表】: ")
        print(f"   - 严重 (Critical): {d['details']['critical_count']}")
        print(f"   - 高危 (High):     {d['details']['high_count']}")
        print(f"   - 中危 (Medium):   {d['details']['medium_count']}")
        print(f"   - 低危 (Low):      {d['details']['low_count']}")
    else:
        print("❌ 错误: DecisionAgent 未能生成决策数据，请检查 Findings 是否为空。")

    if hasattr(context, "report") and context.report:
        # 获取报告保存的路径（假设你在 ReportService 里记录了路径）
        # 如果你的 ReportAgent 只是把数据存入 context.report，你可以打印关键摘要
        print(f"✅ 报告代理运行成功！")
        print(f"   - 风险等级: {context.report.get('summary', {}).get('risk_level')}")
        print(f"   - 发现总数: {context.report.get('summary', {}).get('finding_count')}")
        print(f"   - 物理报告: 请检查项目根目录下的 data/reports/ 文件夹")
    else:
        print("❌ 错误: ReportAgent 未能生成报告数据。")

    # 5. 展示原始解析事实 (ParserAgent 的产物)
    print("\n" + "-"*70)
    print("📦 提取的 Skill 基础事实 (Metadata Facts):")
    manifest = context.parsed.get("manifest", {})
    print(f"   - Skill名称: {manifest.get('name')}")
    print(f"   - 版本号  : {manifest.get('version')}")
    print(f"   - 作者    : {manifest.get('author', '未知')}")
    print(f"   - 结构验证: {context.parsed.get('validation', {}).get('checks', {})}")

if __name__ == "__main__":
    # 使用你电脑上的真实路径
    # 建议先测试那个攻击性强的 SSH Skill 文件夹
    TARGET_SKILL = r"F:\skill test" 
    
    if os.path.exists(TARGET_SKILL):
        run_full_audit(TARGET_SKILL)
    else:
        print(f"错误: 找不到目标路径 {TARGET_SKILL}")
