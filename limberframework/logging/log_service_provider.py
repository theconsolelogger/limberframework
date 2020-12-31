"""Service providers for logging services."""
import sys
from os.path import join

from loguru import logger
from loguru._logger import Logger

from limberframework.foundation.application import Application
from limberframework.support.services import Service, ServiceProvider


class LogServiceProvider(ServiceProvider):
    """Provide services to a service container to handle logging."""

    def register(self, app: Application) -> None:
        """Register the log service to a service container.

        The log service returns an instance of `loguru._logger.Logger` and has
        sinks for stdout and files.

        Note:
            The log service is registered as a singleton service so that only
            one instance is created.

        Args:
            app: The service container to register the log service too.

        Example:
            >>> app = Application()
            >>> LogServiceProvider().register(app)
            >>> log = await app.make("log")
            >>> log.info("Hello World!")
        """

        async def register_log(app: Application) -> Logger:
            """Create the log service.

            Creates a new `loguru._logger.Logger` instance and adds a sink for
            stdout and for a file, overriding any previous sinks. The settings
            for the sinks are gathered from the config service, with the
            section log.stdout for the stdout sink and log.file for the file
            sink, and are passed directly to loguru. The path for the log file
            is set to the log path set in the service container, i.e
            `app.paths['log']`.

            Args:
                app: The service container to register the log service too.

            Returns:
                loguru._logger.Logger: A new Logger instance with the stdout
                    and file sinks.
            """
            config_service = await app.make("config")

            logger.remove()
            logger.add(sys.stdout, **config_service.get_section("log.stdout"))
            logger.add(
                join(app.paths["log"], f"{app.title}.log"),
                **config_service.get_section("log.file"),
            )

            return logger

        app.bind(Service("log", register_log, singleton=True))
