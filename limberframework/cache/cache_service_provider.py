"""Providers services related to the cache."""
from typing import Optional

from limberframework.cache.cache import Cache
from limberframework.cache.lockers import Locker, make_locker
from limberframework.cache.stores import Store, make_store
from limberframework.foundation.application import Application
from limberframework.support.services import Service, ServiceProvider


class CacheServiceProvider(ServiceProvider):
    """Register cache services to the service container."""

    def register(self, app: Application):
        """Register the cache store to the service container.

        Args:
            app: The service container.
        """

        async def register_store(app: Application) -> Store:
            """Closure for establishing a cache store.

            Args:
                app: The Application.

            Returns:
                Store: The created Store.
            """
            config_service = await app.make("config")
            config = config_service.get_section("cache")

            if config["driver"] == "file":
                config["path"] = app.paths["cache"]
            elif (
                config["driver"] == "redis" or config["driver"] == "asyncredis"
            ) and "password" not in config:
                config["password"] = None

            return await make_store(config)

        app.bind(Service("cache.store", register_store, singleton=True))

        async def register_locker(app: Application) -> Optional[Locker]:
            """Closure for establishing a locker.

            Args:
                app: The Application.

            Returns
                Locker: The created Locker.
            """
            config_service = await app.make("config")
            config = config_service.get_section("cache")

            if config["locker"] == "asyncredis" and "password" not in config:
                config["password"] = None

            try:
                return await make_locker(config)
            except ValueError:
                return None

        app.bind(Service("cache.locker", register_locker, singleton=True))

        async def register_cache(app: Application) -> Cache:
            """Closure for establishing a cache and linking to a store.

            Args:
                app: The Application.

            Returns:
                Cache: The created Cache.
            """
            store = await app.make("cache.store")
            locker = await app.make("cache.locker")
            return Cache(store, locker)

        app.bind(Service("cache", register_cache, defer=True))
