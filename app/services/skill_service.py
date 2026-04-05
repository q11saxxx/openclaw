"""Skill 服务。

负责 skill 文件级操作：保存、元数据管理、列表查询等。
此服务使用 SkillRepository 进行简单持久化（data/skills.json）。
"""
from app.analyzers.skill_parser import SkillParser
from app.repositories.skill_repository import SkillRepository
from app.config.settings import settings
from pathlib import Path
from fastapi import UploadFile
import hashlib
import datetime
from app.analyzers.script_analyzer import ScriptAnalyzer
from app.analyzers.file_permission_analyzer import FilePermissionAnalyzer
from app.analyzers.prompt_injection_detector import PromptInjectionDetector


class SkillService:
    def __init__(self) -> None:
        self.parser = SkillParser()
        self.repo = SkillRepository()

    async def save_uploaded_file(self, upload_file: UploadFile) -> dict:
        """保存上传文件到磁盘并在仓储中创建记录，返回记录。"""
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)

        filename = upload_file.filename or "uploaded"
        unique_prefix = hashlib.sha1((filename + str(datetime.datetime.utcnow().timestamp())).encode()).hexdigest()
        dest = upload_dir / f"{unique_prefix}_{filename}"

        content = await upload_file.read()
        with open(dest, "wb") as f:
            f.write(content)

        sha256 = hashlib.sha256(content).hexdigest()
        record = {
            "name": filename,
            "path": str(dest),
            "filename": filename,
            "size": len(content),
            "sha256": sha256,
            "status": "uploaded",
        }
        saved = self.repo.save(record)

        # 进行轻量级的快速检测（synchronous quick checks）
        try:
            script_analyzer = ScriptAnalyzer()
            fileperm_analyzer = FilePermissionAnalyzer()
            prompt_detector = PromptInjectionDetector()

            script_res = script_analyzer.analyze(str(dest))
            fileperm_res = fileperm_analyzer.analyze(str(dest))
            prompt_res = prompt_detector.detect(str(dest))

            # 收集发现并计算最高风险等级
            levels = []
            if script_res and isinstance(script_res, dict):
                levels.append(script_res.get('level', 'low'))
            if fileperm_res and isinstance(fileperm_res, dict):
                levels.append(fileperm_res.get('level', 'low'))
            if prompt_res and isinstance(prompt_res, dict):
                levels.append(prompt_res.get('risk_level', 'low'))

            severity_rank = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
            max_rank = 0
            for lv in levels:
                max_rank = max(max_rank, severity_rank.get((lv or '').lower(), 1))
            rank_map = {4: 'critical', 3: 'high', 2: 'medium', 1: 'low'}
            quick_level = rank_map.get(max_rank, 'low')

            quick_summary = {
                'timestamp': datetime.datetime.utcnow().isoformat(),
                'level': quick_level,
                'findings': [],
                'summary': {
                    'script': script_res.get('summary') if isinstance(script_res, dict) else {},
                    'file_permission': fileperm_res.get('summary') if isinstance(fileperm_res, dict) else {},
                    'prompt_injection': {'found': bool(prompt_res)}
                }
            }

            # 合并证据（简要），限制数量以免过大
            if isinstance(script_res, dict) and script_res.get('evidence'):
                quick_summary['findings'].extend([{'agent': 'script', 'evidence': e} for e in script_res.get('evidence')[:10]])
            if isinstance(fileperm_res, dict) and fileperm_res.get('evidence'):
                quick_summary['findings'].extend([{'agent': 'file_permission', 'evidence': e} for e in fileperm_res.get('evidence')[:10]])
            if isinstance(prompt_res, dict):
                quick_summary['findings'].append({'agent': 'prompt_injection', 'evidence': prompt_res})

            # 写回仓储
            self.repo.update(saved.get('id'), {'quick_check': quick_summary})
            # refresh saved
            saved = self.repo.get(saved.get('id'))
        except Exception:
            # 快速检查失败不能阻塞上传，保持容错
            pass

        return saved

    def list_skills(self, page: int = 1, size: int = 10, q: str | None = None, risk_level: str | None = None) -> dict:
        return self.repo.list(page=page, size=size, q=q, risk_level=risk_level)

    def get_skill(self, skill_id: str) -> dict | None:
        return self.repo.get(skill_id)

    def update_with_audit(self, skill_id: str, audit_result: dict) -> dict | None:
        # write last audit summary to the skill record
        summary = audit_result.get("decision") or audit_result.get("report") or audit_result
        updates = {
            "last_audit": {
                "risk_level": summary.get("risk_level") if isinstance(summary, dict) else None,
                "confidence": summary.get("confidence") if isinstance(summary, dict) else None,
            },
            "status": "audited",
        }
        return self.repo.update(skill_id, updates)

    def parse_skill(self, path: str) -> dict:
        return {"path": path, "parsed": self.parser.parse(path)}
