"""站点配置更新必须是「局部更新」。

后台各个设置页签（基础设置 / 消息推送 / 文章审核通知 / 社交登录 / 外观）保存时，
只发送自己的字段（见前端 SettingsView.vue、AppearanceView.vue）。如果更新函数把整份
Schema 展开后写库，没发送的字段会被 Schema 默认值覆盖——线上出过的问题：
关掉文章审核后再保存基础设置，文章审核被重置为「开启」。

用 sqlite 内存库只建 wb_config 一张表（Base.metadata 里有同名的 idx_type 索引，
在 SQLite 的库级唯一约束下会冲突）。
"""
import json

import pytest
from sqlalchemy import MetaData, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.models.data.siteconfig as models
from app.crud import siteconfig as crud
from app.models.schemas.siteconfig import SiteConfig

# 各页签实际发送的字段，取值都是「非默认值」
TAB_PAYLOADS = {
    '基础设置': {
        'site_title': '测试站', 'site_logo': None, 'site_favicon': None,
        'disable_comment': 1, 'doc_comment': 0,
        'sensitive_words_enabled': 1, 'watermark_enabled': 1, 'watermark_mode': 'tile',
    },
    '消息推送': {'message_push_method': 'polling', 'polling_interval': 10},
    '文章审核通知': {
        'article_review_enabled': 0,
        'enable_article_review_notification': 1,
        'article_review_notification_roles': '["Admin"]',
    },
    '社交登录': {'oauth_enabled': 1, 'enabled_oauth_providers': ['github']},
    '外观-通用': {
        'language': 'en-US', 'dark_mode': 'dark', 'default_homepage': 'doc',
        'default_docbook_id': 3, 'doc_subdomain': 'docs.example.com',
        'enable_register': 0, 'register_role': 'Author',
    },
    '外观-底部': {'footer_config': {'links': [{'label': 'about'}]}},
}
FOOTER = TAB_PAYLOADS['外观-底部']['footer_config']
SEED = {k: v for payload in TAB_PAYLOADS.values() for k, v in payload.items() if k != 'footer_config'}

# 逐字段断言用的「完整状态」
EXPECTED = {**SEED, 'footer_config': json.dumps(FOOTER, ensure_ascii=False)}


@pytest.fixture()
async def db():
    meta = MetaData()
    models.SiteConfig.__table__.to_metadata(meta)
    engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)
    session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)()
    yield session
    await session.close()
    await engine.dispose()


async def seed_config(db: AsyncSession) -> models.SiteConfig:
    db.add(models.SiteConfig(id=1, **SEED, _footer_config=EXPECTED['footer_config']))
    await db.commit()
    return (await db.execute(select(models.SiteConfig))).scalar_one()


async def load_config(db: AsyncSession) -> dict:
    """按列名取出原始存储值；页脚列直接读 _footer_config 属性（原始 JSON 字符串）。"""
    row = (await db.execute(select(models.SiteConfig))).scalar_one()
    stored = {c.name: getattr(row, c.name) for c in row.__table__.columns if c.name != 'footer_config'}
    stored['footer_config'] = row._footer_config
    return stored


@pytest.mark.parametrize('tab', list(TAB_PAYLOADS))
async def test_saving_one_tab_keeps_other_tabs(db, tab):
    """保存某个页签后，其余页签的设置必须原样保留。"""
    await seed_config(db)

    await crud.update_site_config(db, SiteConfig(**TAB_PAYLOADS[tab]))

    stored = await load_config(db)
    changed = {k: (EXPECTED[k], stored.get(k)) for k in EXPECTED if stored.get(k) != EXPECTED[k]}
    assert not changed, f'保存「{tab}」改动了别的设置: {changed}'


async def test_explicit_null_clears_the_field(db):
    """显式传 null 表示清空（例如清掉文档子域名），不能被当成「没传」而忽略。"""
    await seed_config(db)

    await crud.update_site_config(db, SiteConfig(doc_subdomain=None))

    stored = await load_config(db)
    assert stored['doc_subdomain'] is None
    assert stored['default_docbook_id'] == 3


async def test_footer_config_roundtrip(db):
    """footer_config 在模型里是 _footer_config 列，存 JSON 字符串；传 null 表示清空。"""
    await seed_config(db)

    new_footer = {'links': [{'label': 'contact'}]}
    result = await crud.update_site_config(db, SiteConfig(footer_config=new_footer))
    assert result.footer_config == new_footer

    await crud.update_site_config(db, SiteConfig(footer_config=None))
    assert (await load_config(db))['footer_config'] is None


async def test_update_endpoint_only_touches_sent_fields(db, monkeypatch):
    """走真实 HTTP 接口：请求体里没带的字段不能被改写（含响应里回显的整份配置）。"""
    from types import SimpleNamespace
    from unittest.mock import AsyncMock

    from httpx import ASGITransport, AsyncClient

    import app.middleware.admin_audit as admin_audit
    from app.database import get_db
    from app.dependencies.authentication import get_current_active_admin_user
    from app.main import app

    await seed_config(db)
    # 审计中间件会用独立会话连真实数据库，测试里替掉，避免产生副作用
    monkeypatch.setattr(admin_audit, '_record', AsyncMock(return_value=None))

    async def override_get_db():
        yield db

    admin_user = SimpleNamespace(id=1, username='admin', role='Admin', status='active')
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_admin_user] = lambda: admin_user
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            response = await client.post(
                '/api/admin/setting/update', json=TAB_PAYLOADS['消息推送'],
            )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body['code'] == 1
        # 响应回显整份配置：没发送的字段应保持原值
        data = body['data']
        assert data['article_review_enabled'] == 0
        assert data['watermark_enabled'] == 1
        assert data['language'] == 'en-US'
        assert data['enable_register'] == 0
    finally:
        app.dependency_overrides.clear()
    stored = await load_config(db)
    assert {key: stored[key] for key in EXPECTED} == EXPECTED
