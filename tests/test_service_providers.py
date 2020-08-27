from unittest.mock import MagicMock
from sqlalchemy.orm import Session, sessionmaker
from limberframework.cache.cache_service_provider import CacheServiceProvider
from limberframework.config.config_service_provider import ConfigServiceProvider
from limberframework.database.connections import SqliteConnection
from limberframework.database.database_service_provider import DatabaseServiceProvider
from limberframework.authentication.authentication_service_provider import (
    AuthServiceProvider,
)


def test_database_service_provider():
    mock_app = MagicMock()
    database = DatabaseServiceProvider(mock_app)
    database.register()

    assert mock_app.bind.call_count == 2


def test_config_service_provider():
    mock_app = MagicMock()
    config = ConfigServiceProvider(mock_app)
    config.register()

    assert mock_app.bind.called_once()


def test_authentication_service_provider():
    mock_app = MagicMock()
    auth = AuthServiceProvider(mock_app)
    auth.register()

    assert mock_app.bind.called_once()


def test_cache_service_provider():
    mock_app = MagicMock()
    cache = CacheServiceProvider(mock_app)
    cache.register()

    assert mock_app.bind.call_count == 2
