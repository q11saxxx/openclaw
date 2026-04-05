"""审计任务接口。

规则描述：
- 负责触发审计、查询审计结果。
- 禁止在路由里直接调用 analyzer，必须通过 AuditService。
"""
from typing import Optional
from fastapi import APIRouter, Depends, Body, HTTPException
from app.api.deps import get_audit_service, get_skill_service, get_report_service
from app.services.audit_service import AuditService
from app.services.skill_service import SkillService
from app.services.report_service import ReportService

router = APIRouter()


@router.post("/run")
def run_audit(payload: dict = Body(...), service: AuditService = Depends(get_audit_service), skill_service: SkillService = Depends(get_skill_service), report_service: ReportService = Depends(get_report_service)) -> dict:
    """根据 skill_id 或 skill_path 发起一次同步审计（演示用）。

    请求体示例：{ "skill_id": "..." } 或 { "skill_path": "..." }
    返回：{ "audit_id": "audit_..." }
    """
    skill_id = payload.get('skill_id')
    skill_path = payload.get('skill_path')

    if skill_id:
        rec = skill_service.get_skill(skill_id)
        if not rec:
            raise HTTPException(status_code=404, detail='skill not found')
        skill_path = rec.get('path')

    if not skill_path:
        raise HTTPException(status_code=400, detail='skill_id or skill_path required')

    # 直接运行审计（同步），返回生成的 report id
    options = payload.get('options', {}) if isinstance(payload, dict) else {}
    ctx = service.run_audit(skill_path, options=options)
    report = ctx.get('report') or {}
    report_id = report.get('report_id')
    if not report_id:
        # 尝试根据 skill_name 找到最新的报告
        skill_name = report.get('metadata', {}).get('skill_name')
        if skill_name:
            reps = report_service.list_reports_by_skill_name(skill_name)
            if reps:
                report_id = reps[0]['id']

    return {"audit_id": report_id}


@router.get("/")
@router.get("")  # 同时支持无尾部斜杠的路径（兼容前端 /audits 请求）
def list_audits(report_service: ReportService = Depends(get_report_service)) -> dict:
    items = report_service.list_all_reports()
    return {"items": items, "total": len(items)}


@router.get("/{audit_id}")
def get_audit(audit_id: str, report_service: ReportService = Depends(get_report_service)) -> dict:
    # 返回审计报告的元信息（如果存在）或占位
    try:
        r = report_service.get_report(audit_id)
        return r
    except FileNotFoundError:
        return {"audit_id": audit_id, "status": "not_found"}
