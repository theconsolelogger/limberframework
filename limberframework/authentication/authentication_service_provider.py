"""Database Service Provider

Classes:
- DatabaseServiceProvider: Registers database services.
"""
from limberframework.authentication.authenticators import make_authenticator
from limberframework.foundation.application import Application
from limberframework.support.services import ServiceProvider


class AuthServiceProvider(ServiceProvider):
    """Registers database services to the service container."""

    def register(self) -> None:
        async def register_authenticator(app: Application):
            config_service = await app.make("config")
            return await make_authenticator(config_service["auth"])

        self.app.bind("auth", register_authenticator, defer=True)
