"""Database Service Provider

Classes:
- DatabaseServiceProvider: Registers database services.
"""
from limberframework.authentication.authenticators import make_authenticator
from limberframework.foundation.application import Application
from limberframework.support.services import ServiceProvider


class AuthServiceProvider(ServiceProvider):
    """Registers database services to the service container."""

    def register(self, app: Application) -> None:
        """Registers the auth service with the application.

        Arguments:
        app limberframework.foundation.application.Application --
        the service container.
        """

        async def register_authenticator(app: Application):
            config_service = await app.make("config")
            return await make_authenticator(config_service["auth"])

        app.bind("auth", register_authenticator, defer=True)
