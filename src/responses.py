from typing import Any, Dict, Optional
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import fastapi
import json 
from enum import Enum
from uuid import uuid4

class ErrorCodes(Enum):
    UNKNOW = 100, "Unknown Error"
    PYDANTIC_VALIDATIONS_REQUEST = 8001, "Failed pydantic validations on request"


    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj._description = description
        return obj

    @property
    def description(self):
        return self._description

class EnvelopeResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any] | None = None
    trace_id: str | None = None

class ErrorDetailResponse(BaseModel):
    internal_error: Dict[str, Any]
    details: Dict[str, Any]

    @staticmethod
    def from_error_code(error_code: ErrorCodes, details: Optional[Dict[str, Any]] = None) -> 'ErrorDetailResponse':
        return ErrorDetailResponse(
            internal_error={
                "code": error_code.value,
                "description": error_code.description,
            },
            details=details or {}
        ).model_dump()

def create_response_for_fast_api(
    status_code_http: int = fastapi.status.HTTP_200_OK,
    data: Any = None,
    error_code: Optional[ErrorCodes] = ErrorCodes.UNKNOW,
    message: Optional[str] = None
) -> JSONResponse:
    success = 200 <= status_code_http < 300
    message = message or ("Operation successful" if success else "An error occurred")

    if isinstance(data, BaseModel):
        data = data.model_dump_json()
        data = json.loads(data)

    if not success:
        data = ErrorDetailResponse.from_error_code(error_code=error_code, details=data)

    envelope_response = EnvelopeResponse(
        success=success,
        message=message,
        data=data,
        trace_id=str(uuid4())
    )
    
    return JSONResponse(
        content=envelope_response.model_dump(),
        status_code=status_code_http
    )