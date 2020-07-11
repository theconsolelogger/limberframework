""" Config

Classes:
- BaseConfig: base class for configurations.
"""
from pydantic import BaseSettings

class BaseConfig(BaseSettings):
    """Base class for configurations which
    sets reading from a dotenv file.
    """
    class Config:
        env_file: str = ".env"
