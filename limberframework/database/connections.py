"""Handles establishing connections to different DBMSs."""
from abc import ABCMeta, abstractmethod
from typing import Dict

from sqlalchemy import create_engine


class Connection(metaclass=ABCMeta):
    """Base class for a connection.

    Attributes:
        engine: The connection to the database.
    """

    def __init__(self, connect_args: Dict = {}) -> None:
        """Establish a connection to the database.

        Args:
            connect_args: Connection options for the database.
        """
        self.engine = create_engine(self.get_url(), connect_args=connect_args)

    @abstractmethod
    def get_url(self) -> str:
        """Return the URL to for the database."""


class ServerConnection(Connection):
    """Connection to a database located on a server.

    Attributes:
        driver: Driver used to connect to the database.
        username: Username to connect to the database.
        password: Password to connect to the database.
        host: Name of the host with the database.
        port: Port to communicate with the database on the host.
        database: Name of the database.
    """

    def __init__(
        self,
        driver: str,
        username: str,
        password: str,
        host: str,
        port: int,
        database: str,
    ) -> None:
        """Establish the information needed to connect to the database.

        Args:
            driver: Driver used to connect to the database.
            username: Username to connect to the database.
            password: Password to connect to the database.
            host: Name of the host with the database.
            port: Port to communicate with the database on the host.
            database: Name of the database.
        """
        self.driver = driver
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.database = database

        super().__init__()

    def get_url(self) -> str:
        """Return the URL to for the database."""
        return (
            f"{self.driver}://{self.username}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )


class SqliteConnection(Connection):
    """Connection to a SQLite database.

    Attributes:
        path: Location of the database on the file system.
    """

    def __init__(self, path: str) -> None:
        """Establish the information needed to connect to the database.

        Args:
            path: Path to database on the file system.
        """
        self.path = path

        super().__init__({"check_same_thread": False})

    def get_url(self) -> str:
        """Return the URL to for the database."""
        return f"sqlite:///{self.path}"


async def make_connection(config: Dict) -> Connection:
    """Establish a connection to the database.

    Args:
        config: Information required to establish the connection.

    Returns:
        Connection: The created connection to the database.

    Raises:
        ValueError: If the driver for the database
            in `config` is not recognised.
    """
    if config["driver"] in ["mysql+mysqldb", "postgresql"]:
        return ServerConnection(
            config["driver"],
            config["username"],
            config["password"],
            config["host"],
            config["port"],
            config["database"],
        )
    elif config["driver"] == "sqlite":
        return SqliteConnection(config["path"])

    raise ValueError(f"Unsupported driver {config['driver']}")
