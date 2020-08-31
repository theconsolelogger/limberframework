from os import getcwd
from unittest.mock import MagicMock, patch

from pytest import fixture, mark
from sqlalchemy.orm import Session

from limberframework.authentication.authentication_service_provider import (
    AuthServiceProvider,
)
from limberframework.authentication.authenticators import ApiKey, HttpBasic
from limberframework.cache.cache import Cache
from limberframework.cache.cache_service_provider import CacheServiceProvider
from limberframework.cache.stores import FileStore
from limberframework.config.config_service_provider import (
    ConfigServiceProvider,
)
from limberframework.database.connections import (
    PostgresConnection,
    SqliteConnection,
)
from limberframework.database.database_service_provider import (
    DatabaseServiceProvider,
)
from limberframework.foundation.application import Application


@fixture
def app():
    app = Application()
    app.register(ConfigServiceProvider(app))

    return app


@mark.parametrize(
    "driver,connection",
    [("sqlite", SqliteConnection), ("pgsql", PostgresConnection)],
)
@patch("limberframework.database.connections.create_engine")
@mark.asyncio
async def test_database_service_provider_database_connection(
    mock_create_engine, driver, connection, app
):
    config_service = await app.make("config")
    config_service["database"] = {
        "driver": driver,
        "path": "./test.db",
        "username": "test",
        "password": "test",
        "host": "test",
        "port": "test",
        "database": "test",
    }
    app.register(DatabaseServiceProvider(app))

    database = await app.make("db.connection")

    assert isinstance(database, connection)


@mark.asyncio
async def test_database_service_provider_database_session(app):
    config_service = await app.make("config")
    config_service["database"] = {
        "driver": "sqlite",
        "path": "./test.db",
    }
    app.register(DatabaseServiceProvider(app))

    session = await app.make("db.session")

    assert isinstance(session, Session)


def test_config_service_provider():
    mock_app = MagicMock()
    config = ConfigServiceProvider(mock_app)
    config.register()

    assert mock_app.bind.called_once()


@mark.parametrize(
    "driver,authenticator", [("httpbasic", HttpBasic), ("apikey", ApiKey)]
)
@mark.asyncio
async def test_authentication_service_provider(driver, authenticator, app):
    config_service = await app.make("config")
    config_service["auth"] = {"driver": driver}
    app.register(AuthServiceProvider(app))

    auth = await app.make("auth")

    assert isinstance(auth, authenticator)


@mark.parametrize(
    "path,expected_path",
    [("/", "/"), ("/tests", "/tests"), ("./tests", f"{getcwd()}/./tests")],
)
@mark.asyncio
async def test_cache_service_provider_cache_store(path, expected_path, app):
    config_service = await app.make("config")
    config_service["cache"] = {"driver": "file", "path": path}
    app.register(CacheServiceProvider(app))

    store = await app.make("cache.store")

    assert isinstance(store, FileStore)
    assert store.directory == expected_path


@mark.asyncio
async def test_cache_service_provider_cache(app):
    path = "/tests"
    config_service = await app.make("config")
    config_service["cache"] = {"driver": "file", "path": path}
    app.register(CacheServiceProvider(app))

    store = await app.make("cache")

    assert isinstance(store, Cache)
