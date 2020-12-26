"""Provide services related to the database."""
from sqlalchemy.orm import Session, sessionmaker

from limberframework.database.connections import Connection, make_connection
from limberframework.foundation.application import Application
from limberframework.support.services import Service, ServiceProvider


class DatabaseServiceProvider(ServiceProvider):
    """Register database services to the service container."""

    def register(self, app: Application) -> None:
        """Register the database and session services to the service container.

        Args:
            app: The Application.
        """

        async def register_database_connection(app: Application) -> Connection:
            """Closure for establshing a database connection service.

            Args:
                app: The Application.

            Returns:
                Connection: A connection to the database.
            """
            config_service = await app.make("config")
            config = config_service.get_section("database")
            return await make_connection(config)

        app.bind(Service("db.connection", register_database_connection))

        async def register_database_session(app: Application) -> Session:
            """Closure for establishing a database session.

            Creates a database session using the existing database connection.

            Args:
                app: The Application.

            Returns:
                Session: A session to the database.
            """
            db_connection = await app.make("db.connection")
            return sessionmaker(bind=db_connection.engine)()

        app.bind(Service("db.session", register_database_session, defer=True))
