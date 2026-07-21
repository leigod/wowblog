from typing import Any
from app.models.response import ApiResponse
import time
from fastapi.responses import JSONResponse


# def success(msg: str = 'ok', data: Any = None) -> JSONResponse:
#     return JSONResponse({
#         "code": 1,
#         "msg": msg,
#         "time": int(time.time()),
#         "data": data
#     })


# 新增错误响应函数
def error(msg: str = 'fail', data: Any = None) -> JSONResponse:
    return JSONResponse(
        {
            "code": 0,
            "msg": msg,
            "time": int(time.time()),
            "data": data or []
        },
        # 根据实际情况设置HTTP状态码
        # status_code=400
    )

def success(msg: str = 'ok', data: Any = None) -> ApiResponse:
    return ApiResponse(
        msg=msg,
        time=int(time.time()),
        data=data
    )


# def error(msg: str = 'fail', data: any = None) -> ApiResponse:
#     return ApiResponse(
#         code=0,
#         msg=msg,
#         time=int(time.time()),
#         data=data or []
#     )
