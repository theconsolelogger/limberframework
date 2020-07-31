from unittest.mock import patch
from pytest import raises, mark
from sqlalchemy.engine import Engine
from limberframework.database.connections import Connection, PostgresConnection, SqliteConnection, make_connection

@mark.parametrize('config', [
    ({
        'username': 'root',
        'password': 'toor',
        'host': 'localhost',
        'port': 5432,
        'database': 'public'
    }),
    ({
        'username': 'admin',
        'password': 'pass1234',
        'host': 'postgres',
        'port': 2500,
        'database': 'test'
    })
])
def test_postgres_connection(config):
    postgres_connection = PostgresConnection(
        **config
    )

    assert isinstance(postgres_connection, PostgresConnection)
    assert isinstance(postgres_connection.engine, Engine)
    assert postgres_connection.username == config['username']
    assert postgres_connection.password == config['password']
    assert postgres_connection.host == config['host']
    assert postgres_connection.port == config['port']
    assert postgres_connection.database == config['database']

@mark.parametrize('path', [
    ('./sqlite.db'),
    ('../database'),
    ('./database/file.db')
])
def test_sqlite_connection(path):
    sqlite_connection = SqliteConnection(path)

    assert isinstance(sqlite_connection, SqliteConnection)
    assert isinstance(sqlite_connection.engine, Engine)
    assert sqlite_connection.path == path

@mark.parametrize('config,expected_url', [
    ({
        'username': 'root',
        'password': 'toor',
        'host': 'localhost',
        'port': 5432,
        'database': 'public'
    }, 'postgresql://root:toor@localhost:5432/public'),
    ({
        'username': 'admin',
        'password': 'pass1234',
        'host': 'postgres',
        'port': 2500,
        'database': 'test'
    }, 'postgresql://admin:pass1234@postgres:2500/test'),
])
def test_pgsql_connection_get_url(config, expected_url):
    postgres_connection = PostgresConnection(
        **config
    )

    url = postgres_connection.get_url()

    assert expected_url in url

@mark.parametrize('path,expected_url', [
    ('./sqlite.db', 'sqlite:///./sqlite.db'),
    ('../database', 'sqlite:///../database'),
    ('./database/file.db', 'sqlite:///./database/file.db')
])
def test_sqlite_connection_get_url(path, expected_url):
    sqlite_connection = SqliteConnection(path)

    url = sqlite_connection.get_url()

    assert expected_url in url

def test_make_connection_with_invalid_config():
    config = { 'driver': 'sqlite' }

    with raises(KeyError) as exception:
        make_connection(config)

    assert f"path" in str(exception.value)

def test_make_connection_with_invalid_driver():
    config = { 'driver': 'invalid_driver' }

    with raises(Exception) as exception:
        make_connection(config)

    assert f"Unsupported driver {config['driver']}" in str(exception.value)

def test_make_connection_pgsql():
    config = {
        'driver': 'pgsql',
        'username': 'test',
        'password': 'test',
        'host': 'test',
        'port': 5432,
        'database': 'test'
    }

    response = make_connection(config)

    assert isinstance(response, PostgresConnection)
