"""Provides services for configuration."""
from os import listdir
from os.path import isfile

from limberframework.config.config import Config
from limberframework.foundation.application import Application
from limberframework.support.services import Service, ServiceProvider


class ConfigServiceProvider(ServiceProvider):
    """Registers configuration services to the service container."""

    def register(self, app: Application) -> None:
        """Register the Config class to the service container.

        This service holds configuration settings for the application.

        Args:
            app: The Application.
        """

        async def register_config(app: Application) -> Config:
            """Closure for creating a new config service instance.

            Args:
                app: The Application.

            Returns:
                Config: Created Config instance.
            """
            config = Config()
            config.optionxform = str

            for config_file in listdir(app.paths["config"]):
                config_file_path = f"{app.paths['config']}/{config_file}"

                if isfile(config_file_path) and config_file.lower().endswith(
                    ".ini"
                ):
                    config.read(config_file_path, encoding="utf-8")

            return config

        app.bind(Service("config", register_config, singleton=True))
