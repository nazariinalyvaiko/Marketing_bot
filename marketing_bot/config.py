from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	# OpenAI
	OPENAI_API_KEY: str | None = None
	OPENAI_MODEL: str = "gpt-4o-mini"
	OPENAI_BASE_URL: str | None = None

	# Modes
	OFFLINE_MODE: bool = False
	SENDER_DRY_RUN: bool = True

	# Email defaults
	EMAIL_SENDER_NAME: str = "Marketing Bot"
	EMAIL_SENDER_ADDR: str = "marketing@example.com"

	# SMTP
	SMTP_HOST: str | None = None
	SMTP_PORT: int = 587
	SMTP_USERNAME: str | None = None
	SMTP_PASSWORD: str | None = None
	SMTP_USE_TLS: bool = True

	# SendGrid
	SENDGRID_API_KEY: str | None = None
	SENDGRID_FROM_EMAIL: str | None = None

	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


settings = Settings()
