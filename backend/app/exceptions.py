from typing import Union
from fastapi import Request, status
from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.constants import REF_PREFIX
from fastapi.openapi.utils import validation_error_response_definition
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from sqlalchemy.exc import SQLAlchemyError
import time
import traceback
import os
import logging

logger = logging.getLogger(__name__)

# 生产环境不返回堆栈跟踪
DEBUG_MODE = os.getenv('DEBUG', 'false').lower() == 'true'


async def http_exception_handler(request: Request, exc):
    """处理HTTP异常"""
    return JSONResponse(
        {
            "code": 0,
            "msg": str(exc.detail),
            "time": int(time.time()),
            "data": {
                "path": request.url.path,
                "method": request.method,
                "detail": exc.detail
            }
        },
        status_code=exc.status_code
    )


# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     """处理请求验证错误"""
#     return JSONResponse(
#         {
#             "code": 0,
#             "msg": "请求参数验证失败",
#             "time": int(time.time()),
#             "data": {
#                 "path": request.url.path,
#                 "errors": exc.errors()
#             }
#         },
#         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
#     )


async def validation_exception_handler(
        _: Request,
        exc: Union[RequestValidationError, ValidationError],
) -> JSONResponse:
    return JSONResponse(
        {
            "code": 0,
            "msg": "请求参数验证失败",
            "time": int(time.time()),
            "data": {
                "path": _.url.path,
                "errors": exc.errors()
            }
        },
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


validation_error_response_definition["properties"] = {
    "errors": {
        "title": "Errors",
        "type": "array",
        "items": {"$ref": "{0}ValidationError".format(REF_PREFIX)},
    },
}


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """处理数据库异常"""
    # 记录详细错误信息到日志
    logger.error(f"Database error at {request.url.path}: {str(exc)}", exc_info=True)

    response_data = {
        "code": 0,
        "msg": "数据库操作失败",
        "time": int(time.time()),
        "data": {
            "path": request.url.path,
            "error": "数据库操作失败"  # 不暴露具体错误信息
        }
    }

    # 仅在调试模式返回堆栈跟踪
    if DEBUG_MODE:
        response_data["data"]["error"] = str(exc)
        response_data["data"]["traceback"] = traceback.format_exc()

    return JSONResponse(response_data, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def general_exception_handler(request: Request, exc: Exception):
    """处理通用异常"""
    # 记录详细错误信息到日志
    logger.error(f"Unexpected error at {request.url.path}: {str(exc)}", exc_info=True)

    response_data = {
        "code": 0,
        "msg": "服务器内部错误",
        "time": int(time.time()),
        "data": {
            "path": request.url.path,
            "error": "服务器内部错误"  # 不暴露具体错误信息
        }
    }

    # 仅在调试模式返回堆栈跟踪
    if DEBUG_MODE:
        response_data["data"]["error"] = str(exc)
        response_data["data"]["traceback"] = traceback.format_exc()

    return JSONResponse(response_data, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
