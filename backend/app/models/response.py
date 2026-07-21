from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    code: int = 1
    msg: str = 'ok'
    time: int
    data: Optional[T] = None

    class Config:
        from_attributes = True
