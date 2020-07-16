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

### Fixed
- Resolve SQLite single thread warning by turning off 'same thread check'.
