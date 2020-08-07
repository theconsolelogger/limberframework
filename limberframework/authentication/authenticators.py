"""Authenticators

Classes:
Authenticator -- base Authenticator class.
HttpBasic -- Authenticator for username and password auth.
ApiKey -- Authenticator for api key auth.

Functions:
make_authenticator -- factory function to make an authenticator.
authorise -- authorise a request using the established authenticator.
"""

from abc import ABCMeta, abstractmethod
from typing import Dict, Optional, Union
from fastapi import Request
from fastapi.security.http import HTTPBasic
from fastapi.security.api_key import APIKeyHeader
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session
from starlette.status import HTTP_401_UNAUTHORIZED

class Authenticator(metaclass=ABCMeta):
    """Base Authenticator class.

    Attributes:
    user_id int -- id of user that matches the request credentials.
    """
    def __init__(self) -> None:
        """Establishes the Authenticator."""
        self.user_id: int = None

    @abstractmethod
    async def authorise(self, request: Request) -> Optional[int]:
        """Checks the request for authorisation.

        Arguments:
        request Request -- a request object.

        Returns:
        int -- user id that matches the credentials.
        """

    @abstractmethod
    def get_user_id(self, session: Session, credentials: Dict) -> Union[int, None]:
        """Find the user id that matches the given credentials.

        Arguments:
        session Session -- Session to use for querying the database.
        credentials Dict -- authorisation credentials.

        Returns:
        int -- user id.
        none -- no user id is found for the credentials.
        """

    @staticmethod
    def respond_unauthorized() -> None:
        """Raises a HTTP 401 exception as a response."""
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

class HttpBasic(Authenticator):
    """An Authenticator for HTTP basic authentication,
    username and password."""
    @staticmethod
    def get_user_id(session: Session, credentials: Dict) -> Union[int, None]:
        """Find the user id that matches the username
        and password in the user table.

        Arguments:
        session Session -- Session object.
        credentials Dict -- contains username and password.

        Returns:
        int -- user id.
        none -- no user is found for the credentials.
        """
        user_id = session.execute(
            "SELECT id FROM user WHERE username=:username AND password=:password",
            {
                "username": credentials['username'],
                "password": credentials['password']
            }
        ).scalar()

        return user_id

    async def authorise(self, request: Request) -> Optional[int]:
        """Check the credentials of a request
        are found in the database.

        Arguments:
        request Request -- Request object.

        Returns:
        int -- user id.
        """
        credentials = await HTTPBasic()(request)
        user_id = self.get_user_id(request.app['db.session'], credentials.dict())

        if not user_id:
            self.respond_unauthorized()

        self.user_id = user_id
        return user_id

class ApiKey(Authenticator):
    """An Authenticator for API key in the header authentication."""
    @staticmethod
    def get_user_id(session: Session, credentials: Dict) -> Union[int, None]:
        """Find the user id that matches the api key
        in the apikey table.

        Arguments:
        session Session -- Session object.
        credentials Dict -- contains apikey.

        Returns:
        int -- user id.
        none -- no user is found for the credentials.
        """
        user_id = session.execute(
            "SELECT user_id FROM apikey WHERE key=:key",
            {"key": credentials['apikey']}
        ).scalar()

        return user_id

    async def authorise(self, request: Request) -> Optional[int]:
        """Check the credentials of a request
        are found in the database.

        Arguments:
        request Request -- Request object.

        Returns:
        int -- user id.
        """
        api_key = await APIKeyHeader(name='token')(request)
        user_id = self.get_user_id(request.app['db.session'], api_key)

        if not user_id:
            self.respond_unauthorized()

        self.user_id = user_id
        return user_id

def make_authenticator(config: Dict) -> Authenticator:
    """Factory function to establish the authenticator.

    Arguments:
    driver str -- name of Authenticator to use for authorisation.

    Returns:
    Authenticator
    """
    if config['driver'] == 'httpbasic':
        return HttpBasic()
    if config['driver'] == 'apikey':
        return ApiKey()

    raise Exception(f"Unsupported authenticator {config['driver']}.")

async def authorise(request: Request) -> Optional[int]:
    """Authorises a request by calling the authorise
    method of the configured Authenticator.

    Arguments:
    request Request -- request object to authorise.

    Returns:
    int -- user id for the given credentials.
    """
    return await request.app['auth'].authorise(request)
