from pydantic import BaseModel
from datetime import datetime
from pydantic.config import ConfigDict
from typing import Optional, List, Literal
import time


class BlogCategoryBase(BaseModel):
    name: str
    cat_desc: str | None = None
    slug: str
    image: str | None = None
    articles_order: Literal['id desc', 'views desc', 'pubtime asc'] = 'id desc'
    model_config = ConfigDict(from_attributes=True)


class BlogCategoryCreate(BlogCategoryBase):
    pid: int = 0
    createtime: int = int(time.time())


class BlogCategoryUpdate(BlogCategoryBase):
    pid: int
    updatetime: int = int(time.time())


class BlogCategoryUpdateSort(BaseModel):
    pid: int
    sort: int


class BlogCategoryUpdateArticlesOrder(BaseModel):
    articles_order: Literal['id desc', 'views desc', 'pubtime asc'] = 'id desc'
    updatetime: int = int(time.time())


class BlogCategory(BlogCategoryBase):
    id: int
    pid: int
    sort: int

    class Config:
        orm_mode = True
