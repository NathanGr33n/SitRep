"""
Configuration module for SitRep backend.
Loads settings from environment variables using Pydantic.
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = Field(default="postgresql://sitrep_user:sitrep_password@localhost:5432/sitrep_db")
    
    # API
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_reload: bool = Field(default=True)
    
    # Mapbox
    mapbox_access_token: str = Field(default="")
    
    # NLP Models
    ner_model: str = Field(default="dslim/bert-base-NER")
    summarization_model: str = Field(default="facebook/bart-large-cnn")
    classification_model: str = Field(default="facebook/bart-large-mnli")
    
    # Geocoding
    geocoding_user_agent: str = Field(default="sitrep_dashboard")
    geocoding_rate_limit: int = Field(default=1)
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")
    
    # Ingestion
    ingestion_interval_hours: int = Field(default=6)
    max_articles_per_source: int = Field(default=100)
    
    # Confidence
    min_confidence_score: float = Field(default=0.3)
    high_confidence_threshold: float = Field(default=0.7)
    
    # Clustering
    cluster_distance_km: float = Field(default=50.0)
    cluster_time_window_hours: int = Field(default=48)
    
    # Logging
    log_level: str = Field(default="INFO")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
