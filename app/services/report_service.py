

import datetime
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ReportService:
    def build_report(self, data: dict) -> dict:
        """构建结构化报告"""
        decision = data.get("decision", {})
        findings = data.get("findings", [])
        parsed = data.get("parsed", {})
        
        # 统计风险分布
        severity_dist = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for f in findings:
            # 兼容性读取风险等级
            lv = (f.get("risk_level") or f.get("level") or f.get("severity") or "low").lower()
            if lv in severity_dist:
                severity_dist[lv] += 1
            elif lv == "info": # 兼容某些扫描器的 info 等级
                severity_dist["low"] += 1

        report = {
            "metadata": {
                "skill_name": parsed.get("manifest", {}).get("name") or Path(data.get("skill_path")).name,
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
                "overall_summary": decision.get("summary", "审计流程已完成，详细结果见下方列表。")
            },
            "findings": findings,
            "parsed_facts": parsed
        }
        
        # 保存到磁盘
        self._save_report_to_disk(report)
        return report

    def _save_report_to_disk(self, report: dict):
        output_dir = Path("data/reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        name = report["metadata"]["skill_name"].replace(" ", "_")
        
        # 保存 JSON
        json_file = output_dir / f"audit_{name}_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        # 生成并保存 Markdown
        self._generate_markdown(report, output_dir / f"audit_{name}_{timestamp}.md")

    def _generate_markdown(self, report: dict, file_path: Path):
        """生成人类可读的 Markdown 报告"""
        summ = report['summary']
        meta = report['metadata']

        md = f"""# OpenClaw Skill 供应链安全审计报告

## 1. 审计概述
- **Skill 名称**: {meta['skill_name']}
- **审计结果**: **{summ['risk_level']}**
- **处置建议**: `{summ['recommendation']}`
- **置信度**: {round(summ['confidence'] * 100, 2)}%
- **扫描路径**: `{meta['skill_path']}`

---

## 2. 风险汇总
> {summ['overall_summary']}

| 严重程度 | 发现数量 |
| :--- | :--- |
| Critical | {summ['severity_distribution']['critical']} |
| High | {summ['severity_distribution']['high']} |
| Medium | {summ['severity_distribution']['medium']} |
| Low | {summ['severity_distribution']['low']} |

---

## 3. 详细风险列表
"""
        if not report['findings']:
            md += "\n> ✅ 未发现明显安全风险。\n"
        
        for i, f in enumerate(report['findings'], 1):
            # --- 核心改进：强大的字段兜底提取 ---
            level = (f.get('risk_level') or f.get('level') or f.get('severity') or 'LOW').upper()
            agent = f.get('agent') or 'security_engine'
            title = f.get('type') or f.get('title') or 'Security Finding'
            reason = f.get('reason') or f.get('description') or '检测到潜在风险点，需结合上下文复核。'
            evidence = f.get('evidence')

            md += f"### {i}. [{level}] {title}\n"
            md += f"- **来源智能体**: `{agent}`\n"
            md += f"- **描述**: {reason}\n"
            
            # --- 核心改进：智能证据排版 ---
            if isinstance(evidence, list) and len(evidence) > 0:
                md += f"- **证据详情**: 发现 {len(evidence)} 处匹配：\n"
                for item in evidence[:10]: # 最多显示10条
                    if isinstance(item, dict):
                        file = item.get('file', 'unknown')
                        line = item.get('line', '?')
                        content = item.get('content', '').strip()
                        md += f"  - `[{file}:{line}]` : `{content}`\n"
                    else:
                        md += f"  - `{item}`\n"
            elif isinstance(evidence, dict):
                # 如果证据本身是个字典（比如语义分析结果）
                md += f"- **证据详情**: \n"
                for k, v in evidence.items():
                    md += f"  - **{k}**: {v}\n"
            else:
                # 字符串或其他
                md += f"- **证据**: `{evidence}`\n"
            
            md += "\n---\n"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md)
