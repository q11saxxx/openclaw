"""依赖注入占位。

规则描述：
- 统一放置数据库会话、鉴权用户、请求上下文等依赖。
- 路由层不要重复实例化 service 和 repository。
"""
from app.services.audit_service import AuditService
from app.services.report_service import ReportService
from app.services.skill_service import SkillService

def get_skill_service() -> SkillService:
    return SkillService()

def get_audit_service() -> AuditService:
    return AuditService()

def get_report_service() -> ReportService:
    return ReportService()
