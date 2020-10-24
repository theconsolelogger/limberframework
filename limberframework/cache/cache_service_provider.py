"""Cache Service Provider

Classes:
- CacheServiceProvider: Registers cache services.
"""
from limberframework.cache.cache import Cache
from limberframework.cache.lockers import Locker, make_locker
from limberframework.cache.stores import Store, make_store
from limberframework.foundation.application import Application
from limberframework.support.services import Service, ServiceProvider


class CacheServiceProvider(ServiceProvider):
    """Registers cache services to the service container."""

    def register(self, app: Application):
        """Registers the cache store to the service container.

        Arguments:
        app limberframework.foundation.application.Application --
        the service container.
        """

        async def register_store(app: Application) -> Store:
            """Closure for establishing a cache store.

            Arguments:
            app Application -- foundation.application.Application object.

            Returns Store object.
            """
            config_service = await app.make("config")
            return await make_store(config_service["cache"])

        app.bind(Service("cache.store", register_store, singleton=True))

        async def register_locker(app: Application) -> Locker:
            """Closure for establishing a locker.

            Arguments:
            app Application -- foundation.application.Application object.

            Returns Locker.
            """
            config_service = await app.make("config")

            try:
                return await make_locker(config_service["cache"])
            except ValueError:
                return None

        app.bind(Service("cache.locker", register_locker, singleton=True))

        async def register_cache(app: Application) -> Cache:
            """Closure for establishing a
            cache and linking to a store.

            Arguments:
            app Application -- foundation.application.Application object.

            Returns Cache.
            """
            store = await app.make("cache.store")
            locker = await app.make("cache.locker")
            return Cache(store, locker)

        app.bind(Service("cache", register_cache, defer=True))
