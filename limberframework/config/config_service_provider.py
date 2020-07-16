"""Config Service Provider

Classes:
- ConfigServiceProvider: Registers configuration services.
"""
from limberframework.config.config import Config
from limberframework.support.service_providers import ServiceProvider

class ConfigServiceProvider(ServiceProvider):
    """Registers configuration services to the service container."""
    def register(self) -> None:
        """Registers the Config class to the service container,
        which holds configuration settings for the application.
        """
        def register_config(app: 'Application') -> Config:
            """Closure for creating a new config service instance.

            Arguments:
            app Application -- Application object.

            Returns:
            Config -- Config object.
            """
            return Config()

        self.app.bind('config', register_config, True)
