""" Config

Classes:
- BaseConfig: base class for configurations.
- Config: holds configuration settings.
"""
from typing import Dict
from pydantic import BaseSettings

class BaseConfig(BaseSettings):
    """Base class for configurations which
    sets reading from a dotenv file.
    """
    class Config:
        env_file: str = ".env"

class Config:
    """Handles configuration settings for an application.

    Attributes:
    config dict -- the configuration settings.
    """
    def __init__(self) -> None:
        """Establishes the initial configuration settings."""
        self.config = {}

    def __getitem__(self, name: str) -> Dict:
        """Access a set of configuration
        settings associated with a name.

        Arguments:
        name str -- name of configuration set.

        Returns:
        dict -- configuration settings.
        """
        return self.config[name]

    def __setitem__(self, name: str, config: Dict) -> None:
        """Associate configuration settings with a name.

        Arguments:
        name str -- name of configuration settings.
        config dict -- configuration settings.
        """
        self.config[name] = config
