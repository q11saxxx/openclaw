"""本文件说明：读取环境变量并提供统一配置入口。"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """本类说明：集中管理 API、数据库、Trivy、漏洞源等配置。"""

    app_name: str = "OpenClaw Skill Audit Platform"
    app_env: str = "development"
    app_debug: bool = True
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./data/db/dev.sqlite3"
    trivy_binary: str = "trivy"
    trivy_cache_dir: str = "./data/trivy"

    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")


settings = Settings()
