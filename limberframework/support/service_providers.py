"""Service Providers

Classes:
- ServiceProvider: base abstract class for service providers.
"""
from abc import ABCMeta, abstractmethod

class ServiceProvider(metaclass=ABCMeta):
    """Base abstract class for service providers."""
    def __init__(self, app: 'Application') -> None:
        """Establishes the application to add the services.

        Arguments:
        app Application -- limberframework.foundation.application.Application object.
        """
        self.app = app

    @abstractmethod
    def register(self) -> None:
        """Register service bindings to the container."""
