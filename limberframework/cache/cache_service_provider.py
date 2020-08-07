"""Cache Service Provider

Classes:
- CacheServiceProvider: Registers cache services.
"""
from limberframework.cache.cache import Cache
from limberframework.cache.stores import make_store, Store
from limberframework.support.service_providers import ServiceProvider

class CacheServiceProvider(ServiceProvider):
    """Registers cache services to the service container."""
    def register(self):
        """Registers the cache store to the service container."""
        def register_store(app: 'Application') -> Store:
            """Closure for establishing a cache store.

            Arguments:
            app Application -- foundation.application.Application object.

            Returns Store object.
            """
            return make_store(app['config']['cache'], base_path=app.base_path)

        self.app.bind('cache.store', register_store, True)

        def register_cache(app: 'Application') -> Cache:
            """Closure for establishing a
            cache and linking to a store.

            Arguments:
            app Application -- foundation.application.Application object.

            Returns Cache.
            """
            return Cache(app['cache.store'])

        self.app.bind('cache', register_cache)
