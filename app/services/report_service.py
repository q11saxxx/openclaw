# app/services/report_service.py

import datetime
import io
import json
import zipfile
from pathlib import Path
import logging
import copy

from app.utils.scan_metadata import (
    platform_engine_version,
    build_scan_block,
    collect_license_like_paths,
)
from app.utils.skill_innovation_signals import build_openclaw_innovation_bundle

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

        manifest = parsed.get("manifest", {}) or {}
        skill_path_str = data.get("skill_path") or ""
        scan_block = build_scan_block(data)
        supply_chain = {
            "license_files_in_archive": collect_license_like_paths(skill_path_str, parsed if isinstance(parsed, dict) else {}),
            "manifest_license_field": manifest.get("license"),
            "manifest_author_field": manifest.get("author"),
        }
        innovation = build_openclaw_innovation_bundle(data)

        report = {
            "metadata": {
                "skill_name": manifest.get("name") or Path(skill_path_str).name,
                "version": manifest.get("version", "unknown"),
                "author": manifest.get("author"),
                "skill_path": skill_path_str,
                "scan_time": scan_block.get("finished_at") or datetime.datetime.now().isoformat(),
                "engine_version": platform_engine_version(),
                "ai_preprocessing": bool(data.get("options", {}).get("ai_preprocessing", False)) or bool(data.get("preprocessed", {}).get("files_analyzed", 0) > 0),
                "scan": scan_block,
                "supply_chain": supply_chain,
                "openclaw_innovation": innovation,
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
            "preprocessed": data.get("preprocessed", {}),
            "parsed_facts": parsed
        }
        
        # 在保存到磁盘前，对可能非常大的字段做裁剪，避免浏览器/前端加载失败
        report_to_save = copy.deepcopy(report)
        try:
            pre = report_to_save.get('preprocessed') or {}
            files = pre.get('preprocessed_files') or []
            MAX_CONTENT = 20 * 1024  # 20KB
            for f in files:
                # 裁剪 preprocessed_content
                pc = f.get('preprocessed_content')
                if isinstance(pc, str) and len(pc) > MAX_CONTENT:
                    f['preprocessed_content'] = pc[:MAX_CONTENT] + '\n... (truncated) ...'

                # 裁剪 ai_summary 与 ai_recommendation 长文本（若存在）
                if 'ai_summary' in f and isinstance(f['ai_summary'], str) and len(f['ai_summary']) > 2000:
                    f['ai_summary'] = f['ai_summary'][:2000] + '... (truncated)'
                if 'ai_recommendation' in f and isinstance(f['ai_recommendation'], str) and len(f['ai_recommendation']) > 2000:
                    f['ai_recommendation'] = f['ai_recommendation'][:2000] + '... (truncated)'
        except Exception:
            # 若裁剪失败，也不要阻塞报告保存
            pass

        # 裁剪 findings 中可能的大块文本（例如 evidence.content、matched_text 等）
        try:
            findings = report_to_save.get('findings') or []
            for item in findings:
                if isinstance(item, dict):
                    # 对所有字符串字段做长度限制
                    for key, val in list(item.items()):
                        if isinstance(val, str) and len(val) > 4000:
                            item[key] = val[:4000] + '... (truncated)'

                    # 特别处理 evidence 字段
                    ev = item.get('evidence')
                    if isinstance(ev, list):
                        # 限制条目数量并裁剪每条中的长文本
                        new_ev = []
                        for e in ev[:20]:
                            if isinstance(e, dict):
                                for k2, v2 in list(e.items()):
                                    if isinstance(v2, str) and len(v2) > 2000:
                                        e[k2] = v2[:2000] + '... (truncated)'
                                new_ev.append(e)
                            else:
                                s = str(e)
                                if len(s) > 2000:
                                    s = s[:2000] + '... (truncated)'
                                new_ev.append(s)
                        item['evidence'] = new_ev
                    elif isinstance(ev, dict):
                        # 裁剪字典内的长字符串
                        for k2, v2 in list(ev.items()):
                            if isinstance(v2, str) and len(v2) > 2000:
                                ev[k2] = v2[:2000] + '... (truncated)'
        except Exception:
            pass

        # 裁剪 parsed_facts.structure 中的细节（例如完整文件列表或大块文本）
        try:
            pf = report_to_save.get('parsed_facts') or {}
            struct = pf.get('structure')
            if isinstance(struct, dict):
                # 如果存在 files 列表，替换为仅包含文件路径的简短列表
                files = struct.get('files')
                if isinstance(files, list):
                    short_files = []
                    for f in files[:500]:
                        if isinstance(f, dict) and f.get('path'):
                            short_files.append(f.get('path'))
                        elif isinstance(f, str):
                            short_files.append(f)
                    struct['files'] = short_files
        except Exception:
            pass

        # 保存到磁盘，返回保存路径以便外部使用 report_id
        json_file = self._save_report_to_disk(report_to_save)
        # 将生成的报告 id 注入返回结果，便于调用方引用
        if json_file:
            report['report_id'] = json_file.stem
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
        md_file = output_dir / f"audit_{safe_name}_{timestamp}.md"
        self._generate_markdown(report, md_file)

        return json_file

    def _generate_markdown(self, report: dict, file_path: Path):
        """生成人类可读的 Markdown 报告"""
        
        # 风险等级翻译映射（仅用于 Markdown 展示）
        LEVEL_MAP = {
            'critical': '严重',
            'high': '高危',
            'medium': '中危',
            'low': '低危',
            'info': '提示'
        }
        
        # 风险类型翻译映射（仅用于 Markdown 展示）
        TYPE_MAP = {
            'anonymous_publication': '匿名发布',
            'missing_license': '缺少许可证',
            'dangerous_command': '危险命令',
            'sensitive_data': '敏感数据',
            'insecure_dependency': '不安全依赖',
            'prompt_injection': '提示词注入',
            'code_injection': '代码注入',
            'path_traversal': '路径遍历',
            'privilege_escalation': '权限提升',
            'information_disclosure': '信息泄露',
            'high_entropy_string': '高熵可疑字符串',
            'url_surface_summary': 'URL 暴露面汇总',
            'openai_api_like': '疑似 API Key 形态',
            'aws_access_key_id_like': '疑似 AWS Access Key',
            'github_token_like': '疑似 GitHub Token',
            'slack_token_like': '疑似 Slack Token',
            'api_key_assignment': 'API Key 赋值',
            'bearer_token_like': 'Bearer 令牌形态',
            'jwt_like_blob': 'JWT 形态串',
        }
        
        def _translate_field_value(key: str, value: str) -> str:
            """翻译字段值为中文（仅用于 Markdown 展示）"""
            if not isinstance(value, str):
                return value
            
            lower_key = key.lower()
            lower_value = value.lower()
            
            # 如果是风险等级字段
            if any(k in lower_key for k in ['level', 'severity', '等级']):
                return LEVEL_MAP.get(lower_value, value)
            
            # 如果是风险类型字段
            if any(k in lower_key for k in ['type', '类型']):
                return TYPE_MAP.get(lower_value, value)
            
            return value
        
        def _translate_evidence_fields(obj):
            """递归翻译证据字典中的英文字段名和字段值为中文"""
            if isinstance(obj, dict):
                field_mapping = {
                    'type': '风险类型',
                    'level': '风险等级',
                    'message': '风险说明',
                    'evidence': '证据',
                    'risk_level': '风险等级',
                    'reason': '原因',
                    'description': '描述',
                    'file': '文件',
                    'line': '行号',
                    'content': '内容',
                    'package': '依赖包',
                    'version': '版本',
                    'source': '来源',
                    'url': '链接',
                    'recommendation': '修复建议',
                    'title': '标题',
                    'detail': '详情',
                    'item': '项目',
                    'module': '模块',
                    'path': '路径',
                    'command': '命令',
                    'pattern': '模式',
                    'agent': '来源智能体'
                }
                translated = {}
                for key, value in obj.items():
                    # 递归处理嵌套字典和列表
                    translated_key = field_mapping.get(key, key)
                    translated_value = _translate_evidence_fields(value)
                    
                    # 翻译字段值（如果是字符串）
                    if isinstance(translated_value, str):
                        translated_value = _translate_field_value(translated_key, translated_value)
                    
                    translated[translated_key] = translated_value
                return translated
            elif isinstance(obj, list):
                return [_translate_evidence_fields(item) for item in obj]
            else:
                return obj
        
        summ = report['summary']
        meta = report['metadata']
        parsed_facts = report.get('parsed_facts', {})
        manifest = parsed_facts.get('manifest', {}) 

        scan = meta.get("scan") or {}
        supply = meta.get("supply_chain") or {}
        lic_files = supply.get("license_files_in_archive") or []
        lic_lines = ", ".join(f"`{x}`" for x in lic_files[:12]) if lic_files else "_未发现常见许可证文件名_"
        dur = scan.get("duration_ms")
        dur_txt = f"{dur} ms" if isinstance(dur, int) else "_未知_"
        opts = scan.get("options_applied") or {}
        opts_txt = ", ".join(f"{k}={v}" for k, v in opts.items()) if opts else "_默认_"
        err_keys = list((scan.get("agent_errors") or {}).keys())

        oci = meta.get("openclaw_innovation") or {}
        ifp = oci.get("intent_fingerprint") or {}
        sigs = oci.get("declared_vs_surface") or []
        aut = oci.get("autonomy_surface") or {}
        sig_lines = "\n".join(
            f"- **[{s.get('severity', 'info')}]** {s.get('title', '')}: {s.get('detail', '')}" for s in sigs[:12]
        )
        if not sig_lines:
            sig_lines = "- _未触发声明—表面张力规则（或技能包结构信息不足）_"

        md = f"""# OpenClaw Skill 风险审计报告

## 1. 审计概述
- **Skill 名称**: {meta['skill_name']}
- **审计结果**: **{summ['risk_level']}**
- **处置建议**: `{summ['recommendation']}`
- **置信度**: {round(summ['confidence'] * 100, 2)}%
- **扫描路径**: `{meta['skill_path']}`

---

## 1.1 扫描可复现性（类 CI / 审计平台元数据）
- **引擎版本**: `{meta.get('engine_version', '')}`
- **扫描开始**: `{scan.get('started_at') or '-'}`
- **扫描结束**: `{scan.get('finished_at') or '-'}`
- **耗时**: {dur_txt}
- **基线对比**: {"是" if scan.get("baseline_used") else "否"}
- **请求选项快照**: {opts_txt}
- **Agent 失败记录**: {", ".join(err_keys) if err_keys else "无"}

---

## 1.2 OpenClaw 创新洞察（技能包视角）
> {oci.get("about", "")}

- **意图指纹 (short)**: `{ifp.get("short_id", "-")}`  （完整 SHA-256 见 JSON `metadata.openclaw_innovation.intent_fingerprint.full_hash`）
- **SKILL.md 参与指纹**: {"是" if ifp.get("skill_md_included") else "否"}
- **自主执行面**: 壳层/脚本类文件约 **{aut.get("shell_like_file_count", 0)}** 个，密度 **{aut.get("shell_density", 0)}** — _{aut.get("interpretation", "")}_
- **声明 vs 表面信号**:
{sig_lines}

---

## 1.5 供应链溯源摘要 ️
- **开发者身份**: `{manifest.get('author') or '⚠️ 匿名'}`
- **许可证声明**: `{manifest.get('license') or '❌ 未声明'}`
- **版本合规性**: `{manifest.get('version') or '未知'}`
- **信誉评估**: {" 风险 - 来源不可信" if not manifest.get('author') else "🟢 正常 - 身份已识别"}

---

## 2. 风险汇总
> {summ['overall_summary']}

| 严重程度 | 发现数量 |
| :--- | :--- |
| 严重 | {summ['severity_distribution']['critical']} |
| 高危 | {summ['severity_distribution']['high']} |
| 中危 | {summ['severity_distribution']['medium']} |
| 低危 | {summ['severity_distribution']['low']} |

---

## 3. 详细风险列表
"""
        if not report['findings']:
            md += "\n> ✅ 未发现明显安全风险。\n"
        
        for i, f in enumerate(report['findings'], 1):
            # 1. 基础字段提取与兜底
            level = (f.get('risk_level') or f.get('level') or f.get('severity') or 'low').lower()
            agent = f.get('agent') or '安全引擎'
            title = f.get('type') or f.get('title') or '安全发现'
            reason = f.get('reason') or f.get('description') or '检测到潜在风险点，需结合上下文复核。'
            evidence_data = f.get('evidence')
            
            # 翻译风险等级（仅用于 Markdown 展示，不影响 JSON 数据）
            level_map = {
                'critical': '严重',
                'high': '高危',
                'medium': '中危',
                'low': '低危',
                'info': '提示'
            }
            level_cn = level_map.get(level, level)
            
            # 翻译风险类型（仅用于 Markdown 展示，不影响 JSON 数据）
            type_map = {
                'anonymous_publication': '匿名发布',
                'missing_license': '缺少许可证',
                'dangerous_command': '危险命令',
                'sensitive_data': '敏感数据',
                'insecure_dependency': '不安全依赖',
                'prompt_injection': '提示词注入',
                'code_injection': '代码注入',
                'path_traversal': '路径遍历',
                'privilege_escalation': '权限提升',
                'information_disclosure': '信息泄露',
                'high_entropy_string': '高熵可疑字符串',
                'url_surface_summary': 'URL 暴露面汇总',
                'openai_api_like': '疑似 API Key 形态',
                'aws_access_key_id_like': '疑似 AWS Access Key',
                'github_token_like': '疑似 GitHub Token',
                'slack_token_like': '疑似 Slack Token',
                'api_key_assignment': 'API Key 赋值',
                'bearer_token_like': 'Bearer 令牌形态',
                'jwt_like_blob': 'JWT 形态串',
            }
            title_cn = type_map.get(title.lower(), title)

            md += f"### {i}. [{level_cn}] {title_cn}\n"
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
                            file = '语义分析'
                            line = item.get('type') or '问题'
                            content = item.get('evidence')

                        # 兜底：如果还是没提取到
                        file = file or "未知"
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
                # 证据本身是字典 - 使用递归翻译所有字段名
                md += f"- **证据详情**: \n"
                translated_evidence = _translate_evidence_fields(evidence_data)
                
                def _format_dict_to_md(d, indent=0):
                    """递归将字典格式化为 Markdown"""
                    result = ""
                    prefix = "  " * (indent + 1)
                    for key, value in d.items():
                        if isinstance(value, dict):
                            result += f"{prefix}- **{key}**: \n"
                            result += _format_dict_to_md(value, indent + 1)
                        elif isinstance(value, list):
                            result += f"{prefix}- **{key}**: \n"
                            for item in value:
                                if isinstance(item, dict):
                                    result += _format_dict_to_md(item, indent + 2)
                                else:
                                    result += f"{prefix}  - {item}\n"
                        else:
                            val = str(value).replace('\n', ' ')
                            result += f"{prefix}- **{key}**: {val}\n"
                    return result
                
                md += _format_dict_to_md(translated_evidence)
            else:
                # 字符串或其他类型
                md += f"- **证据**: `{str(evidence_data).strip()}`\n"
            
            md += "\n---\n"

        # 4. 底部声明
        md += f"\n\n> 报告生成时间: {meta['scan_time']} | 审计引擎: {meta['engine_version']}\n"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md)
        logger.info(f"Markdown report generated: {file_path}")

    def get_report(self, audit_id: str) -> dict:
        """读取并返回指定 audit_id 的 JSON 报告内容（data/reports/{audit_id}.json）。"""
        json_file = Path("data/reports") / f"{audit_id}.json"
        if not json_file.exists():
            raise FileNotFoundError(f"Report not found: {audit_id}")
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 注入运行时元信息，便于前端进度显示
            data.setdefault('report_id', audit_id)
            data['completed'] = True
            data['progress'] = 100
            # 提供有意义的审计日志
            data.setdefault('logs', [
                "审计流程已完成",
                "报告已生成并保存"
            ])
            return data

    def get_report_file_path(self, audit_id: str, fmt: str = 'json') -> Path | None:
        """返回报告的文件路径（json 或 md），不存在时返回 None。"""
        base = Path("data/reports")
        fmt = fmt.lower()
        if fmt not in ('json', 'md'):
            fmt = 'json'
        p = base / f"{audit_id}.{fmt}"
        return p if p.exists() else None

    def export_report(self, audit_id: str, fmt: str = 'json') -> Path:
        p = self.get_report_file_path(audit_id, fmt)
        if not p:
            raise FileNotFoundError(f"Report file not found: {audit_id}.{fmt}")
        return p

    def list_reports_by_skill_name(self, skill_name: str) -> list:
        """列出与 skill_name 对应的报告文件（基于 ReportService 中的命名规范）。

        返回结构示例：
        [ { "id": "audit_MySkill_20260405_1234", "json": "data/reports/..json", "md": "data/reports/..md", "created_at": "..." }, ... ]
        """
        base = Path("data/reports")
        if not base.exists():
            return []
        safe_name = "".join([c if c.isalnum() else "_" for c in (skill_name or "")])
        pattern = f"audit_{safe_name}_*"
        results = []
        for jf in sorted(base.glob(pattern + ".json"), key=lambda p: p.stat().st_mtime, reverse=True):
            mdf = jf.with_suffix('.md')
            stem = jf.stem
            created = jf.stat().st_mtime
            results.append({
                "id": stem,
                "json": str(jf),
                "md": str(mdf) if mdf.exists() else None,
                "created_at": datetime.datetime.fromtimestamp(created).isoformat()
            })
        return results

    def list_all_reports(self) -> list:
        """列出所有已生成的审计报告（按时间倒序）。

        返回列表项格式：{id, skill_name, created_at, risk_level, finding_count, json, md}
        """
        base = Path("data/reports")
        if not base.exists():
            return []
        out = []
        for jf in sorted(base.glob("audit_*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                with open(jf, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                meta = data.get('metadata', {})
                summ = data.get('summary', {})
                out.append({
                    'id': jf.stem,
                    'skill_name': meta.get('skill_name'),
                    'created_at': meta.get('scan_time') or datetime.datetime.fromtimestamp(jf.stat().st_mtime).isoformat(),
                    'risk_level': summ.get('risk_level'),
                    'finding_count': summ.get('finding_count', 0),
                    'confidence': summ.get('confidence', 0.0),
                    'status': 'completed',  # 已生成的报告都是已完成状态
                    'json': str(jf),
                    'md': str(jf.with_suffix('.md')) if jf.with_suffix('.md').exists() else None
                })
            except Exception:
                continue
        return out

    def build_ci_summary_from_report(self, r: dict, audit_id: str) -> dict:
        """与 HTTP ci-summary 一致的事实摘要，供流水线与答辩材料包复用。"""
        meta = r.get("metadata") or {}
        summ = r.get("summary") or {}
        scan = meta.get("scan") or {}
        supply = meta.get("supply_chain") or {}
        oci = meta.get("openclaw_innovation") or {}
        ifp = oci.get("intent_fingerprint") or {}
        aut = oci.get("autonomy_surface") or {}
        sigs = oci.get("declared_vs_surface") or []
        codes = [s.get("code") for s in sigs if isinstance(s, dict) and s.get("code")]
        return {
            "report_id": audit_id,
            "skill_name": meta.get("skill_name"),
            "risk_level": summ.get("risk_level"),
            "recommendation": summ.get("recommendation"),
            "confidence": summ.get("confidence"),
            "finding_count": summ.get("finding_count"),
            "severity_distribution": summ.get("severity_distribution"),
            "engine_version": meta.get("engine_version"),
            "scan_time": meta.get("scan_time"),
            "duration_ms": scan.get("duration_ms"),
            "baseline_used": scan.get("baseline_used"),
            "options_applied": scan.get("options_applied"),
            "agent_errors": scan.get("agent_errors"),
            "license_like_files": supply.get("license_files_in_archive"),
            "manifest_license": supply.get("manifest_license_field"),
            "intent_fingerprint_short": ifp.get("short_id"),
            "autonomy_surface_level": aut.get("level"),
            "autonomy_shell_like_count": aut.get("shell_like_file_count"),
            "declared_vs_surface_codes": codes,
        }

    def build_ci_summary(self, audit_id: str) -> dict:
        r = self.get_report(audit_id)
        return self.build_ci_summary_from_report(r, audit_id)

    def build_competition_bundle_zip(self, audit_id: str) -> bytes:
        """答辩材料 ZIP：完整报告 JSON/MD、CI 摘要、创新洞察子集、README 指引。"""
        r = self.get_report(audit_id)
        base = Path("data/reports")
        jf = base / f"{audit_id}.json"
        if not jf.exists():
            raise FileNotFoundError(f"Report not found: {audit_id}")
        ci = self.build_ci_summary_from_report(r, audit_id)
        meta = r.get("metadata") or {}
        oci = meta.get("openclaw_innovation") or {}
        innovation_export = {
            "intent_fingerprint": oci.get("intent_fingerprint"),
            "declared_vs_surface": oci.get("declared_vs_surface"),
            "autonomy_surface": oci.get("autonomy_surface"),
            "about": oci.get("about"),
        }
        readme = (
            "OpenClaw — 网络技术挑战赛 / 答辩材料包说明\n"
            "=====================================\n"
            f"报告 ID: {audit_id}\n"
            f"技能包: {meta.get('skill_name', '-')}\n\n"
            "目录：\n"
            f"  - {audit_id}_full_report.json  完整审计报告（机器可读）\n"
            f"  - {audit_id}_report.md         人类可读 Markdown（若生成时存在）\n"
            "  - ci_summary.json               流水线友好轻量摘要\n"
            "  - openclaw_innovation.json      意图指纹 / 声明-表面 / 自主执行面\n"
            "  - api_reference.txt             评委可现场调用的 API 列表\n\n"
            "现场演示建议：上传技能包 → 发起审计 → 打开报告详情 → 展示「创新洞察」与 SARIF 导出。\n"
        )
        api_ref = (
            "GET /api/health/competition          大赛就绪度与答辩提示\n"
            f"GET /api/reports/{audit_id}            完整报告 JSON\n"
            f"GET /api/reports/{audit_id}/ci-summary  CI 摘要\n"
            f"GET /api/reports/{audit_id}/export?format=json|md  单文件导出\n"
            f"GET /api/reports/{audit_id}/export-bundle 本答辩材料 ZIP\n"
        )
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(jf, arcname=f"openclaw_bundle/{audit_id}_full_report.json")
            mf = jf.with_suffix(".md")
            if mf.exists():
                zf.write(mf, arcname=f"openclaw_bundle/{audit_id}_report.md")
            zf.writestr(
                "openclaw_bundle/ci_summary.json",
                json.dumps(ci, ensure_ascii=False, indent=2),
            )
            zf.writestr(
                "openclaw_bundle/openclaw_innovation.json",
                json.dumps(innovation_export, ensure_ascii=False, indent=2),
            )
            zf.writestr("openclaw_bundle/README_答辩指引.txt", readme)
            zf.writestr("openclaw_bundle/api_reference.txt", api_ref)
        return buf.getvalue()
