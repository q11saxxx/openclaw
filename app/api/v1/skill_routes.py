"""Skill 相关接口。

负责 skill 上传、基础解析、元数据查看。
路由层只做参数校验和 service 调用。
"""
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks, HTTPException
from app.api.deps import get_skill_service, get_audit_service, get_report_service
from app.services.skill_service import SkillService
from app.services.audit_service import AuditService
from app.services.report_service import ReportService

router = APIRouter()


@router.get("/")
@router.get("")  # 同时支持无尾部斜杠的路径
def list_skills(page: int = 1, size: int = 10, q: Optional[str] = None, risk_level: Optional[str] = None, service: SkillService = Depends(get_skill_service)) -> dict:
    """分页列出 skills（支持简单搜索与按风险过滤）。"""
    return service.list_skills(page=page, size=size, q=q, risk_level=risk_level)


@router.get("/{skill_id}")
def get_skill_detail(skill_id: str, service: SkillService = Depends(get_skill_service), report_service: ReportService = Depends(get_report_service)) -> dict:
    """获取单个 skill 的详情，并返回可用的审计报告列表（若存在）。"""
    rec = service.get_skill(skill_id)
    if not rec:
        raise HTTPException(status_code=404, detail="skill not found")
    # attempt to parse for manifest/parsed facts
    parsed = {}
    try:
        parsed = service.parse_skill(rec.get('path'))
    except Exception:
        parsed = {}

    reports = report_service.list_reports_by_skill_name(rec.get('name') or '')
    return {**rec, 'parsed': parsed, 'reports': reports}


@router.post("/upload")
async def upload_skill(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    run_audit: bool = Form(False),
    service: SkillService = Depends(get_skill_service),
) -> dict:
    """接收 multipart 上传并保存，若 run_audit=True 则异步触发审计流程（调用 Orchestrator，包含 Decision/Report Agent）。"""
    saved = await service.save_uploaded_file(file)

    if run_audit:
        def _bg_run_audit(skill_id: str, skill_path: str):
            try:
                # instantiate AuditService lazily inside background task to avoid heavy initialization in request lifecycle
                from app.services.audit_service import AuditService

                audit_service = AuditService()
                res = audit_service.run_audit(skill_path)
                service.update_with_audit(skill_id, res)
            except Exception:
                # 保持容错，不抛到客户端
                pass

        background_tasks.add_task(_bg_run_audit, saved["id"], saved["path"])

    # 返回完整记录，包含可能的 quick_check 摘要
    return saved


@router.post("/parse")
def parse_skill(path: str, service: SkillService = Depends(get_skill_service)) -> dict:
    return service.parse_skill(path)
