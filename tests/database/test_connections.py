from pytest import mark, raises
from sqlalchemy.engine import Engine

from limberframework.database.connections import (
    ServerConnection,
    SqliteConnection,
    make_connection,
)


@mark.parametrize(
    "config",
    [
        (
            {
                "driver": "mysql+mysqldb",
                "username": "root",
                "password": "toor",
                "host": "localhost",
                "port": 5432,
                "database": "public",
            }
        ),
        (
            {
                "driver": "postgresql",
                "username": "admin",
                "password": "pass1234",
                "host": "postgres",
                "port": 2500,
                "database": "test",
            }
        ),
    ],
)
def test_server_connection(config):
    server_connection = ServerConnection(**config)

    assert isinstance(server_connection, ServerConnection)
    assert isinstance(server_connection.engine, Engine)
    assert server_connection.driver == config["driver"]
    assert server_connection.username == config["username"]
    assert server_connection.password == config["password"]
    assert server_connection.host == config["host"]
    assert server_connection.port == config["port"]
    assert server_connection.database == config["database"]


@mark.parametrize(
    "path", [("./sqlite.db"), ("../database"), ("./database/file.db")]
)
def test_sqlite_connection(path):
    sqlite_connection = SqliteConnection(path)

    assert isinstance(sqlite_connection, SqliteConnection)
    assert isinstance(sqlite_connection.engine, Engine)
    assert sqlite_connection.path == path


@mark.parametrize(
    "config,expected_url",
    [
        (
            {
                "driver": "mysql+mysqldb",
                "username": "root",
                "password": "toor",
                "host": "localhost",
                "port": 5432,
                "database": "public",
            },
            "mysql+mysqldb://root:toor@localhost:5432/public",
        ),
        (
            {
                "driver": "postgresql",
                "username": "admin",
                "password": "pass1234",
                "host": "postgres",
                "port": 2500,
                "database": "test",
            },
            "postgresql://admin:pass1234@postgres:2500/test",
        ),
    ],
)
def test_server_connection_get_url(config, expected_url):
    server_connection = ServerConnection(**config)

    url = server_connection.get_url()

    assert expected_url in url


@mark.parametrize(
    "path,expected_url",
    [
        ("./sqlite.db", "sqlite:///./sqlite.db"),
        ("../database", "sqlite:///../database"),
        ("./database/file.db", "sqlite:///./database/file.db"),
    ],
)
def test_sqlite_connection_get_url(path, expected_url):
    sqlite_connection = SqliteConnection(path)

    url = sqlite_connection.get_url()

    assert expected_url in url


@mark.asyncio
async def test_make_connection_with_invalid_config():
    config = {"driver": "sqlite"}

    with raises(KeyError) as exception:
        await make_connection(config)

    assert "path" in str(exception.value)


@mark.asyncio
async def test_make_connection_with_invalid_driver():
    config = {"driver": "invalid_driver"}

    with raises(Exception) as exception:
        await make_connection(config)

    assert f"Unsupported driver {config['driver']}" in str(exception.value)


@mark.parametrize(
    "config,connection_class",
    [
        (
            {
                "driver": "mysql+mysqldb",
                "username": "root",
                "password": "toor",
                "host": "localhost",
                "port": 5432,
                "database": "public",
            },
            ServerConnection,
        ),
        (
            {
                "driver": "postgresql",
                "username": "admin",
                "password": "pass1234",
                "host": "postgres",
                "port": 2500,
                "database": "test",
            },
            ServerConnection,
        ),
        (
            {
                "driver": "sqlite",
                "path": "./sqlite.db",
            },
            SqliteConnection,
        ),
    ],
)
@mark.asyncio
async def test_make_connection(config, connection_class):
    response = await make_connection(config)

    assert isinstance(response, connection_class)
