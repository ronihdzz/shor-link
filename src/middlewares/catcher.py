from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm.exc import NoResultFound
from starlette.middleware.base import BaseHTTPMiddleware
from responses import create_response_for_fast_api,ErrorCodes

class CatcherExceptionsMiddleware(BaseHTTPMiddleware):
    def _init_(self, app):
        super()._init_(app)

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:  # noqa: BLE001
            internal_error = ErrorCodes.UNKNOW
            error_message = None
            error_data = None
            status_code_http = status.HTTP_500_INTERNAL_SERVER_ERROR
            if isinstance(e, HTTPException):
                error_data = {"detail": str(e.detail)}
                status_code_http = e.status_code
            if isinstance(e, NoResultFound):
                error_data = {"detail": f"No found: {e}"}
                status_code_http = status.HTTP_404_NOT_FOUND
            else:
                error_data = {"detail": str(e)}
                status_code_http = status.HTTP_500_INTERNAL_SERVER_ERROR

            return create_response_for_fast_api(
                status_code_http=status_code_http,
                data=error_data,
                error_code=internal_error,
                message=error_message
            )