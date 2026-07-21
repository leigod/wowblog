from pydantic import BaseModel
from datetime import datetime
from pydantic.config import ConfigDict
from typing import Optional, List, Literal
import time


class BlogPageBase(BaseModel):
    type: Literal['system', 'custom'] = 'custom'
    title: str
    content: str
    slug: str
    image: str | None = None
    seo_desc: str | None = None
    status: Literal['normal', 'hidden'] = 'normal'
    model_config = ConfigDict(from_attributes=True)


class BlogPageCreate(BlogPageBase):
    createtime: int = int(time.time())


class BlogPageUpdate(BlogPageBase):
    updatetime: int = int(time.time())


class BlogPageUpdateStatus(BaseModel):
    status: str


class BlogPage(BlogPageBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
