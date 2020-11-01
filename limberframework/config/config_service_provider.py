"""Config Service Provider

Classes:
- ConfigServiceProvider: Registers configuration services.
"""
from os import listdir
from os.path import isfile

from limberframework.config.config import Config
from limberframework.foundation.application import Application
from limberframework.support.services import Service, ServiceProvider


class ConfigServiceProvider(ServiceProvider):
    """Registers configuration services to the service container."""

    def register(self, app: Application) -> None:
        """Registers the Config class to the service container,
        which holds configuration settings for the application.

        Arguments:
        app limberframework.foundation.application.Application --
        the service container.
        """

        async def register_config(app: Application) -> Config:
            """Closure for creating a new config service instance.

            Arguments:
            app Application -- Application object.

            Returns:
            Config -- Config object.
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
