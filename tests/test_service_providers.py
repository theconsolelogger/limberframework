from sqlalchemy.orm import Session, sessionmaker
from limberframework.config.config_service_provider import ConfigServiceProvider
from limberframework.database.connections import SqliteConnection
from limberframework.database.database_service_provider import DatabaseServiceProvider

def test_database_service_provider():
    config = {
        'driver': 'sqlite',
        'path': './sqlite.db'
    }

    database_service_provider = DatabaseServiceProvider(config)

    assert isinstance(database_service_provider.database, SqliteConnection)
    assert isinstance(database_service_provider.session, sessionmaker)
    assert isinstance(database_service_provider.session(), Session)

def test_config_service_provider():
    config = {
        'database': {
            'driver': 'sqlite',
            'path': './sqlite.db'
        }
    }

    config_service_provider = ConfigServiceProvider(config)

    assert isinstance(config_service_provider, ConfigServiceProvider)
    assert config_service_provider.configs is config
    assert config_service_provider is ConfigServiceProvider(config)
