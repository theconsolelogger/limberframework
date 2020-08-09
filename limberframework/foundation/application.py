"""Application

Classes:
- Application: service container that registers and manages services.
"""
from os import getcwd
from typing import Any
from fastapi import FastAPI
from limberframework.support.service_providers import ServiceProvider

class Application(FastAPI):
    """The service container for the application,
    registering and managing services.

    Attributes:
    config dict -- application configuration settings.
    bindings dict -- services bound to the service container.
    instances dict -- instances of singleton services.
    """
    def __init__(self, base_path: str = None, *args, **kwargs) -> None:
        """Establishes the service container."""
        self.base_path = base_path or getcwd()
        self.bindings = {}
        self.instances = {}

        super().__init__(*args, **kwargs)

    def register(self, service_provider: ServiceProvider) -> None:
        """Register a service provider with the application.

        Arguments:
        service_provider ServiceProvider -- ServiceProvider object.
        """
        service_provider.register()

    def bind(self, name, closure, singleton=False) -> None:
        """Bind a service to the application.

        Arguments:
        name str -- name of the service.
        closure function -- function to call to create the service.
        singleton bool -- whether multiple instances of the service are allowed.
        """
        self.bindings[name] = {
            'closure': closure,
            'singleton': singleton
        }

    def make(self, name: str) -> Any:
        """Create a new instance of a service, if the service
        is marked as a singleton then any existing
        instance will be retuned.

        Arguments:
        name str -- name of the service.

        Returns:
        Any -- an instance of the service.
        """
        try:
            binding = self.bindings[name]
        except KeyError:
            raise KeyError(f'Unknown service {name}, check service '
                           f'is bound to the service container.')

        # If service is not a singleton, return a new instance.
        if not binding['singleton']:
            return self.bindings[name]['closure'](self)

        # If an existing instance of the singleton
        # service is available return it.
        if name in self.instances.keys():
            return self.instances[name]

        # Otherwise create a new instance and store it.
        self.instances[name] = self.bindings[name]['closure'](self)
        return self.instances[name]

    def __getitem__(self, name: str) -> Any:
        """Retrieve a service.

        Arguments:
        name str -- name of the service.

        Returns:
        Any -- an instance of the service.
        """
        return self.make(name)
