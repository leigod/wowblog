"""blog 分类 / 系列 slug 生成工具。

约定（与文章 slug 口径一致）：
- 只含 a-z0-9_-，一律小写；
- 中文走 pypinyin 转拼音，空格/逗号归一为下划线/短横线；
- 同用户内唯一，冲突时追加 _ + 4 位随机后缀（分类/系列 slug 列 varchar(50)，留足余量）。

调用方：crud/user_blog.py 的 create/update 路径。
"""
import random
import re
import string

import pypinyin
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.data.user_blog import UserCategory, UserSeries

MAX_SLUG_LEN = 50
_SUFFIX_LEN = 5  # '_' + 4 位
_NAME_RE = re.compile(r"[a-zA-Z0-9_-]")


def normalize_slug(raw: str) -> str:
    """把任意输入名义上的 slug 归一到合法小写形态（不做唯一性处理）。"""
    text = (raw or "").strip().lower()
    text = text.replace(" ", "_").replace(",", "-")
    text = "".join(c for c in text if _NAME_RE.match(c))
    return text[:MAX_SLUG_LEN]


def slug_from_name(name: str) -> str:
    """由名称生成名义 slug：中文拼音化，英文直接归一。"""
    if any("一" <= ch <= "鿿" for ch in name):
        joined = "_".join(pypinyin.lazy_pinyin(name))
    else:
        joined = name
    slug = normalize_slug(joined)
    return slug or "item"


async def ensure_unique_slug(
    db: AsyncSession,
    user_id: int,
    slug: str,
    model,
    exclude_id: int | None = None,
) -> str:
    """保证 slug 在 (user_id, model) 范围内唯一，冲突追加随机后缀。"""
    candidate = normalize_slug(slug) or "item"
    # 主体截断，给后缀留位置
    stem = candidate[: MAX_SLUG_LEN - _SUFFIX_LEN]

    while True:
        stmt = select(model.id).where(
            model.user_id == user_id, model.slug == candidate
        )
        if exclude_id is not None:
            stmt = stmt.where(model.id != exclude_id)
        exists = (await db.execute(stmt)).scalar_one_or_none() is not None
        if not exists:
            return candidate
        suffix = "_" + "".join(random.sample(string.ascii_lowercase + string.digits, 4))
        candidate = stem + suffix


async def resolve_slug(
    db: AsyncSession,
    user_id: int,
    raw_slug: str | None,
    name: str,
    model,
    exclude_id: int | None = None,
) -> str:
    """创建/编辑时的统一入口：有传 slug 用传入值，否则按 name 生成，再保证唯一。"""
    base = normalize_slug(raw_slug) if raw_slug else slug_from_name(name)
    return await ensure_unique_slug(db, user_id, base, model, exclude_id)


__all__ = [
    "normalize_slug",
    "slug_from_name",
    "ensure_unique_slug",
    "resolve_slug",
    "UserCategory",
    "UserSeries",
]
