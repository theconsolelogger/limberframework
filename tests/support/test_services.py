from os import getcwd
from unittest.mock import MagicMock, Mock, patch

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
from limberframework.support.services import Service


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
    config_service["cache"] = {"driver": "file", "path": path, "locker": None}
    app.register(CacheServiceProvider(app))

    store = await app.make("cache")

    assert isinstance(store, Cache)


@patch("limberframework.cache.cache_service_provider.make_locker")
@mark.asyncio
async def test_cache_service_provider_cache_locker(mock_make_locker, app):
    config = {
        "driver": "asyncredis",
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "password": None,
        "locker": "asyncredis",
    }
    config_service = await app.make("config")
    config_service["cache"] = config

    app.register(CacheServiceProvider(app))

    await app.make("cache.locker")

    mock_make_locker.assert_called_once_with(config)


def test_create_service():
    """Tests creating a Service NamedTuple."""
    name = "Test Service"
    closure = Mock()
    singleton = True
    defer = True

    service = Service(name, closure, singleton, defer)

    assert service.name == name
    assert service.closure == closure
    assert service.singleton == singleton
    assert service.defer == defer


def test_service_representation():
    """Tests retrieving a string representation of a Service."""
    name = "Test Service"
    closure = Mock()
    singleton = True
    defer = True

    service = Service(name, closure, singleton, defer)
    str_representation = str(service)

    assert str_representation == (
        f"<Service name={name}, closure={closure}, "
        f"singleton={singleton}, defer={defer}>"
    )
