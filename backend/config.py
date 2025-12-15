"""Configuration management for AWS Track Agent."""
from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    # AWS Configuration
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    aws_access_key_id: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_session_token: Optional[str] = os.getenv("AWS_SESSION_TOKEN")
    
    # CloudTrail Configuration
    cloudtrail_s3_bucket: str = os.getenv("CLOUDTRAIL_S3_BUCKET", "")
    cloudtrail_log_prefix: str = os.getenv("CLOUDTRAIL_LOG_PREFIX", "CloudTrail/")
    
    # Cost Anomaly Detection
    cost_anomaly_detection_enabled: bool = os.getenv("COST_ANOMALY_DETECTION_ENABLED", "true").lower() == "true"
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/aws_track_agent")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # API Configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_debug: bool = os.getenv("API_DEBUG", "false").lower() == "true"
    
    # Frontend URL
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Alerting Configuration
    sns_topic_arn: Optional[str] = os.getenv("SNS_TOPIC_ARN")
    slack_webhook_url: Optional[str] = os.getenv("SLACK_WEBHOOK_URL")
    email_from: str = os.getenv("EMAIL_FROM", "noreply@example.com")
    email_to: str = os.getenv("EMAIL_TO", "admin@example.com")
    
    # Monitoring Configuration
    monitoring_interval_seconds: int = int(os.getenv("MONITORING_INTERVAL_SECONDS", "300"))
    cloudtrail_check_interval_seconds: int = int(os.getenv("CLOUDTRAIL_CHECK_INTERVAL_SECONDS", "60"))
    cost_check_interval_seconds: int = int(os.getenv("COST_CHECK_INTERVAL_SECONDS", "3600"))
    
    # Test Mode
    test_mode: bool = os.getenv("TEST_MODE", "false").lower() == "true"
    use_sample_data: bool = os.getenv("USE_SAMPLE_DATA", "false").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
