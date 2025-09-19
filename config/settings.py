"""Configuration settings for the Premier League Agent."""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class AzureConfig:
    endpoint: str
    model_name: str
    deployment: str
    subscription_key: str
    api_version: str


@dataclass
class FootballAPIConfig:
    base_url: str
    api_key: str
    competition_code: str = "PL"


@dataclass
class AppConfig:
    azure: AzureConfig
    football_api: FootballAPIConfig
    cache_ttl_hours: int = 24
    max_completion_tokens: int = 2048


def load_config() -> AppConfig:
    """Load configuration from environment variables."""
    azure_config = AzureConfig(
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
        model_name=os.getenv("AZURE_MODEL_NAME", "gpt-5-mini"),
        deployment=os.getenv("AZURE_DEPLOYMENT", "gpt-5-mini"),
        subscription_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
        api_version=os.getenv("OPENAI_API_VERSION", "2024-12-01-preview")
    )

    football_config = FootballAPIConfig(
        base_url=os.getenv("FOOTBALL_API_BASE",
                           "http://api.football-data.org/v4/"),
        api_key=os.getenv("FOOTBALL_API_KEY", "")
    )

    return AppConfig(
        azure=azure_config,
        football_api=football_config,
        cache_ttl_hours=int(os.getenv("CACHE_TTL_HOURS", "24")),
        max_completion_tokens=int(os.getenv("MAX_COMPLETION_TOKENS", "2048"))
    )
