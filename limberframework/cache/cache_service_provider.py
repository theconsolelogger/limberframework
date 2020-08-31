"""Cache Service Provider

Classes:
- CacheServiceProvider: Registers cache services.
"""
from limberframework.cache.cache import Cache
from limberframework.cache.stores import Store, make_store
from limberframework.foundation.application import Application
from limberframework.support.service_providers import ServiceProvider


class CacheServiceProvider(ServiceProvider):
    """Registers cache services to the service container."""

    def register(self):
        """Registers the cache store to the service container."""

        async def register_store(app: Application) -> Store:
            """Closure for establishing a cache store.

            Arguments:
            app Application -- foundation.application.Application object.

            Returns Store object.
            """
            config_service = await app.make("config")
            config = config_service["cache"]

            # Check whether the cache path is a relative
            # path, and construct the absolute path.
            if config_service["cache"]["path"][0] != "/":
                config = config_service["cache"].copy()
                config["path"] = (
                    app.base_path + "/" + config_service["cache"]["path"]
                )

            return await make_store(config)

        self.app.bind("cache.store", register_store, True)

        async def register_cache(app: Application) -> Cache:
            """Closure for establishing a
            cache and linking to a store.

            Arguments:
            app Application -- foundation.application.Application object.

            Returns Cache.
            """
            store = await app.make("cache.store")
            return Cache(store)

        self.app.bind("cache", register_cache, defer=True)
