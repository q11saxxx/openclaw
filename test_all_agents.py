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

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("IntegrationTest")

# 加载环境变量
load_dotenv()

def run_full_audit(target_path: str):
    logger.info(f"开始全链路安全审计演示 (含深度供应链分析)")
    logger.info(f"目标 Skill 路径: {target_path}")
    print("\n" + "="*75)

    # 1. 初始化上下文
    context = AuditContext(skill_path=target_path)
    
    if not hasattr(context, "parsed"):
        context.parsed = {} 

    # 2. 构造流水线
    pipeline = [
        ParserAgent(),            # 提取元数据
        StaticSecurityAgent(),    # 代码级漏洞扫描
        SemanticAuditAgent(),     # 语义意图审计
        ProvenanceAgent(),        # 🔥 供应链/依赖/第三方库分析 (包含新功能)
        DecisionAgent(),          # 风险决策汇总
        ReportAgent()             # 生成最终报告
    ]

    # 3. 顺序执行 Agent
    print(f"{'智能体名称':<25} | {'状态':<10} | {'操作说明'}")
    print("-" * 75)
    
    for agent in pipeline:
        try:
            agent.run(context)
            status = "✅ 成功"
            note = f"已完成 {agent.name} 任务"
            print(f"{agent.name:<28} | {status:<10} | {note}")
        except Exception as e:
            print(f"{agent.name:<28} | ❌ 失败     | 错误: {str(e)}")

    # 4. 展示决策中心 (DecisionAgent) 的产出
    print("\n" + "="*75)
    print("🏆 最终审计决策报告 (Final Decision Report)")
    print("="*75)

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
        print("❌ 错误: DecisionAgent 未能生成决策数据。")

    # 5. 展示原始解析事实
    print("\n" + "-"*75)
    print("📦 提取的 Skill 基础事实 (Metadata Facts):")
    manifest = context.parsed.get("manifest", {})
    print(f"   - Skill名称: {manifest.get('name')}")
    print(f"   - 版本号  : {manifest.get('version')}")
    print(f"   - 作者    : {manifest.get('author', '未知')}")

    # 6. 🔥 新增：展示供应链与第三方库审计细节 (Deep Dependency Insights)
    print("\n" + "-"*75)
    print("⛓️ 供应链与深度依赖审计详情 (Supply Chain Insights):")
    if hasattr(context, "provenance"):
        prov = context.provenance
        stats = prov.get("stats", {})
        
        print(f"   - 识别总依赖数: {stats.get('total_dependencies', 0)}")
        print(f"   - 代码库引用数: {stats.get('code_reference_count', 0)}")
        print(f"   - 提取外部连接: {stats.get('unique_urls', 0)}")
        
        # 专门过滤出来自 provenance 代理的高危风险项
        supply_chain_risks = [
            f for f in context.findings 
            if f.get("agent") == "provenance" and f.get("risk_level") in ["high", "critical"]
        ]
        
        if supply_chain_risks:
            print(f"   - 🔴 关键供应链风险警报 ({len(supply_chain_risks)}项):")
            for risk in supply_chain_risks:
                print(f"     > [{risk['type'].upper()}] {risk['reason']}")
        else:
            print(f"   - ✅ 供应链基础环境未发现严重威胁。")

    # 7. 展示报告生成状态
    print("\n" + "="*75)
    print("📝 报告生成状态 (Report Status)")
    print("="*75)
    if hasattr(context, "report") and context.report:
        print(f"✅ 报告代理运行成功！")
        print(f"   - 物理报告: 请检查 data/reports/ 目录下的最新 Markdown 文件")
    else:
        print("❌ 错误: ReportAgent 未能生成报告。")

if __name__ == "__main__":
    # 使用包含恶意依赖（如 reqests 或 event-stream）的测试文件夹
    TARGET_SKILL = r"F:\skill test" 
    
    if os.path.exists(TARGET_SKILL):
        run_full_audit(TARGET_SKILL)
    else:
        print(f"错误: 找不到目标路径 {TARGET_SKILL}")