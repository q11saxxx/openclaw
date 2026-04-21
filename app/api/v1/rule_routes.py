"""规则管理 API 路由。"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Body

from app.services.rule_service import RuleService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Rules"])


def get_rule_service() -> RuleService:
    """依赖注入：获取规则服务实例。"""
    return RuleService()


@router.get("", response_model=dict)
async def list_rules(
    rule_type: Optional[str] = None,
    service: RuleService = Depends(get_rule_service)
) -> dict:
    """
    列出所有规则。
    
    Query Parameters:
    - rule_type: 规则类型过滤（'builtin' 或 'custom'，默认全部）
    
    Returns:
    {
        "rules": [
            {
                "id": "rule-id",
                "title": "规则标题",
                "pattern": "匹配模式",
                "level": "high",
                "_source": "builtin/xxx.yaml"
            }
        ],
        "total": 10
    }
    """
    try:
        rules = service.list_rules(rule_type)
        return {
            "rules": rules,
            "total": len(rules)
        }
    except Exception as e:
        logger.error(f"Failed to list rules: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{rule_id}", response_model=dict)
async def get_rule(
    rule_id: str,
    service: RuleService = Depends(get_rule_service)
) -> dict:
    """
    获取指定规则。
    
    Path Parameters:
    - rule_id: 规则 ID
    
    Returns:
    {
        "id": "rule-id",
        "title": "规则标题",
        "pattern": "匹配模式",
        "level": "high",
        "_source": "builtin/xxx.yaml"
    }
    """
    try:
        rule = service.get_rule(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail=f"Rule not found: {rule_id}")
        return rule
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get rule: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=dict, status_code=201)
async def create_rule(
    rule_data: dict = Body(...),
    service: RuleService = Depends(get_rule_service)
) -> dict:
    """
    创建新规则。
    
    Request Body:
    {
        "id": "custom-rule-1",
        "title": "自定义规则标题",
        "pattern": "匹配模式",
        "level": "high",
        "description": "可选的规则描述"
    }
    
    Returns:
    {
        "id": "custom-rule-1",
        "title": "自定义规则标题",
        "pattern": "匹配模式",
        "level": "high",
        "_source": "custom/custom-rule-1.yaml"
    }
    """
    try:
        rule = service.create_rule(rule_data)
        return rule
    except ValueError as e:
        logger.warning(f"Invalid rule data: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create rule: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{rule_id}", response_model=dict)
async def update_rule(
    rule_id: str,
    rule_data: dict = Body(...),
    service: RuleService = Depends(get_rule_service)
) -> dict:
    """
    更新规则。
    
    Path Parameters:
    - rule_id: 规则 ID
    
    Request Body:
    {
        "title": "新的规则标题",
        "pattern": "新的匹配模式",
        "level": "medium",
        "description": "新的描述"
    }
    
    Returns:
    {
        "id": "rule-id",
        "title": "新的规则标题",
        "pattern": "新的匹配模式",
        "level": "medium",
        "_source": "custom/rule-id.yaml"
    }
    """
    try:
        rule = service.update_rule(rule_id, rule_data)
        return rule
    except ValueError as e:
        logger.warning(f"Invalid update data: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update rule: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{rule_id}", response_model=dict)
async def delete_rule(
    rule_id: str,
    service: RuleService = Depends(get_rule_service)
) -> dict:
    """
    删除规则。
    
    Path Parameters:
    - rule_id: 规则 ID
    
    Returns:
    {
        "message": "规则已删除",
        "rule_id": "rule-id"
    }
    """
    try:
        service.delete_rule(rule_id)
        return {
            "message": "规则已删除",
            "rule_id": rule_id
        }
    except ValueError as e:
        logger.warning(f"Cannot delete rule: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete rule: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
