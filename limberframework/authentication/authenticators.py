"""Available authenticators to authenticate a request."""

from abc import ABCMeta, abstractmethod
from typing import Dict, Optional

from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.security.api_key import APIKeyHeader
from fastapi.security.http import HTTPBasic
from sqlalchemy.orm.session import Session
from starlette.status import HTTP_401_UNAUTHORIZED


class Authenticator(metaclass=ABCMeta):
    """Base Authenticator class.

    Attributes:
        user_id: id of user that matches the request credentials.
    """

    def __init__(self) -> None:
        """Establish the Authenticator."""
        self.user_id: int = None

    @abstractmethod
    async def authorise(self, request: Request) -> Optional[int]:
        """Check the request for authorisation.

        Args:
            request: A request object.

        Returns:
            int: User id that matches the credentials.
        """

    @abstractmethod
    def get_user_id(
        self, session: Session, credentials: Dict
    ) -> Optional[int]:
        """Find the user id that matches the given credentials.

        Args:
            session: Session to use for querying the database.
            credentials: Authorisation credentials.

        Returns:
            int: User id.
        """

    @staticmethod
    def respond_unauthorized() -> None:
        """Raise a HTTP 401 exception as a response."""
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )


class HttpBasic(Authenticator):
    """An Authenticator for HTTP basic authentication."""

    @staticmethod
    def get_user_id(session: Session, credentials: Dict) -> Optional[int]:
        """Find the user id that matches the username and password in the user table.

        Args:
            session: Session object.
            credentials: Contains username and password.

        Returns:
            int: user id.
        """
        user_id = session.execute(
            "SELECT id FROM user WHERE username=:username AND "
            "password=:password",
            {
                "username": credentials["username"],
                "password": credentials["password"],
            },
        ).scalar()

        return user_id

    async def authorise(self, request: Request) -> Optional[int]:
        """Check the credentials of a request are found in the database.

        Arguments:
        request Request -- Request object.

        Returns:
        int -- user id.
        """
        credentials = await HTTPBasic()(request)
        user_id = self.get_user_id(
            request.app.make("db.session"), credentials.dict()
        )

        if not user_id:
            self.respond_unauthorized()

        self.user_id = user_id
        return user_id


class ApiKey(Authenticator):
    """An Authenticator for API key in the header authentication."""

    @staticmethod
    def get_user_id(session: Session, credentials: Dict) -> Optional[int]:
        """Find the user id that matches the api key in the apikey table.

        Args:
            session: Session object.
            credentials: contains apikey.

        Returns:
            int: User id.
            none: No user is found for the credentials.
        """
        user_id = session.execute(
            "SELECT user_id FROM apikey WHERE key=:key",
            {"key": credentials["apikey"]},
        ).scalar()

        return user_id

    async def authorise(self, request: Request) -> Optional[int]:
        """Check the credentials of a request are found in the database.

        Args:
            request: Request object.

        Returns:
            int: User id.
        """
        api_key = await APIKeyHeader(name="token")(request)
        user_id = self.get_user_id(request.app.make("db.session"), api_key)

        if not user_id:
            self.respond_unauthorized()

        self.user_id = user_id
        return user_id


async def make_authenticator(config: Dict) -> Authenticator:
    """Establish the authenticator.

    Args:
        config: config settings for the authenticator.

    Returns:
        Authenticator: The created Authenticator instance.

    Raises:
        ValueError: If the authenticator driver is not recognised.
        KeyError: If a setting is not available in `config`.
    """
    if config["driver"] == "httpbasic":
        return HttpBasic()
    if config["driver"] == "apikey":
        return ApiKey()

    raise ValueError(f"Unsupported authenticator {config['driver']}.")


async def authorise(request: Request) -> Optional[int]:
    """Authorises a request by calling the authorise method.

    Args:
        request: Request object to authorise.

    Returns:
        int: User id for the given credentials.
    """
    authenticator = await request.app.make("auth")
    return await authenticator.authorise(request)
