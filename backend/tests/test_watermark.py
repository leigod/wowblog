"""水印服务单元测试。

覆盖：
- 素材三级回退链（logo → favicon+名称 → 纯文字）与 blog_name 空回退
- 开关优先级（Author 博客级覆盖全站，NULL=跟随全站；非 Author 只看全站）
- 渲染（三种素材 × corner/tile、JPEG/PNG、小图跳过、GIF 跳过、透明 PNG alpha 保留）
- _read_material 素材路径解析与目录穿越防护
"""
import pytest
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from PIL import Image

from app.services import watermark_service as ws


# ---------- 测试工具 ----------

def make_image_bytes(w=1200, h=800, mode='RGB', color=(120, 40, 200)) -> bytes:
    buf = BytesIO()
    Image.new(mode, (w, h), color).save(buf, 'PNG' if 'A' in mode else 'JPEG', quality=90)
    return buf.getvalue()


def make_logo_bytes() -> bytes:
    buf = BytesIO()
    Image.new('RGBA', (200, 50), (0, 120, 255, 255)).save(buf, 'PNG')
    return buf.getvalue()


def fake_db_returning(value):
    """构造 db.execute(...) 返回 scalar_one_or_none()==value 的 AsyncMock。"""
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    db = MagicMock()
    db.execute = AsyncMock(return_value=result)
    return db


def site_config(**kw):
    defaults = dict(site_title='哇饮站', site_logo=None, site_favicon=None,
                    watermark_enabled=1, watermark_mode='corner')
    defaults.update(kw)
    return SimpleNamespace(**defaults)


def blog_config(**kw):
    defaults = dict(blog_name='哇饮到家', logo=None, favicon=None,
                    watermark_enabled=None, watermark_mode=None)
    defaults.update(kw)
    return SimpleNamespace(**defaults)


def user_of(role, username='daojia', uid=7):
    return SimpleNamespace(role=role, username=username, id=uid)


@pytest.fixture(autouse=True)
def clean_cache():
    ws.invalidate_cache()
    yield
    ws.invalidate_cache()


# ---------- 身份判定与三级回退 ----------

@pytest.mark.asyncio
async def test_admin_uses_site_identity(monkeypatch):
    """Admin/Editor/Contributor 上传 → 网站身份，与个人博客配置无关。"""
    db = fake_db_returning(site_config(watermark_enabled=1))
    for role in ('Admin', 'Editor', 'Contributor'):
        ws.invalidate_cache()
        resolved = await ws.resolve_watermark(db, user_of(role))
        assert resolved is not None
        assert resolved.material.kind == 'text'
        assert resolved.material.text == '哇饮站'   # 站名，不带 @账号


@pytest.mark.asyncio
async def test_author_level3_name_at_username(monkeypatch):
    """Author 无 logo 无 favicon → 纯文字「博客名@账号」。"""
    db = fake_db_returning(None)  # 第一个 scalar_one_or_none 给 site
    # site 与 blog 都查同一 mock：site=有效配置，blog=空配置行
    db = MagicMock()
    result_site = MagicMock(); result_site.scalar_one_or_none.return_value = site_config()
    result_blog = MagicMock(); result_blog.scalar_one_or_none.return_value = blog_config()
    db.execute = AsyncMock(side_effect=[result_site, result_blog])

    resolved = await ws.resolve_watermark(db, user_of('Author'))
    assert resolved.material.kind == 'text'
    assert resolved.material.text == '哇饮到家@daojia'


@pytest.mark.asyncio
async def test_author_blog_name_empty_falls_back_to_username():
    """blog_name 为空 → 名称回退用户名，L3 只显示账号避免「daojia@daojia」。"""
    db = MagicMock()
    result_site = MagicMock(); result_site.scalar_one_or_none.return_value = site_config()
    result_blog = MagicMock(); result_blog.scalar_one_or_none.return_value = blog_config(blog_name=None)
    db.execute = AsyncMock(side_effect=[result_site, result_blog])

    resolved = await ws.resolve_watermark(db, user_of('Author'))
    assert resolved.material.text == 'daojia'


@pytest.mark.asyncio
async def test_level1_logo_and_level2_favicon(monkeypatch):
    """有 logo → logo 素材；无 logo 有 favicon → 图标+名称。"""
    logo = make_logo_bytes()
    monkeypatch.setattr(ws, '_read_material', lambda url: logo if url else None)

    db = MagicMock()
    r1 = MagicMock(); r1.scalar_one_or_none.return_value = site_config(site_logo='/static/x/l.png')
    db.execute = AsyncMock(return_value=r1)
    resolved = await ws.resolve_watermark(db, user_of('Admin'))
    assert resolved.material.kind == 'logo'

    ws.invalidate_cache()
    r2 = MagicMock(); r2.scalar_one_or_none.return_value = site_config(site_favicon='/static/x/f.ico')
    db.execute = AsyncMock(return_value=r2)
    resolved = await ws.resolve_watermark(db, user_of('Admin'))
    assert resolved.material.kind == 'icon_text'
    assert resolved.material.text == '哇饮站'


@pytest.mark.asyncio
async def test_site_disabled_returns_none():
    db = fake_db_returning(site_config(watermark_enabled=0))
    assert await ws.resolve_watermark(db, user_of('Admin')) is None


@pytest.mark.asyncio
async def test_author_override_and_follow():
    """博客级设置优先级：NULL=跟随全站；0=显式关闭（即使全站开）；1=显式开启（即使全站关）。"""
    def db_with(site_kw, blog_kw):
        db = MagicMock()
        rs = MagicMock(); rs.scalar_one_or_none.return_value = site_config(**site_kw)
        rb = MagicMock(); rb.scalar_one_or_none.return_value = blog_config(**blog_kw)
        db.execute = AsyncMock(side_effect=[rs, rb])
        return db

    # 全站开 + 博客 NULL → 跟随开启
    assert await ws.resolve_watermark(db_with(dict(watermark_enabled=1), dict()), user_of('Author')) is not None
    # 全站开 + 博客 0 → 关闭
    ws.invalidate_cache()
    assert await ws.resolve_watermark(db_with(dict(watermark_enabled=1), dict(watermark_enabled=0)), user_of('Author')) is None
    # 全站关 + 博客 1 → 开启（覆盖）
    ws.invalidate_cache()
    assert await ws.resolve_watermark(db_with(dict(watermark_enabled=0), dict(watermark_enabled=1)), user_of('Author')) is not None
    # 全站关 + 博客 NULL → 跟随关闭
    ws.invalidate_cache()
    assert await ws.resolve_watermark(db_with(dict(watermark_enabled=0), dict()), user_of('Author')) is None


@pytest.mark.asyncio
async def test_mode_override_and_fallback():
    """mode：博客级非法值/NULL 回退全站；全站非法值回退 corner。"""
    db = MagicMock()
    rs = MagicMock(); rs.scalar_one_or_none.return_value = site_config(watermark_mode='tile')
    rb = MagicMock(); rb.scalar_one_or_none.return_value = blog_config(watermark_mode=None)
    db.execute = AsyncMock(side_effect=[rs, rb])
    resolved = await ws.resolve_watermark(db, user_of('Author'))
    assert resolved.mode == 'tile'

    ws.invalidate_cache()
    rs2 = MagicMock(); rs2.scalar_one_or_none.return_value = site_config(watermark_mode='diagonal')
    rb2 = MagicMock(); rb2.scalar_one_or_none.return_value = blog_config(watermark_mode='corner')
    db.execute = AsyncMock(side_effect=[rs2, rb2])
    resolved = await ws.resolve_watermark(db, user_of('Author'))
    assert resolved.mode == 'corner'


def test_material_cache_hit(monkeypatch):
    """同身份重复解析命中缓存：不再查库（side_effect 列表只够一次）。"""
    import asyncio

    db = MagicMock()
    rs = MagicMock(); rs.scalar_one_or_none.return_value = site_config()
    db.execute = AsyncMock(side_effect=[rs])  # 只允许一次查询

    async def run():
        await ws.resolve_watermark(db, user_of('Admin'))
        return await ws.resolve_watermark(db, user_of('Admin'))

    resolved = asyncio.run(run())
    assert resolved is not None


# ---------- 渲染 ----------

def test_render_all_kinds_and_modes():
    logo = make_logo_bytes()
    mats = [
        ws.WatermarkMaterial('logo', image_bytes=logo),
        ws.WatermarkMaterial('icon_text', image_bytes=logo, text='哇饮到家'),
        ws.WatermarkMaterial('text', text='哇饮到家@daojia'),
    ]
    for mat in mats:
        for mode in ('corner', 'tile'):
            out = ws.apply_watermark(make_image_bytes(), '.png',
                                     ws.ResolvedWatermark(True, mode, mat))
            assert out, f'{mat.kind}/{mode} 未生成'
            img = Image.open(BytesIO(out))
            assert img.size == (1200, 800)
            assert img.mode == 'RGBA'


def test_jpeg_roundtrip_mode_rgb():
    out = ws.apply_watermark(make_image_bytes(mode='RGB'), '.jpg',
                             ws.ResolvedWatermark(True, 'corner', ws.WatermarkMaterial('text', text='测试')))
    img = Image.open(BytesIO(out))
    assert img.format == 'JPEG' and img.mode == 'RGB'


def test_small_image_skipped():
    out = ws.apply_watermark(make_image_bytes(200, 100), '.png',
                             ws.ResolvedWatermark(True, 'corner', ws.WatermarkMaterial('text', text='x')))
    assert out is None


def test_gif_and_unknown_ext_skipped():
    r = ws.ResolvedWatermark(True, 'corner', ws.WatermarkMaterial('text', text='x'))
    assert ws.apply_watermark(b'GIF89a', '.gif', r) is None
    assert ws.apply_watermark(b'%PDF-1.4', '.pdf', r) is None


def test_transparent_png_alpha_preserved():
    out = ws.apply_watermark(make_image_bytes(900, 700, mode='RGBA'), '.png',
                             ws.ResolvedWatermark(True, 'corner', ws.WatermarkMaterial('text', text='透明')))
    img = Image.open(BytesIO(out))
    # 左上角远离水印区，背景 alpha 应保持原值 255（不透明红底）
    assert img.getpixel((5, 5))[3] == 255


def test_watermark_actually_drawn():
    """corner 模式右下角区域应发生像素变化。"""
    src = make_image_bytes(1200, 800)
    out = ws.apply_watermark(src, '.png',
                             ws.ResolvedWatermark(True, 'corner', ws.WatermarkMaterial('text', text='哇饮到家@daojia')))
    a, b = Image.open(BytesIO(src)).convert('RGB'), Image.open(BytesIO(out)).convert('RGB')
    changed = sum(1 for x in range(900, 1180, 10) for y in range(650, 790, 10)
                  if a.getpixel((x, y)) != b.getpixel((x, y)))
    assert changed > 0, '右下角无任何水印像素'


# ---------- 可见性（回归：水印必须真的看得见） ----------
# 这组断言来自一次线上返工：旧参数（字号按短边取 3% 且上限 32px、白字透明度 0.55、
# 描边 0.39、平铺透明度 0.18，外加合成时透明度被平方）在真实照片封面上几乎不可见，
# 结果是「开关开了，但用户看不到水印」。

def _flat_png(w, h, color) -> bytes:
    buf = BytesIO()
    Image.new('RGB', (w, h), color).save(buf, 'PNG')
    return buf.getvalue()


def _corner_text_png(w, h, color) -> bytes:
    out = ws.apply_watermark(_flat_png(w, h, color), '.png',
                             ws.ResolvedWatermark(True, 'corner', ws.WatermarkMaterial('text', text='哇饮到家@daojia')))
    assert out is not None
    return out


def _ratio_in_corner(out: bytes, w, h, lo, hi) -> float:
    """右下角 420x120 区域内亮度落在 [lo, hi) 的像素占比。"""
    region = Image.open(BytesIO(out)).convert('L').crop((w - 420, h - 120, w, h))
    hist = region.histogram()
    return sum(hist[lo:hi]) / (region.width * region.height)


@pytest.mark.parametrize('color, lo, hi, what', [
    ((245, 243, 238), 0, 128, '深色像素'),     # 浅色底：靠描边和投影显形
    ((20, 22, 28), 200, 256, '亮色像素'),      # 深色底：靠白色字身显形
])
def test_corner_text_has_contrast_on_flat_background(color, lo, hi, what):
    """纯色底上的文字水印必须带出足够的对比（旧参数白字 0.55 压白底等于没画）。"""
    ratio = _ratio_in_corner(_corner_text_png(1376, 768, color), 1376, 768, lo, hi)
    assert ratio > 0.02, f'右下角{what}占比仅 {ratio:.1%}，水印在这种底色上不可见'


@pytest.mark.parametrize('width, height, min_height', [(1376, 768, 34), (2560, 1440, 52)])
def test_corner_text_scales_with_image_width(width, height, min_height):
    """字号按图宽取比例且不被 32px 上限压制——封面缩到 760px 显示时仍要读得出来。"""
    from PIL import ImageChops
    src = _flat_png(width, height, (90, 140, 200))
    a = Image.open(BytesIO(src)).convert('L')
    b = Image.open(BytesIO(_corner_text_png(width, height, (90, 140, 200)))).convert('L')
    left, top, right, bottom = ImageChops.difference(a, b).point(lambda v: 255 if v > 8 else 0).getbbox()
    assert bottom - top >= min_height, f'水印字高仅 {bottom - top}px'
    # 贴右下角，留边约为图宽的 2.5%
    assert 0 < width - right < width * 0.06
    assert 0 < height - bottom < width * 0.06


def test_tile_is_perceptible():
    """平铺模式必须在画面上留下可感知的痕迹（旧透明度 0.18 等于隐形）。"""
    from PIL import ImageChops
    src = _flat_png(1200, 800, (128, 128, 128))
    out = ws.apply_watermark(src, '.png', ws.ResolvedWatermark(True, 'tile', ws.WatermarkMaterial('text', text='哇饮到家@daojia')))
    a = Image.open(BytesIO(src)).convert('L')
    b = Image.open(BytesIO(out)).convert('L')
    hist = ImageChops.difference(a, b).histogram()
    strong = sum(hist[41:]) / (1200 * 800)
    assert 0.01 < strong < 0.2, f'平铺强变化像素占比 {strong:.1%}'


# ---------- 素材路径安全 ----------

def test_read_material_rejects_traversal(tmp_path, monkeypatch):
    monkeypatch.setattr(ws, '_UPLOADS_DIR', tmp_path)
    assert ws._read_material(None) is None
    assert ws._read_material('/static/../../etc/passwd') is None
    assert ws._read_material('/static/not-exists.png') is None


def test_read_material_maps_static_url(tmp_path, monkeypatch):
    target = tmp_path / '20260101' / 'logo.png'
    target.parent.mkdir(parents=True)
    target.write_bytes(make_logo_bytes())
    monkeypatch.setattr(ws, '_UPLOADS_DIR', tmp_path)

    assert ws._read_material('/static/20260101/logo.png') is not None
    # 完整 URL（Creator 工作台存 full_url）同样可读
    assert ws._read_material('http://example.com/static/20260101/logo.png') is not None


# ---------- /upload/ 接口端到端 ----------

@pytest.mark.asyncio
async def test_upload_endpoint_watermarks_content_image():
    """Author 上传正文图（purpose=content 默认）→ 落盘文件与原图不同（已加水印）。"""
    from datetime import datetime
    from pathlib import Path as P
    from unittest.mock import AsyncMock as AMock
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    from app.database import get_db
    from app.dependencies.authentication import get_current_user

    # db：site 配置 + Author 博客配置
    db = MagicMock()
    rs = MagicMock(); rs.scalar_one_or_none.return_value = site_config(watermark_enabled=1)
    rb = MagicMock(); rb.scalar_one_or_none.return_value = blog_config()
    db.execute = AMock(side_effect=[rs, rb])

    author = user_of('Author')

    async def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: author
    saved = None
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            src = make_image_bytes(1000, 700, mode='RGBA')  # 真 PNG 字节
            resp = await ac.post('/api/upload/', files={
                'file': ('photo.png', BytesIO(src), 'image/png')
            })
            assert resp.status_code == 200, resp.text
            body = resp.json()
            assert body['code'] == 1, body
            uploads_root = P(__file__).resolve().parent.parent / 'app' / 'uploads'
            saved = uploads_root / datetime.now().strftime('%Y%m%d') / body['data']['filename']
            assert saved.is_file(), f'未落盘: {saved}'
            assert saved.read_bytes() != src, '落盘文件与原图一致，水印未生效'
    finally:
        if saved and saved.is_file():
            saved.unlink(missing_ok=True)
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_endpoint_material_skipped():
    """purpose=material（logo/favicon 素材）→ 跳过水印，落盘字节与原图一致。"""
    from datetime import datetime
    from pathlib import Path as P
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    from app.database import get_db
    from app.dependencies.authentication import get_current_user

    db = fake_db_returning(site_config(watermark_enabled=1))
    admin = user_of('Admin')

    async def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: admin
    saved = None
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            src = make_image_bytes(1000, 700, mode='RGBA')  # 真 PNG 字节
            resp = await ac.post('/api/upload/', files={
                'file': ('logo.png', BytesIO(src), 'image/png')
            }, data={'purpose': 'material'})
            assert resp.status_code == 200, resp.text
            body = resp.json()
            assert body['code'] == 1, body
            uploads_root = P(__file__).resolve().parent.parent / 'app' / 'uploads'
            saved = uploads_root / datetime.now().strftime('%Y%m%d') / body['data']['filename']
            assert saved.is_file()
            assert saved.read_bytes() == src, '素材被误加水印'
    finally:
        if saved and saved.is_file():
            saved.unlink(missing_ok=True)
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_endpoint_full_pipeline_webp():
    """content 上传全管线：返回 .webp 文件名、RIFF 文件头、且带水印（与纯 optimize 结果不同）。"""
    from datetime import datetime
    from pathlib import Path as P
    from unittest.mock import AsyncMock as AMock
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    from app.database import get_db
    from app.dependencies.authentication import get_current_user
    from app.services.image_optimize import optimize_image

    db = MagicMock()
    rs = MagicMock(); rs.scalar_one_or_none.return_value = site_config(watermark_enabled=1)
    rb = MagicMock(); rb.scalar_one_or_none.return_value = blog_config()
    db.execute = AMock(side_effect=[rs, rb])

    author = user_of('Author')

    async def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: author
    saved = None
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            src = make_image_bytes(1000, 700)
            resp = await ac.post('/api/upload/', files={
                'file': ('photo.jpg', BytesIO(src), 'image/jpeg')
            })
            assert resp.status_code == 200, resp.text
            body = resp.json()
            assert body['code'] == 1, body
            assert body['data']['filename'].endswith('.webp'), '应转为 webp'

            uploads_root = P(__file__).resolve().parent.parent / 'app' / 'uploads'
            saved = uploads_root / datetime.now().strftime('%Y%m%d') / body['data']['filename']
            raw = saved.read_bytes()
            assert raw[:4] == b'RIFF' and raw[8:12] == b'WEBP', '文件头非 webp'

            # 与"仅压缩"结果不同 → 水印确实叠加在压缩之后
            optimized_only, _ = optimize_image(src, '.jpg')
            assert raw != optimized_only, '水印未生效'
    finally:
        if saved and saved.is_file():
            saved.unlink(missing_ok=True)
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_endpoint_cover_optimized_without_watermark():
    """purpose=cover（封面/OG）→ 压缩转 webp 但不加水印（与 optimize 结果一致）。"""
    from datetime import datetime
    from pathlib import Path as P
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    from app.database import get_db
    from app.dependencies.authentication import get_current_user
    from app.services.image_optimize import optimize_image

    db = fake_db_returning(site_config(watermark_enabled=1))
    admin = user_of('Admin')

    async def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: admin
    saved = None
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            src = make_image_bytes(1000, 700)
            resp = await ac.post('/api/upload/', files={
                'file': ('cover.jpg', BytesIO(src), 'image/jpeg')
            }, data={'purpose': 'cover'})
            assert resp.status_code == 200, resp.text
            body = resp.json()
            assert body['code'] == 1, body
            assert body['data']['filename'].endswith('.webp')

            uploads_root = P(__file__).resolve().parent.parent / 'app' / 'uploads'
            saved = uploads_root / datetime.now().strftime('%Y%m%d') / body['data']['filename']
            raw = saved.read_bytes()
            optimized_only, _ = optimize_image(src, '.jpg')
            assert raw == optimized_only, 'cover 不应加水印，应与纯压缩结果一致'
    finally:
        if saved and saved.is_file():
            saved.unlink(missing_ok=True)
        app.dependency_overrides.clear()
