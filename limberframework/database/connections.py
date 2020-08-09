"""Connections

Handles establishing connections
to different DBMSs.

Classes:
- Connection: base class for a connection.
- PostgresConnection: connection for a PostgreSQL database.
- SqliteConnection: connection for a SQLite database.

Functions:
- make_connection: factory for creating a connection.
"""
from abc import ABCMeta, abstractmethod
from typing import Dict
from sqlalchemy import create_engine

class Connection(metaclass=ABCMeta):
    """Base class for a connection.

    Attributes:
    - engine Engine -- a connection to the database.
    """
    def __init__(self, connect_args: Dict = {}) -> None:
        """Establishes a connection to the database.

        Arguments:
        - connect_args Dict -- connection options for the database.
        """
        self.engine = create_engine(self.get_url(), connect_args=connect_args)

    @abstractmethod
    def get_url(self) -> str:
        """Returns the URL to for the database."""

class PostgresConnection(Connection):
    """Connection to a PostgreSQL database.

    Attributes:
    - username str -- username to connect to the database.
    - password str -- password to connect to the database.
    - host str -- name of the host with the database.
    - port int -- port to communicate with the database on the host.
    - database str -- name of the database.
    """
    def __init__(self, username: str, password: str, host: str, port: int, database: str) -> None:
        """Establishes the information needed to connect to the database.

        Arguments:
        - username str -- username to connect to the database.
        - password str -- password to connect to the database.
        - host str -- name of the host with the database.
        - port int -- port to communicate with the database on the host.
        - database str -- name of the database.
        """
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.database = database

        super().__init__()

    def get_url(self) -> str:
        """Returns the URL to for the database."""
        return (
            f"postgresql://{self.username}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )

class SqliteConnection(Connection):
    """Connection to a SQLite database.

    Attributes:
    - path str -- location of the database on the file system.
    """
    def __init__(self, path: str) -> None:
        """Establishes the information needed to connect to the database.

        Arguments:
        - path str -- path to database on the file system.
        """
        self.path = path

        super().__init__({"check_same_thread": False})

    def get_url(self) -> str:
        """Returns the URL to for the database."""
        return f"sqlite:///{self.path}"

def make_connection(config: Dict) -> Connection:
    """Factory function to establish a connection to the database.

    Arguments:
    - config Dict -- information required to establish the connection.

    Returns:
    - Connection -- a connection object.
    """
    if config['driver'] == 'pgsql':
        return PostgresConnection(
            config['username'],
            config['password'],
            config['host'],
            config['port'],
            config['database']
        )
    elif config['driver'] == 'sqlite':
        return SqliteConnection(
            config['path']
        )

    raise Exception(f"Unsupported driver {config['driver']}")
