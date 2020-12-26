"""Establishes the service container.

The service container registers and manages services for the application.
"""
from os import getcwd
from os.path import join
from typing import Any

from fastapi import FastAPI

from limberframework.support.services import Service


class Application(FastAPI):
    """The service container for the application.

    Attributes:
        paths: A dictionary containing paths to
            core parts of the application.
        _bindings: A dictionary containing services
            bound to the service container.
        _instances: A dictionary containing created
            instances of singleton services.

    Example:
        app = Application(base_path=abspath("limber"))
    """

    def __init__(self, *args, base_path: str = None, **kwargs) -> None:
        """Establish the service container and necessary paths.

        Args:
            base_path: A string with the system path to the application.
        """
        base_path = base_path or getcwd()

        self.paths = {
            "base": base_path,
            "cache": join(base_path, "storage", "cache"),
            "config": join(base_path, "config"),
        }
        self._bindings = {}
        self._instances = {}

        super().__init__(*args, **kwargs)

    def bind(self, service: Service) -> None:
        """Bind a service to the service container.

        Args:
            service: The Service to bind.

        Raises:
            ValueError: If the service name has already
                been used to bind another service.
        """
        if service.name in self._bindings:
            raise ValueError(
                f"A service with the name {service.name} has already "
                f"be bound to the service container."
            )

        self._bindings[service.name] = service

    async def make(self, name: str) -> Any:
        """Create a new instance of a service.

        If the service is marked as a singleton then any existing
        instance will be retuned.

        Args:
            name: A string of the service name.

        Returns:
            The service, as returned by the Service closure.
        """
        try:
            binding = self._bindings[name]
        except KeyError:
            raise KeyError(
                f"Unknown service {name}, check service "
                f"is bound to the service container."
            )

        if not binding.singleton:
            return await self._bindings[name].closure(self)

        if name in self._instances:
            return self._instances[name]

        self._instances[name] = await self._bindings[name].closure(self)
        return self._instances[name]

    async def load_services(self) -> None:
        """Make instances of registered services that are not deferrable."""
        for service in self._bindings.values():
            if not service.defer:
                await self.make(service.name)
