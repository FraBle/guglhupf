"""Settings management using pydantic."""

from pathlib import Path
from typing import Union

from pydantic import BaseSettings
from single_source import get_version


class Settings(BaseSettings):
    """All settings for guglhupf.

    Values can be overridden with environment variables or a .env file.
    See: https://pydantic-docs.helpmanual.io/usage/settings/
    """

    app_name: str = 'guglhupf'
    app_version: str = get_version(
        __name__, Path(__file__).parent.parent.parent,
    )
    debug: bool = False
    log_level: str = 'info'
    log_format: str = (
        '<level>{level: <8}</level> ' +
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> ' +
        '<cyan>{name}</cyan>:<cyan>{function}</cyan> - ' +
        '<level>{message}</level>' +
        '{exception}\n'
    )

    class Config(object):  # noqa: WPS431
        """Enable support to load settings from .env files."""

        env_file = '.env'


settings = Settings()
