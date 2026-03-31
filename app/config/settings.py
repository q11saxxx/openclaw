"""全局配置。

规则描述：
- 所有环境变量统一在此收口。
- 禁止在业务代码中硬编码路径、模型名、数据库地址。
- 新增配置必须同步更新 `.env.example`。
"""
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "OpenClaw Skill Risk Platform"
    app_env: str = "dev"
    debug: bool = True
    database_url: str = "sqlite:///./risk_platform.db"
    report_dir: str = "./data/reports"
    upload_dir: str = "./data/uploads"
    extract_dir: str = "./data/extracted"
    llm_provider: str = "mock"
    llm_model: str = "mock-model"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
