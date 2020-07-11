from sqlalchemy.orm import Session, sessionmaker
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
