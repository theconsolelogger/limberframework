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

    @abstractmethod
    def register(self, app: "Application") -> None:  # noqa
        """Register service bindings to the container.

        Arguments:
        app limberframework.foundation.application.Application --
        the service container.
        """
