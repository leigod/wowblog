from pydantic import BaseModel
from datetime import datetime
from pydantic.config import ConfigDict
from typing import Optional, List, Literal
import time


class BlogTagBase(BaseModel):
    type: Literal['sys', 'user'] = 'user'
    name: str
    slug: str
    image: str | None = None
    tag_desc: str | None = None
    status: Literal['normal', 'hidden'] = 'normal'
    model_config = ConfigDict(from_attributes=True)


class BlogTagCreate(BaseModel):
    name: str
    type: Literal['sys', 'user'] = 'user'
    slug: str
    image: str | None = None
    tag_desc: str | None = None
    status: Literal['normal', 'hidden'] = 'normal'


class BlogTagUpdate(BlogTagCreate):
    pass


class BlogTagUpdateStatus(BaseModel):
    status: str


class BlogTag(BlogTagBase):
    id: int
    counts: int | None = 0
    views: int | None = 0
    follows: int | None = 0

    model_config = ConfigDict(from_attributes=True)


class BlogTagPageInfo(BaseModel):
    tag: BlogTag
    total_articles: int | None = 0
    total_followers: int | None = 0

    model_config = ConfigDict(from_attributes=True)
