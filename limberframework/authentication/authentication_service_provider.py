"""Provides authentication services."""
from limberframework.authentication.authenticators import make_authenticator
from limberframework.foundation.application import Application
from limberframework.support.services import Service, ServiceProvider


class AuthServiceProvider(ServiceProvider):
    """Register authentication services to the service container."""

    def register(self, app: Application) -> None:
        """Register the auth service with the application.

        Args:
            app: The Application.
        """

        async def register_authenticator(app: Application):
            """Closure to create the auth service.

            Args:
                app: The Application.
            """
            config_service = await app.make("config")
            config = config_service.get_section("auth")
            return await make_authenticator(config)

        app.bind(Service("auth", register_authenticator, defer=True))
