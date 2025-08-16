from pydantic import Field, validator
from pydantic_settings import BaseSettings


class ProjectSettings(BaseSettings):
    """Production-ready configuration with validation"""

    # App
    app_name: str = 'Personal AI Assistant'
    debug: bool = False
    version: str = '0.1.0'
    log_level: str = 'INFO'

    # Security
    secret_key: str = Field(..., min_length=32)
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30

    # Rate limiting
    rate_limit_per_minute: int = 60

    @validator('secret_key')
    def validate_secret_key(cls, v):  # noqa: N805
        if len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters long')
        return v

    @validator('log_level')
    def validate_log_level(cls, v):  # noqa: N805
        valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if v.upper() not in valid_levels:
            raise ValueError(f'LOG_LEVEL must be one of {valid_levels}')
        return v.upper()


class DatabaseSettings(BaseSettings):
    database_url: str = Field(..., description='PostgreSQL URL')
    database_pool_size: int = 20
    database_max_overflow: int = 0


class RedisSettings(BaseSettings):
    redis_url: str = Field(default='redis://localhost:6379/0')
    redis_max_connections: int = 20


class TelemetrySettings(BaseSettings):
    telemetry_enabled: bool = True
    telemetry_endpoint: str = None


PROJECT_SETTINGS = ProjectSettings()
DATABASE_SETTINGS = DatabaseSettings()
REDIS_SETTINGS = RedisSettings()
TELEMETRY_SETTINGS = TelemetrySettings()
