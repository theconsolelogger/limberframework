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
    ServerConnection,
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
    config_service_provider = ConfigServiceProvider()
    config_service_provider.register(app)

    return app


@mark.parametrize(
    "driver,connection",
    [
        ("sqlite", SqliteConnection),
        ("postgresql", ServerConnection),
        ("mysql+mysqldb", ServerConnection),
    ],
)
@patch("limberframework.config.config_service_provider.listdir")
@patch("limberframework.database.connections.create_engine")
@mark.asyncio
async def test_database_service_provider_database_connection(
    mock_create_engine, mock_list_dir, driver, connection, app
):
    mock_list_dir.return_value = []

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
    database_service_provider = DatabaseServiceProvider()
    database_service_provider.register(app)

    database = await app.make("db.connection")

    assert isinstance(database, connection)


@patch("limberframework.config.config_service_provider.listdir")
@mark.asyncio
async def test_database_service_provider_database_session(mock_list_dir, app):
    mock_list_dir.return_value = []

    config_service = await app.make("config")
    config_service["database"] = {
        "driver": "sqlite",
        "path": "./test.db",
    }
    database_service_provider = DatabaseServiceProvider()
    database_service_provider.register(app)

    session = await app.make("db.session")

    assert isinstance(session, Session)


def test_config_service_provider():
    mock_app = MagicMock()
    config_service_provider = ConfigServiceProvider()
    config_service_provider.register(mock_app)

    assert mock_app.bind.called_once()


@patch("limberframework.config.config_service_provider.Config")
@patch("limberframework.config.config_service_provider.isfile")
@patch("limberframework.config.config_service_provider.listdir")
@mark.asyncio
async def test_config_service_provider_config_service(
    mock_list_dir, mock_is_file, mock_config
):
    mock_list_dir.return_value = ["test.ini", "testing"]
    mock_is_file.return_value = True

    app = Application()
    app.paths = {"base": "test_path", "config": "test_path/config"}

    config_service_provider = ConfigServiceProvider()
    config_service_provider.register(app)

    config_service = await app.make("config")

    assert config_service == mock_config.return_value
    mock_config.return_value.read.assert_called_once_with(
        "test_path/config/test.ini", encoding="utf-8"
    )


@mark.parametrize(
    "driver,authenticator", [("httpbasic", HttpBasic), ("apikey", ApiKey)]
)
@patch("limberframework.config.config_service_provider.listdir")
@mark.asyncio
async def test_authentication_service_provider(
    mock_list_dir, driver, authenticator, app
):
    mock_list_dir.return_value = []

    config_service = await app.make("config")
    config_service["auth"] = {"driver": driver}
    auth_service_provider = AuthServiceProvider()
    auth_service_provider.register(app)

    auth = await app.make("auth")

    assert isinstance(auth, authenticator)


@patch("limberframework.config.config_service_provider.listdir")
@mark.asyncio
async def test_cache_service_provider_cache_store(mock_list_dir, app):
    mock_list_dir.return_value = []

    config_service = await app.make("config")
    config_service["cache"] = {"driver": "file"}
    cache_service_provider = CacheServiceProvider()
    cache_service_provider.register(app)

    store = await app.make("cache.store")

    assert isinstance(store, FileStore)


@patch("limberframework.config.config_service_provider.listdir")
@patch("limberframework.cache.cache_service_provider.make_store")
@mark.asyncio
async def test_cache_service_provider_redis_store_without_password(
    mock_make_store, mock_list_dir, app
):
    mock_list_dir.return_value = []

    config_service = await app.make("config")
    config_service["cache"] = {"driver": "redis"}
    cache_service_provider = CacheServiceProvider()
    cache_service_provider.register(app)

    await app.make("cache.store")

    mock_make_store.assert_called_once_with(
        {"driver": "redis", "password": None}
    )


@patch("limberframework.config.config_service_provider.listdir")
@mark.asyncio
async def test_cache_service_provider_cache(mock_list_dir, app):
    mock_list_dir.return_value = []

    path = "/tests"
    config_service = await app.make("config")
    config_service["cache"] = {
        "driver": "file",
        "path": path,
        "locker": "None",
    }
    cache_service_provider = CacheServiceProvider()
    cache_service_provider.register(app)

    store = await app.make("cache")

    assert isinstance(store, Cache)


@patch("limberframework.config.config_service_provider.listdir")
@patch("limberframework.cache.cache_service_provider.make_locker")
@mark.asyncio
async def test_cache_service_provider_cache_locker(
    mock_make_locker, mock_list_dir, app
):
    mock_list_dir.return_value = []

    config_service = await app.make("config")
    config_service["cache"] = {"locker": "None"}

    cache_service_provider = CacheServiceProvider()
    cache_service_provider.register(app)

    await app.make("cache.locker")

    mock_make_locker.assert_called_once_with({"locker": None})


@patch("limberframework.config.config_service_provider.listdir")
@patch("limberframework.cache.cache_service_provider.make_locker")
@mark.asyncio
async def test_cache_service_provider_locker_without_password(
    mock_make_locker, mock_list_dir, app
):
    mock_list_dir.return_value = []

    config_service = await app.make("config")
    config_service["cache"] = {"locker": "asyncredis"}

    cache_service_provider = CacheServiceProvider()
    cache_service_provider.register(app)

    await app.make("cache.locker")

    mock_make_locker.assert_called_once_with(
        {"locker": "asyncredis", "password": None}
    )


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
