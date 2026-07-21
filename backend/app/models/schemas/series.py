from pydantic import BaseModel
from datetime import datetime
from pydantic.config import ConfigDict
from typing import Optional, List, Literal
import time


class BlogSeriesBase(BaseModel):
    name: str
    series_desc: str | None = None
    slug: str
    image: str | None = None
    articles_order: Literal['asc', 'desc'] = 'desc'
    sort: int | None = 0
    model_config = ConfigDict(from_attributes=True)


class BlogSeriesCreate(BlogSeriesBase):
    createtime: int = int(time.time())


class BlogSeriesUpdate(BlogSeriesBase):
    updatetime: int = int(time.time())


class BlogSeries(BlogSeriesBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
