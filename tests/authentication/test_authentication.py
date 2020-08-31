from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from fastapi.exceptions import HTTPException

from limberframework.authentication.authenticators import (
    ApiKey,
    HttpBasic,
    authorise,
    make_authenticator,
)


@pytest.mark.asyncio
async def test_make_authenticator_unknown_driver():
    driver = "test"

    with pytest.raises(Exception) as exc:
        await make_authenticator({"driver": driver})

    assert f"Unsupported authenticator {driver}." in str(exc.value)


@pytest.mark.asyncio
async def test_make_authenticator_known_driver():
    http_basic = await make_authenticator({"driver": "httpbasic"})
    api_key = await make_authenticator({"driver": "apikey"})

    assert isinstance(http_basic, HttpBasic)
    assert isinstance(api_key, ApiKey)


def test_api_key_get_user_id():
    key = "test"
    user_id = 1
    mock_session = Mock()
    mock_session.execute.return_value.scalar.return_value = user_id

    api_key = ApiKey()
    response = api_key.get_user_id(mock_session, {"apikey": key})

    mock_session.execute.assert_called_with(
        "SELECT user_id FROM apikey WHERE key=:key", {"key": key}
    )
    mock_session.execute.return_value.scalar.assert_called_once()
    assert response == user_id


def test_http_basic_get_user_id():
    username = "test"
    password = "test"
    user_id = 1
    mock_session = Mock()
    mock_session.execute.return_value.scalar.return_value = user_id

    http_basic = HttpBasic()
    response = http_basic.get_user_id(
        mock_session, {"username": username, "password": password}
    )

    mock_session.execute.assert_called_with(
        "SELECT id FROM user WHERE username=:username AND password=:password",
        {"username": username, "password": password},
    )
    mock_session.execute.return_value.scalar.assert_called_once()
    assert response == user_id


@pytest.mark.asyncio
@patch("limberframework.authentication.authenticators.APIKeyHeader")
async def test_api_key_authorise_unauthorised(mock_api_key):
    key = "test"
    mock_api_key.return_value = AsyncMock(return_value=key)
    mock_request = MagicMock()

    api_key = ApiKey()
    api_key.get_user_id = Mock(return_value=None)

    with pytest.raises(HTTPException):
        await api_key.authorise(mock_request)


@pytest.mark.asyncio
@patch("limberframework.authentication.authenticators.APIKeyHeader")
async def test_api_key_authorise_authorised(mock_api_key):
    key = "test"
    user_id = 1
    mock_api_key.return_value = AsyncMock(return_value=key)
    mock_request = MagicMock()

    api_key = ApiKey()
    api_key.get_user_id = Mock(return_value=user_id)

    response = await api_key.authorise(mock_request)

    assert response == user_id


@pytest.mark.asyncio
@patch("limberframework.authentication.authenticators.HTTPBasic")
async def test_http_basic_authorise_unauthorised(mock_http_basic):
    credentials = Mock()
    mock_http_basic.return_value = AsyncMock(return_value=credentials)
    mock_request = MagicMock()

    http_basic = HttpBasic()
    http_basic.get_user_id = Mock(return_value=None)

    with pytest.raises(HTTPException):
        await http_basic.authorise(mock_request)


@pytest.mark.asyncio
@patch("limberframework.authentication.authenticators.HTTPBasic")
async def test_http_basic_authorise_authorised(mock_http_basic):
    credentials = Mock()
    user_id = 1
    mock_http_basic.return_value = AsyncMock(return_value=credentials)
    mock_request = MagicMock()

    http_basic = HttpBasic()
    http_basic.get_user_id = Mock(return_value=user_id)

    response = await http_basic.authorise(mock_request)

    assert response == user_id


@pytest.mark.asyncio
async def test_authorise():
    user_id = 1

    mock_auth = AsyncMock()
    mock_auth.authorise.return_value = user_id
    mock_request = AsyncMock()
    mock_request.app.__getitem__.return_value = mock_auth

    authorised = await authorise(mock_request)

    assert authorised == user_id
