"""规则管理 API 路由。"""
import logging
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel, Field

from app.services.rule_service import RuleService

logger = logging.getLogger(__name__)

# 定义路由，不在这里写 prefix，统一在 main.py 中定义
router = APIRouter(tags=["Rules"])

# --- 1. 数据校验模型 (解决 422 报错的核心) ---

class RuleCreate(BaseModel):
    """创建规则的请求模型"""
    id: str = Field(..., description="规则唯一标识符，如: detect_eval", example="detect_eval")
    title: str = Field(..., description="规则名称", example="禁用 eval 函数")
    pattern: str = Field(..., description="正则表达式模式", example="eval\\s*\\(")
    level: str = Field(..., description="风险等级: low, medium, high, critical", example="high")
    description: Optional[str] = Field(None, description="规则详细描述", example="防止执行任意代码指令")

class RuleUpdate(BaseModel):
    """更新规则的请求模型（ID不可修改）"""
    title: Optional[str] = None
    pattern: Optional[str] = None
    level: Optional[str] = None
    description: Optional[str] = None

# --- 2. 依赖注入 ---

def get_rule_service() -> RuleService:
    """获取规则服务实例。"""
    return RuleService()

# --- 3. API 接口实现 ---

@router.get("/", response_model=Dict[str, Any])
@router.get("", include_in_schema=False) # 兼容不带斜杠的请求
async def list_rules(
    rule_type: Optional[str] = None,
    service: RuleService = Depends(get_rule_service)
):
    """列出所有规则（可按 builtin 或 custom 过滤）"""
    try:
        rules = service.list_rules(rule_type)
        return {
            "rules": rules,
            "total": len(rules)
        }
    except Exception as e:
        logger.error(f"Failed to list rules: {str(e)}")
        raise HTTPException(status_code=500, detail="获取规则列表失败")

@router.get("/{rule_id}", response_model=Dict[str, Any])
async def get_rule(
    rule_id: str,
    service: RuleService = Depends(get_rule_service)
):
    """获取指定规则详情"""
    rule = service.get_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail=f"未找到 ID 为 {rule_id} 的规则")
    return rule

@router.post("/", response_model=Dict[str, Any], status_code=201)
@router.post("", include_in_schema=False)
async def create_rule(
    rule_data: RuleCreate, # 👈 使用模型校验，FastAPI 会自动解析 JSON
    service: RuleService = Depends(get_rule_service)
):
    """创建新的自定义规则"""
    try:
        # 将模型转为字典传给 service
        rule = service.create_rule(rule_data.dict())
        return rule
    except ValueError as e:
        # 如果 ID 已存在或数据不合法，service 会抛出 ValueError
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create rule: {str(e)}")
        raise HTTPException(status_code=500, detail="创建规则失败")

@router.put("/{rule_id}", response_model=Dict[str, Any])
async def update_rule(
    rule_id: str,
    rule_data: RuleUpdate,
    service: RuleService = Depends(get_rule_service)
):
    """更新自定义规则内容"""
    try:
        # 过滤掉请求中为 None 的字段，只更新传了值的字段
        update_dict = {k: v for k, v in rule_data.dict().items() if v is not None}
        rule = service.update_rule(rule_id, update_dict)
        return rule
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update rule {rule_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="更新规则失败")

@router.delete("/{rule_id}", response_model=Dict[str, Any])
async def delete_rule(
    rule_id: str,
    service: RuleService = Depends(get_rule_service)
):
    """删除指定的自定义规则"""
    try:
        service.delete_rule(rule_id)
        return {
            "message": f"规则 {rule_id} 已成功删除",
            "rule_id": rule_id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete rule {rule_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="删除规则失败")
