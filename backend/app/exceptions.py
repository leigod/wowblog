from typing import Union
from fastapi import Request, status
from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.constants import REF_PREFIX
from fastapi.openapi.utils import validation_error_response_definition
from starlette.requests import Request
from starlette.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
import time
import traceback
import os
import logging

from dotenv import load_dotenv

# 必须 reload .env：本模块可能在 database.py（其内才调用 load_dotenv）之前被导入，
# 否则 DEBUG 环境变量尚未加载，DEBUG_MODE 恒为 False，开发期 500 不返回堆栈
load_dotenv()

logger = logging.getLogger(__name__)

# 422 常量：Starlette 新版改名 UNPROCESSABLE_CONTENT（RFC 9110 术语更新），
# 新版对旧名发 DeprecationWarning、旧版没有新名——兼容取值
try:
    HTTP_422 = status.HTTP_422_UNPROCESSABLE_CONTENT
except AttributeError:
    HTTP_422 = status.HTTP_422_UNPROCESSABLE_ENTITY

# 生产环境不返回堆栈跟踪
DEBUG_MODE = os.getenv('DEBUG', 'false').lower() == 'true'


def _json_safe(value, _depth: int = 0):
    """把校验错误中的非 JSON 对象转成可序列化值。

    Pydantic v2 的 RequestValidationError.errors() 在 ctx 里会放原始异常对象
    （如 JSONDecodeError/ValueError）。直接塞进 JSONResponse 会抛
    TypeError: Object of type ValueError is not JSON serializable，
    导致本应返回 422 的请求变成 500。
    """
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if _depth > 8:
        return str(value)
    if isinstance(value, Exception):
        return f"{type(value).__name__}: {value}"
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')[:2000]
    if isinstance(value, dict):
        return {str(key): _json_safe(item, _depth + 1) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item, _depth + 1) for item in value]
    return str(value)


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
                "detail": _json_safe(exc.detail)
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
#         status_code=HTTP_422
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
                "errors": _json_safe(exc.errors())
            }
        },
        status_code=HTTP_422
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
