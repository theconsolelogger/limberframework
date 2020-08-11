# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Changed
- psycopg2-binary package to psycopg2.

## [0.1.0] - 2020-08-09
### Added
- Documentation files: README.md; LICENSE.txt; CONTRIBUTING.md; CODEOFCONDUCT.md; and, CHANGELOG.md.
- Database connection and session management for SQLite and PostgreSQL databases.
- Configuration service provider to manage configuration settings and add dotenv file support.
- Application class to act as a service container that manages available services.
- Config class to manage application configuration.
- DatabaseSessionMiddleware to automatically establish a database session when a request is received.
- Model class for providing a base class for SQLAlchemy declarative classes with convenience methods.
- Add methods to add, update, and delete Model classes.
- Soft delete property to Model class to remove Models without deleting from the database.
- Tests for config/config module.
- Test for creating a PostgresConnection instance.
- Authentication service provider along with HTTP Basic and API Key authenticators.
- Hasher class to handle hashing values.
- FileSystem class to handle reading and writing files on the file system.
- Cache services, including FileStore to cache data in files and the Cache class to interact with the cache.
- Base path attribute to Application class used to work out the location of the app.
- Rate limiting features, including RateLimiter class and ThrottleRequests middleware.

### Fixed
- Resolve SQLite single thread warning by turning off 'same thread check'.
- Authenticator factory function now accepts a dictionary containing configurations for an authenticator.
- Authenticator factory function tests to pass a config dictionary rather than a string.

### Changed
- DatabaseServiceProvider to implement required methods by ServiceProvider for registering services with with the Application class.
- ConfigServiceProvider to implement required methods by ServiceProvider for registering services with the Application class.
- Database session to autocommit and autoflush.
- Commit session to database after processing the request in the DatabaseSessionMiddleware.
- Pipenv to poetry for package management and distribution.

### Removed
- Singleton metaclass as singletons are now handled by the Application class.
