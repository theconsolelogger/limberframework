"""Database Service Provider

Classes:
- DatabaseServiceProvider: Registers database services.
"""
from sqlalchemy.orm import Session, sessionmaker
from limberframework.database.connections import Connection
from limberframework.database.connections import make_connection
from limberframework.support.service_providers import ServiceProvider

class DatabaseServiceProvider(ServiceProvider):
    """Registers database services to the service container."""
    def register(self) -> None:
        """Registers the database connection and session
        services to the service container.
        """
        def register_database_connection(app: 'Application') -> Connection:
            """Closure for establshing a database connection service.

            Arguments:
            app Application -- foundation.application.Application object

            Returns:
            Connection object
            """
            return make_connection(app['config']['database'])

        self.app.bind('db.connection', register_database_connection, True)

        def register_database_session(app: 'Application') -> Session:
            """Closure for establishing a database session
            using the existing database connection.

            Arguments:
            app Application -- foundation.application.Application object

            Returns:
            Session object
            """
            return sessionmaker(bind=app['db.connection'].engine)()

        self.app.bind('db.session', register_database_session)
