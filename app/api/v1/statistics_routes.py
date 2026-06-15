"""审计统计分析接口。

提供审计历史趋势、Skill对比和智能洞察等统计功能。
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.services.audit_statistics_service import AuditStatisticsService

router = APIRouter()


def get_statistics_service() -> AuditStatisticsService:
    """获取统计服务实例"""
    return AuditStatisticsService()


@router.get("/trends")
def get_audit_trends(
    days: int = Query(default=30, ge=1, le=365, description="统计天数"),
    service: AuditStatisticsService = Depends(get_statistics_service)
):
    """获取审计趋势数据
    
    Args:
        days: 统计天数（1-365天）
        
    Returns:
        包含趋势数据的字典
    """
    try:
        trends = service.get_audit_trends(days=days)
        return {
            "success": True,
            "data": trends
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取趋势数据失败: {str(e)}")


@router.get("/skill-comparison/{skill_name}")
def get_skill_comparison(
    skill_name: str,
    service: AuditStatisticsService = Depends(get_statistics_service)
):
    """获取指定Skill的历史审计对比数据
    
    Args:
        skill_name: Skill名称
        
    Returns:
        包含对比数据的字典
    """
    try:
        comparison = service.get_skill_comparison(skill_name)
        return {
            "success": True,
            "data": comparison
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对比数据失败: {str(e)}")


@router.get("/insights")
def get_insights(
    service: AuditStatisticsService = Depends(get_statistics_service)
):
    """获取智能洞察
    
    Returns:
        包含洞察信息的字典
    """
    try:
        insights = service.get_insights()
        return {
            "success": True,
            "data": insights
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成洞察失败: {str(e)}")
