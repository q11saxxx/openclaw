

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
            lv = (f.get("risk_level") or f.get("level") or f.get("severity") or "low").lower()
            if lv in severity_dist:
                severity_dist[lv] += 1
            elif lv == "info": 
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
        """保存 JSON 和 Markdown 格式报告"""
        output_dir = Path("data/reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 规范化文件名，去掉非法字符
        safe_name = "".join([c if c.isalnum() else "_" for c in report["metadata"]["skill_name"]])
        
        # 保存 JSON
        json_file = output_dir / f"audit_{safe_name}_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        # 生成并保存 Markdown
        self._generate_markdown(report, output_dir / f"audit_{safe_name}_{timestamp}.md")

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
            # 1. 基础字段提取与兜底
            level = (f.get('risk_level') or f.get('level') or f.get('severity') or 'LOW').upper()
            agent = f.get('agent') or 'security_engine'
            title = f.get('type') or f.get('title') or 'Security Finding'
            reason = f.get('reason') or f.get('description') or '检测到潜在风险点，需结合上下文复核。'
            evidence_data = f.get('evidence')

            md += f"### {i}. [{level}] {title}\n"
            md += f"- **来源智能体**: `{agent}`\n"
            md += f"- **描述**: {reason}\n"
            
            # 2. 智能证据排版逻辑
            if isinstance(evidence_data, list) and len(evidence_data) > 0:
                md += f"- **证据详情**: 发现 {len(evidence_data)} 处匹配：\n"
                for item in evidence_data[:15]: # 最多显示15条
                    if isinstance(item, dict):
                        # --- 情况 A: 静态扫描格式 (file, line, content) ---
                        file = item.get('file') or ""
                        line = item.get('line') or ""
                        content = item.get('content') or ""

                        # --- 情况 B: 语义静态探测格式 (matched_text, location) ---
                        if not content and item.get('matched_text'):
                            file = 'SKILL.md'
                            line = item.get('location') or '?'
                            content = item.get('matched_text')

                        # --- 情况 C: LLM 语义审计格式 (type, evidence, reason) ---
                        if not content and item.get('evidence'):
                            file = 'Semantic'
                            line = item.get('type') or 'Issue'
                            content = item.get('evidence')

                        # 兜底：如果还是没提取到
                        file = file or "unknown"
                        line = line or "?"
                        
                        # 清洗内容：去除换行符，限制长度，防止破坏 Markdown 结构
                        display_content = str(content).replace('\n', ' ').strip()
                        if len(display_content) > 200:
                            display_content = display_content[:200] + "..."

                        md += f"  - `[{file}:{line}]` : `{display_content}`\n"
                    else:
                        # 纯文本列表
                        md += f"  - `{str(item).strip()}`\n"
            
            elif isinstance(evidence_data, dict):
                # 证据本身是字典
                md += f"- **证据详情**: \n"
                for k, v in evidence_data.items():
                    val = str(v).replace('\n', ' ')
                    md += f"  - **{k}**: {val}\n"
            else:
                # 字符串或其他类型
                md += f"- **证据**: `{str(evidence_data).strip()}`\n"
            
            md += "\n---\n"

        # 4. 底部声明
        md += f"\n\n> 报告生成时间: {meta['scan_time']} | 审计引擎: {meta['engine_version']}\n"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md)
        logger.info(f"Markdown report generated: {file_path}")
