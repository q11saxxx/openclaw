"""本文件说明：项目模块的请求与响应模型。"""

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    """本模型说明：创建项目时前端提交的数据结构。"""

    name: str
    project_type: str = "openclaw-skill"
    description: str = ""
