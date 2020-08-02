"""Database Service Provider

Classes:
- DatabaseServiceProvider: Registers database services.
"""
from limberframework.authentication.authenticators import make_authenticator
from limberframework.support.service_providers import ServiceProvider

class AuthServiceProvider(ServiceProvider):
    """Registers database services to the service container."""
    def register(self) -> None:
        def register_authenticator(app: 'Application'):
            return make_authenticator(app['config']['auth'])

        self.app.bind('auth', register_authenticator)
