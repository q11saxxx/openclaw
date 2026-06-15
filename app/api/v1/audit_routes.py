"""审计任务接口。

规则描述：
- 负责触发审计、查询审计结果。
- 禁止在路由里直接调用 analyzer，必须通过 AuditService。
"""
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Body, HTTPException
from app.api.deps import get_audit_service, get_skill_service, get_report_service
from app.services.audit_service import AuditService
from app.services.skill_service import SkillService
from app.services.report_service import ReportService

router = APIRouter()


@router.get("/stats")
def get_dashboard_stats(
    skill_service: SkillService = Depends(get_skill_service),
    report_service: ReportService = Depends(get_report_service)
) -> dict:
    """获取 Dashboard 统计数据"""
    # 获取所有 skills
    all_skills = skill_service.list_skills(page=1, size=10000)
    skills = all_skills.get('items', [])
    
    # 获取所有报告（返回的是列表，不是字典）
    reports = report_service.list_all_reports()
    
    # 计算统计数据
    total_skills = len(skills)
    total_reports = len(reports)
    
    # 统计高风险 skill 数量
    high_risk_count = sum(1 for s in skills if s.get('risk_level') in ['high', 'critical'])
    
    # 统计今日审计数量
    today = datetime.now().date()
    today_audits = 0
    for r in reports:
        created_at = r.get('created_at', '')
        if created_at:
            try:
                # 处理不同的时间格式
                if 'T' in created_at:
                    report_date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).date()
                else:
                    report_date = datetime.strptime(created_at[:10], '%Y-%m-%d').date()
                if report_date == today:
                    today_audits += 1
            except (ValueError, TypeError):
                pass
    
    # 最近上传的 skills
    recent_skills = sorted(skills, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
    
    # 最近的报告
    recent_reports = sorted(reports, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
    
    return {
        "total_skills": total_skills,
        "high_risk_count": high_risk_count,
        "today_audits": today_audits,
        "total_reports": total_reports,
        "recent_skills": recent_skills,
        "recent_reports": recent_reports
    }


@router.post("/run")
def run_audit(payload: dict = Body(...), service: AuditService = Depends(get_audit_service), skill_service: SkillService = Depends(get_skill_service), report_service: ReportService = Depends(get_report_service)) -> dict:
    """根据 skill_id 或 skill_path 发起一次同步审计（演示用）。

    请求体示例：{ "skill_id": "..." } 或 { "skill_path": "..." }
    返回：{ "audit_id": "...", "report_id": "...", "completed": true }
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

    previous_skill_path = None
    baseline_skill_id = payload.get('baseline_skill_id') if isinstance(payload, dict) else None
    if baseline_skill_id:
        if skill_id and baseline_skill_id == skill_id:
            raise HTTPException(status_code=400, detail='baseline_skill_id must differ from skill_id')
        prev_rec = skill_service.get_skill(baseline_skill_id)
        if not prev_rec:
            raise HTTPException(status_code=404, detail='baseline skill not found')
        previous_skill_path = prev_rec.get('path')
        if not previous_skill_path:
            raise HTTPException(status_code=400, detail='baseline skill has no storage path')

    # 直接运行审计（同步），返回生成的 report id
    options = payload.get('options', {}) if isinstance(payload, dict) else {}
    ctx = service.run_audit(skill_path, options=options, previous_skill_path=previous_skill_path)
    report = ctx.get('report') or {}
    report_id = report.get('report_id')
    if not report_id:
        # 尝试根据 skill_name 找到最新的报告
        skill_name = report.get('metadata', {}).get('skill_name')
        if skill_name:
            reps = report_service.list_reports_by_skill_name(skill_name)
            if reps:
                report_id = reps[0]['id']

    return {
        "audit_id": report_id,
        "report_id": report_id,
        "completed": True,
        "progress": 100,
        "report": report
    }


@router.get("/")
@router.get("")  # 同时支持无尾部斜杠的路径（兼容前端 /audits 请求）
def list_audits(report_service: ReportService = Depends(get_report_service)) -> dict:
    items = report_service.list_all_reports()
    return {"items": items, "total": len(items)}


@router.get("/{audit_id}")
def get_audit(audit_id: str, report_service: ReportService = Depends(get_report_service)) -> dict:
    """获取审计状态和报告信息"""
    # 先尝试作为报告 ID 查询
    try:
        r = report_service.get_report(audit_id)
        # 返回报告数据，标记为已完成
        return {
            "audit_id": audit_id,
            "report_id": audit_id,
            "completed": True,
            "progress": 100,
            "logs": ["审计已完成"],
            **r
        }
    except FileNotFoundError:
        pass
    
    # 如果不是报告 ID，返回未找到状态
    return {"audit_id": audit_id, "status": "not_found"}
