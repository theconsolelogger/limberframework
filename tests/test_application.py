from unittest.mock import MagicMock
from pytest import fixture, raises
from limberframework.foundation.application import Application

@fixture
def application():
    return Application()

def test_register_service_provider(application):
    mock_service_provider = MagicMock()

    application.register(mock_service_provider)

    mock_service_provider.register.assert_called_once()

def test_bind_service(application):
    name = 'test'
    mock_closure = MagicMock()
    singleton = True

    application.bind(name, mock_closure, singleton)

    assert application.bindings == {
        name: {
            'closure': mock_closure,
            'singleton': singleton
        }
    }

def test_make_unknown_service(application):
    name = 'test'

    with raises(KeyError) as exception:
        application.make(name)

    assert f"Unknown service {name}, check service is bound to the service container." in str(exception.value)

def test_make_known_non_singleton_service(application):
    name = 'test'
    closure = MagicMock
    singleton = False

    application.bind(name, closure, singleton)
    service_1 = application.make(name)
    service_2 = application.make(name)

    assert isinstance(service_1, MagicMock)
    assert isinstance(service_2, MagicMock)
    assert service_1 is not service_2

def test_make_known_singleton_service(application):
    name = 'test'
    closure = MagicMock
    singleton = True

    application.bind(name, closure, singleton)
    service_1 = application.make(name)
    service_2 = application.make(name)

    assert isinstance(service_1, MagicMock)
    assert isinstance(service_2, MagicMock)
    assert service_1 is service_2

def test_get_item(application):
    name = 'test'
    closure = MagicMock
    singleton = True

    application.bind(name, closure, singleton)
    service = application[name]

    assert isinstance(service, MagicMock)