"""Service Providers

Classes:
- Service: representation of a service.
- ServiceProvider: base abstract class for service providers.
"""
from abc import ABCMeta, abstractmethod
from typing import NamedTuple


class Service(NamedTuple):
    """Represents a service which is usable by the service container."""

    name: str
    closure: callable
    singleton: bool = False
    defer: bool = False

    def __repr__(self) -> str:
        """Returns a string representation of the service."""
        return (
            f"<Service name={self.name}, closure={self.closure}, "
            f"singleton={self.singleton}, defer={self.defer}>"
        )


class ServiceProvider(metaclass=ABCMeta):
    """Base abstract class for service providers."""

    def __init__(self, app: "Application") -> None:  # noqa
        """Establishes the application to add the services.

        Arguments:
        app Application -- limberframework.foundation.application.Application
        object.
        """
        self.app = app

    @abstractmethod
    def register(self) -> None:
        """Register service bindings to the container."""
