from unittest.mock import AsyncMock, MagicMock

from pytest import fixture, mark, raises

from limberframework.foundation.application import Application


@fixture
def application():
    return Application()


def test_register_service_provider(application):
    mock_service_provider = MagicMock()

    application.register(mock_service_provider)

    mock_service_provider.register.assert_called_once()


def test_bind_service(application):
    name = "test"
    mock_closure = MagicMock()
    singleton = True
    defer = True

    application.bind(name, mock_closure, singleton, defer)

    assert application.bindings == {
        name: {"closure": mock_closure, "singleton": singleton, "defer": defer}
    }


@mark.asyncio
async def test_make_unknown_service(application):
    name = "test"

    with raises(KeyError) as exception:
        await application.make(name)

    assert (
        f"Unknown service {name}, check service "
        f"is bound to the service container." in str(exception.value)
    )


@mark.asyncio
async def test_make_known_non_singleton_service(application):
    name = "test"

    def return_closure(app):
        return AsyncMock()

    closure = AsyncMock(side_effect=return_closure)
    singleton = False

    application.bind(name, closure, singleton)
    service_1 = await application.make(name)
    service_2 = await application.make(name)

    assert isinstance(service_1, AsyncMock)
    assert isinstance(service_2, AsyncMock)
    assert service_1 is not service_2


@mark.asyncio
async def test_make_known_singleton_service(application):
    name = "test"
    closure = AsyncMock()
    singleton = True

    application.bind(name, closure, singleton)
    service_1 = await application.make(name)
    service_2 = await application.make(name)

    assert isinstance(service_1, AsyncMock)
    assert isinstance(service_2, AsyncMock)
    assert service_1 is service_2


@mark.asyncio
async def test_load_services(application):
    mock_closure = AsyncMock()
    mock_make = AsyncMock()

    application.make = mock_make
    services = [
        {
            "name": "cache",
            "closure": mock_closure,
            "singleton": True,
            "defer": False,
        },
        {
            "name": "auth",
            "closure": mock_closure,
            "singleton": False,
            "defer": True,
        },
    ]

    for service in services:
        application.bind(
            service["name"],
            service["closure"],
            service["singleton"],
            service["defer"],
        )

    await application.load_services()

    application.make.assert_called_once_with(services[0]["name"])


@mark.asyncio
async def test_get_item(application):
    name = "test"
    closure = AsyncMock()
    singleton = True

    application.bind(name, closure, singleton)
    service = await application[name]

    assert isinstance(service, AsyncMock)
