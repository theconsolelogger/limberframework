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
def test_database_service_provider_database_connection(
    mock_create_engine, driver, connection, app
):
    app["config"]["database"] = {
        "driver": driver,
        "path": "./test.db",
        "username": "test",
        "password": "test",
        "host": "test",
        "port": "test",
        "database": "test",
    }
    app.register(DatabaseServiceProvider(app))

    database = app["db.connection"]

    assert isinstance(database, connection)


def test_database_service_provider_database_session(app):
    app["config"]["database"] = {
        "driver": "sqlite",
        "path": "./test.db",
    }
    app.register(DatabaseServiceProvider(app))

    session = app["db.session"]

    assert isinstance(session, Session)


def test_config_service_provider():
    mock_app = MagicMock()
    config = ConfigServiceProvider(mock_app)
    config.register()

    assert mock_app.bind.called_once()


@mark.parametrize(
    "driver,authenticator", [("httpbasic", HttpBasic), ("apikey", ApiKey)]
)
def test_authentication_service_provider(driver, authenticator, app):
    app["config"]["auth"] = {"driver": driver}
    app.register(AuthServiceProvider(app))

    auth = app["auth"]

    assert isinstance(auth, authenticator)


@mark.parametrize(
    "path,expected_path",
    [("/", "/"), ("/tests", "/tests"), ("./tests", f"{getcwd()}/./tests")],
)
def test_cache_service_provider_cache_store(path, expected_path, app):
    app["config"]["cache"] = {"driver": "file", "path": path}
    app.register(CacheServiceProvider(app))

    store = app["cache.store"]

    assert isinstance(store, FileStore)
    assert store.directory == expected_path


def test_cache_service_provider_cache(app):
    path = "/tests"
    app["config"]["cache"] = {"driver": "file", "path": path}
    app.register(CacheServiceProvider(app))

    store = app["cache"]

    assert isinstance(store, Cache)
