"""Database Service Provider

Classes:
- DatabaseServiceProvider: Manages connections and sessions with databases.
"""
from typing import Dict
from sqlalchemy.orm import sessionmaker
from limberframework.database.connections import make_connection
from limberframework.support.metaclasses import Singleton

class DatabaseServiceProvider(metaclass=Singleton):
    """Manages connections and sessions with databases.

    Attributes:
    - database Connection -- a Connection object with access to the database engine.
    - session Session -- a callable Session object to create new sessions.
    """
    def __init__(self, config: Dict) -> None:
        """Establishes a connection to the database and prepares sessions.

        Arguments:
        - config dict -- connection settings for the database.
        """
        self.database = make_connection(config)
        self.session = sessionmaker(autocommit=False, autoflush=False,
                                    bind=self.database.engine)
