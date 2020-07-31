# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
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

### Fixed
- Resolve SQLite single thread warning by turning off 'same thread check'.

### Changed
- DatabaseServiceProvider to implement required methods by ServiceProvider for registering services with with the Application class.
- ConfigServiceProvider to implement required methods by ServiceProvider for registering services with the Application class.
- Database session to autocommit and autoflush.
- Commit session to database after processing the request in the DatabaseSessionMiddleware.

### Removed
- Singleton metaclass as singletons are now handled by the Application class.
