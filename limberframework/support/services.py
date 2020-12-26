"""Foundations of services which can be bound to the service container."""
from abc import ABCMeta, abstractmethod
from typing import NamedTuple


class Service(NamedTuple):
    """Represents a service which is usable by the service container.

    Attributes:
        name: A string for the name of the service.
        closure: A callable for creating the service.
        singleton: A boolean indicating whether to create
            only one instance of the service.
        defer: A boolean indicating whether to wait before
            creating the service until it is requested.
    """

    name: str
    closure: callable
    singleton: bool = False
    defer: bool = False

    def __repr__(self) -> str:
        """Provide a string representation of the service.

        Returns:
            str: string representation.
        """
        return (
            f"<Service name={self.name}, closure={self.closure}, "
            f"singleton={self.singleton}, defer={self.defer}>"
        )


class ServiceProvider(metaclass=ABCMeta):
    """Base abstract class for service providers.

    This class can be used to register a service provider
    with the service container.

    Usage:
        ServiceProvider.register(app)
    """

    @abstractmethod
    def register(self, app: "Application") -> None:  # noqa
        """Register service bindings to the container.

        Args:
            app: The Application.
        """
