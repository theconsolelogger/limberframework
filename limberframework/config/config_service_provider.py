"""Config Service Provider

Classes:
- ConfigServiceProvider: Registers configuration services.
"""
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
            return Config()

        app.bind(Service("config", register_config, singleton=True))
