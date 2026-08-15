from pydantic import BaseModel
from datetime import datetime
from pydantic.config import ConfigDict
from typing import Optional, List, Literal


class BlogNavBase(BaseModel):
    label: str
    nav_type: Literal['sys', 'user']
    type: Literal['link', 'page', 'series', 'doc']
    value: str
    sort: int
    status: int
    model_config = ConfigDict(from_attributes=True)


class BlogNavCreate(BlogNavBase):
    pass


class BlogNavUpdate(BaseModel):
    label: str
    type: Literal['link', 'page', 'series', 'doc']
    value: str


class BlogNavUpdateSort(BaseModel):
    sort: int


class BlogNavUpdateStatus(BaseModel):
    status: Literal[0, 1] = 1


class BlogNav(BlogNavBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
