"""首页列表 exclude_ids 去重测试（真 sqlite 内存库）。

场景：编辑推荐区 7 篇（含置顶主推文）不应再出现在下方文章列表中；
list 与 count 必须同口径，保证 total / hasMore 判断一致；
不传 exclude_ids 时行为不变（向后兼容）。

只建 get_home_article_list 涉及的 4 张表：全局 Base.metadata 里
wb_sensitive_words / wb_blacklist 有同名索引 idx_type（MySQL 表级唯一合法），
SQLite 库级唯一会冲突——这正是 conftest 弃用真库建表的历史原因。
"""
import pytest
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

import app.models.data.articles as articles_models
import app.models.data.users as users_models
import app.models.data.category as category_models
from app.crud import articles as crud_articles
from app.models.schemas.articles import HomeArticleListRequest

_MODELS = [
    users_models.User.__table__,
    articles_models.BlogArticle.__table__,
    articles_models.BlogArticleStatData.__table__,
    category_models.BlogCategory.__table__,
]


@pytest.fixture()
async def db():
    meta = MetaData()
    for table in _MODELS:
        table.to_metadata(meta)
    engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)
    session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)()
    yield session
    await session.close()
    await engine.dispose()


async def seed(session: AsyncSession) -> dict[int, int]:
    """建 1 用户 + 5 篇已发布文章；返回 {角色名: 文章id}。

    hero：置顶主推文（is_pin=1，最老的 createtime 保证置顶排序在前）
    side1/side2：推荐区副列
    other1/other2：仅存在于下方列表
    """
    from app.models.data.users import User
    from app.models.data.articles import BlogArticle

    user = User(username='daojia', email='a@b.c', password='x', role='Author', status='active')
    session.add(user)
    await session.flush()

    def article(title, createtime, is_pin=0):
        return BlogArticle(
            title=title, slug=title, author=user.id, status='published',
            is_pin=is_pin, createtime=createtime, updatetime=createtime,
            content=f'<p>{title} 正文</p>',   # schema BlogArticle.content 非可选
        )

    arts = {
        'hero': article('hero-pinned', 1000, is_pin=1),
        'side1': article('side1', 2000),
        'side2': article('side2', 3000),
        'other1': article('other1', 4000),
        'other2': article('other2', 5000),
    }
    session.add_all(arts.values())
    await session.commit()
    return {k: v.id for k, v in arts.items()}


@pytest.mark.asyncio
async def test_exclude_ids_filters_list_and_count(db):
    ids = await seed(db)

    req = HomeArticleListRequest(type='all', exclude_ids=[ids['hero'], ids['side1'], ids['side2']])
    rows = await crud_articles.get_home_article_list(reqdata=req, db=db, skip=0, limit=10)
    titles = {d['title'] for d in rows}
    assert titles == {'other1', 'other2'}, f'推荐区文章未被排除: {titles}'

    total = await crud_articles.get_home_article_count(db, reqdata=req)
    assert total == 2, f'count 与 list 不同口径: {total}'


@pytest.mark.asyncio
async def test_excluded_pinned_article_gone_from_top(db):
    """核心抱怨场景：置顶主推文被排除后，列表顶部不应再出现它。"""
    ids = await seed(db)
    req = HomeArticleListRequest(type='all', exclude_ids=[ids['hero']])
    rows = await crud_articles.get_home_article_list(reqdata=req, db=db, skip=0, limit=10)
    titles = [d['title'] for d in rows]
    assert 'hero-pinned' not in titles, f'置顶主推文仍在列表: {titles}'


@pytest.mark.asyncio
async def test_no_exclude_ids_backwards_compatible(db):
    """不传 exclude_ids：行为与旧版一致（置顶文排最前）。"""
    await seed(db)
    req = HomeArticleListRequest(type='all')
    rows = await crud_articles.get_home_article_list(reqdata=req, db=db, skip=0, limit=10)
    assert len(rows) == 5
    assert rows[0]['title'] == 'hero-pinned'   # 置顶仍在列表最前（旧行为）
    total = await crud_articles.get_home_article_count(db, reqdata=req)
    assert total == 5


@pytest.mark.asyncio
async def test_empty_exclude_ids_ignored(db):
    """空列表/负值不产生 where 条件（全量返回）。"""
    await seed(db)
    req = HomeArticleListRequest(type='all', exclude_ids=[])
    assert len(await crud_articles.get_home_article_list(reqdata=req, db=db, skip=0, limit=10)) == 5
    req = HomeArticleListRequest(type='all', exclude_ids=[-1, 0])
    assert len(await crud_articles.get_home_article_list(reqdata=req, db=db, skip=0, limit=10)) == 5


@pytest.mark.asyncio
async def test_pagination_offset_works_with_exclude(db):
    """排除后分页仍正确：第 2 页取剩余。"""
    ids = await seed(db)
    req = HomeArticleListRequest(type='all', exclude_ids=[ids['hero'], ids['side1']])
    page1 = await crud_articles.get_home_article_list(reqdata=req, db=db, skip=0, limit=2)
    page2 = await crud_articles.get_home_article_list(reqdata=req, db=db, skip=2, limit=2)
    p1_titles = [d['title'] for d in page1]
    p2_titles = [d['title'] for d in page2]
    assert len(p1_titles) == 2 and len(p2_titles) == 1
    assert not (set(p1_titles) & set(p2_titles)), '分页出现重复'
