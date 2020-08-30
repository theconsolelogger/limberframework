from unittest.mock import AsyncMock, MagicMock, Mock

from pytest import mark, raises

from limberframework.database.middleware import DatabaseSessionMiddleware


@mark.asyncio
async def test_dispatch_database_session_middleware_without_exception():
    mock_request = MagicMock()
    mock_request.app.__getitem__.return_value = Mock()

    mock_call_next = AsyncMock()

    middleware = DatabaseSessionMiddleware(Mock())
    await middleware.dispatch(mock_request, mock_call_next)

    mock_request.app.__getitem__.return_value.commit.assert_called_once()
    mock_request.app.__getitem__.return_value.close.assert_called_once()


@mark.asyncio
async def test_dispatch_database_session_middleware_with_exception():
    mock_request = MagicMock()
    mock_request.app.__getitem__.return_value = Mock()

    mock_call_next = AsyncMock()
    mock_call_next.side_effect = Exception()

    middleware = DatabaseSessionMiddleware(Mock())

    with raises(Exception):
        await middleware.dispatch(mock_request, mock_call_next)

    mock_request.app.__getitem__.return_value.commit.assert_not_called()
    mock_request.app.__getitem__.return_value.close.assert_called_once()
