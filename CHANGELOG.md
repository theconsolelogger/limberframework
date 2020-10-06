# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Fixed
- test_make_store_file_store test to pass cache path inside the config dictionary.
- circular import in support/service_provider between ServiceProvider and Application.
- test_async_redis_add_key_does_not_exist to mock the expireat method with AsyncMock.
- storing locks in a Locker by correcting the `_locks` attribute name in `AsyncRedisLocker`.
- the passing of cache configuration settings from `make_locker()` to `AsyncRedisLocker`.
- the setting of an expire time for a resource in a Redis cache using `AsyncRedisStore`.
- issues with mocking in test for checking the prevention of too many requests, `test_dispatch_too_many_requests_exception`.
- `make_locker` raising `ValueError` for unknown locker.
- improve documentation for the `Application` class.

### Added
- deferrable services which will be loaded when needed.
- loading of services that are not deferrable so that they are ready for a request.
- RedisStore and MemcacheStore to interact with a redis or memcache server and use to cache data.
- Black code formatter to provide a consistent format for the project.
- flake8 to enforce PEP8 styling.
- pytest pre-commit hook to run tests before committing.
- tests to authentication, database middleware, routing middleware, and service providers to increase test coverage to 100%.
- isort pre-commit hook for consistent ordering of imports.
- support for async services by Application.
- AsyncRedisStore to support asynchronous Redis communication.
- cache locker service to lock resources in the cache database, including the AsyncRedisLocker service.
- tests for `locker` module.
- `Service` class to represent a service that is required by the service container.
- check for a used service name when attempting to bind a new service to the service container in `Application.bind()`.

### Changed
- restructured tests to match project structure for consistency.
- `Application` class to use the `Service` class when binding a service.
- `Application.bind()` to check for instances of a singleton service without `.keys()`.
- `Application` class bindings and instances private attributes.

### Removed
- `__getitem__()` from `Application` class as it no longer fits with the async capability of the class.

## [0.1.1] - 2020-08-11
### Changed
- psycopg2-binary package to psycopg2.
- FileStore path to be constructed by CacheServiceProvider from the application base path and cache storage path, and allow the path to be fully overridden with an environment variable.
- Add version 0.1.1 to pyproject.toml

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
- Hasher class to a callable to hash a value rather than using the `hash()` method.

### Removed
- Singleton metaclass as singletons are now handled by the Application class.
