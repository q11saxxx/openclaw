"""数据库模型。

规则描述：
- 定义所有数据库表结构。
"""
from app.db.models.skill_record import SkillRecord
from app.db.models.audit_record import AuditRecord
from app.db.models.report_record import ReportRecord
from app.db.models.risk_item import RiskItem

__all__ = ["SkillRecord", "AuditRecord", "ReportRecord", "RiskItem"]