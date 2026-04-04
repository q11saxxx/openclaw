"""报告服务。

规则描述：
- 报告的构建、渲染、导出统一在这里完成。
- 可逐步扩展 HTML / Markdown / JSON 等输出格式。
"""


import datetime
import json
from pathlib import Path

class ReportService:
    def build_report(self, data: dict) -> dict:
        """构建结构化报告"""
        decision = data.get("decision", {})
        findings = data.get("findings", [])
        parsed = data.get("parsed", {})
        
        # 1. 统计风险分布
        severity_dist = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for f in findings:
            lv = f.get("risk_level", "low").lower()
            if lv in severity_dist:
                severity_dist[lv] += 1

        # 2. 组装符合规范的报告结构
        report = {
            "metadata": {
                "skill_name": parsed.get("manifest", {}).get("name", "Unknown"),
                "version": parsed.get("manifest", {}).get("version", "unknown"),
                "skill_path": data.get("skill_path"),
                "scan_time": datetime.datetime.now().isoformat(),
                "engine_version": "OpenClaw-Risk-Platform-V1"
            },
            "summary": {
                "risk_level": decision.get("risk_level", "UNKNOWN"),
                "recommendation": decision.get("suggestion", "MANUAL_REVIEW"),
                "confidence": decision.get("confidence", 0.0),
                "finding_count": len(findings),
                "severity_distribution": severity_dist,
                "overall_summary": decision.get("summary", "No summary available.")
            },
            "findings": findings,
            "parsed_facts": parsed,
            "decision_logic": decision
        }
        
        # 3. 可选：自动将报告持久化到磁盘
        self._save_report_to_disk(report)
        
        return report

    def _save_report_to_disk(self, report: dict):
        """将报告保存为 JSON 和 Markdown 文件"""
        output_dir = Path("data/reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成唯一文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        name = report["metadata"]["skill_name"]
        
        # 保存 JSON
        json_file = output_dir / f"audit_{name}_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        # 生成并保存 Markdown (演示神器)
        self._generate_markdown(report, output_dir / f"audit_{name}_{timestamp}.md")

    def _generate_markdown(self, report: dict, file_path: Path):
        """生成人类可读的 Markdown 报告"""
        md = f"""# OpenClaw Skill 供应链安全审计报告

## 1. 审计概述
- **Skill 名称**: {report['metadata']['skill_name']}
- **版本**: {report['metadata']['version']}
- **审计结果**: **{report['summary']['risk_level']}**
- **处置建议**: `{report['summary']['recommendation']}`
- **置信度**: {report['summary']['confidence'] * 100}%

---

## 2. 风险汇总
> {report['summary']['overall_summary']}

| 严重程度 | 发现数量 |
| :--- | :--- |
| Critical | {report['summary']['severity_distribution']['critical']} |
| High | {report['summary']['severity_distribution']['high']} |
| Medium | {report['summary']['severity_distribution']['medium']} |
| Low | {report['summary']['severity_distribution']['low']} |

---

## 3. 详细风险列表
"""
        for i, f in enumerate(report['findings'], 1):
            md += f"### [{f.get('risk_level', 'LOW').upper()}] {f.get('type', 'Unknown Issue')}\n"
            md += f"- **来源智能体**: {f.get('agent')}\n"
            md += f"- **描述**: {f.get('reason')}\n"
            if f.get('evidence'):
                md += f"- **证据**: `{json.dumps(f.get('evidence'), ensure_ascii=False)}`\n"
            md += "\n"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md)
