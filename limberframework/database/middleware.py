"""Middleware

Classes:
- DatabaseSessionMiddleware: creates a database session for a request.
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

class DatabaseSessionMiddleware(BaseHTTPMiddleware):
    """Creates a database session when a request is received
    and stores it in state for accessibility.
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        response = Response("Internal server error", status_code=500)

        try:
            request.state.db = request.app['db.session']
            response = await call_next(request)
            request.state.db.commit()
        finally:
            request.state.db.close()
        return response
