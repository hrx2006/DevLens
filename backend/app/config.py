import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "DevLens AI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./devlens.db")
    
    # JWT and Authentication Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "devlens_super_secret_production_key_change_in_env_38192739182")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24)))  # 24 hours
    COOKIE_NAME: str = "devlens_token"
    COOKIE_SECURE: bool = os.getenv("COOKIE_SECURE", "false").lower() in ("true", "1", "t")
    COOKIE_SAMESITE: str = "lax"
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

    # AI Configuration
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "gemini")
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "gemini-2.5-flash")

    # Crawler & Scanner Limits
    MAX_CRAWL_PAGES: int = int(os.getenv("MAX_CRAWL_PAGES", "10"))
    CRAWL_TIMEOUT: int = int(os.getenv("CRAWL_TIMEOUT", "20"))
    MAX_RESPONSE_BYTES: int = int(os.getenv("MAX_RESPONSE_BYTES", str(5 * 1024 * 1024)))  # 5MB
    SSRF_ALLOW_DEMO: bool = os.getenv("SSRF_ALLOW_DEMO", "true").lower() in ("true", "1", "t")

    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

settings = Settings()
