"""本文件说明：项目与插件管理接口，后续承接项目创建、列表、详情与历史对比。"""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_projects() -> dict:
    """本接口说明：返回项目列表，前端项目页先用假数据联调。"""
    return {"items": [], "message": "TODO: list projects"}


@router.post("")
def create_project() -> dict:
    """本接口说明：创建项目，后续接入数据库和请求体模型。"""
    return {"message": "TODO: create project"}
