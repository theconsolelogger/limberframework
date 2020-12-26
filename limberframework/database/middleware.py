"""Creates a database session for a request."""
from fastapi import Request, Response
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)


class DatabaseSessionMiddleware(BaseHTTPMiddleware):
    """Create a database session.

    When a request is received a database session is established
    and stores it in state for accessibility.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Handle creating and closing a database session for a request.

        Args:
            request: Client request.
            call_next: The endpoint to call for the request.

        Returns:
            Response: The response to the client request.
        """
        response = Response("Internal server error", status_code=500)

        try:
            request.state.db = await request.app.make("db.session")
            response = await call_next(request)
            request.state.db.commit()
        finally:
            request.state.db.close()
        return response
