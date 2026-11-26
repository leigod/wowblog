"""图片水印服务。

职责：
1. resolve_watermark：按上传者角色决定水印身份（Admin/Editor/Contributor → 网站，
   Author → 个人博客），并按三级素材回退链解析素材：
     L1 logo 图片 → L2 favicon + 名称 → L3 纯文字（Author 形如 "哇饮到家@daojia"，网站只显示站名）。
2. apply_watermark：用 Pillow 把水印合成到图片字节上（同步 CPU 函数，
   调用方需经 anyio.to_thread 运行，避免阻塞事件循环）。

开关优先级：Author 上传时 wb_user_blogs.watermark_enabled（NULL=跟随全站）覆盖
wb_config.watermark_enabled；Admin/Editor/Contributor 只看全站开关。

失败策略 fail-open：本模块抛出的任何异常由调用方捕获后按原图落盘，
水印是版权增强功能，不应阻断上传。

素材解析结果带 TTL 进程内缓存（默认 300s），素材变更最迟一个 TTL 生效；
多 worker 部署下各进程独立缓存，可接受。
"""
import time
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.logger import upload_logger

# ---------- 可调常量（渲染规格） ----------
WATERMARK_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
MIN_IMAGE_EDGE = 240           # 宽或高低于此值跳过（小图保护）
LOGO_WIDTH_RATIO = 0.18        # logo 宽 = 目标图宽 × 18%
LOGO_MAX_WIDTH = 240
LOGO_OPACITY = 0.65
TEXT_OPACITY = 0.55
TILE_OPACITY = 0.18            # 平铺模式透明度（防裁剪，弱化存在感）
TILE_BASE_RATIO = 0.35         # 平铺单个水印基准 = 目标图短边 × 35%
TILE_FONT_RATIO = 0.16         # 平铺字号 = 基准 × 16%
TILE_FONT_MIN, TILE_FONT_MAX = 16, 48
TILE_ICON_RATIO = 0.14         # 平铺图标高 = 基准 × 14%
ICON_HEIGHT_RATIO = 0.03       # favicon 高 = 目标图短边 × 3%
ICON_HEIGHT_MIN, ICON_HEIGHT_MAX = 16, 32
TEXT_SIZE_RATIO = 0.03         # 文字字号 = 目标图短边 × 3%
TEXT_SIZE_MIN, TEXT_SIZE_MAX = 14, 32
MARGIN_RATIO = 0.02            # 右下角边距 = 短边 × 2%
MARGIN_MIN = 16
TILE_SPACING_RATIO = 0.4       # 平铺间隔 = 单个水印尺寸 × 0.4
MATERIAL_CACHE_TTL = 300

_BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent  # app/services → app → backend
_FONT_PATH = _BACKEND_ROOT / 'assets' / 'fonts' / 'NotoSansSC-Regular.otf'
_UPLOADS_DIR = _BACKEND_ROOT / 'app' / 'uploads'

_font_object = None  # 惰性加载的 truetype 对象基字号（实际按尺寸逐次加载）


@dataclass
class WatermarkMaterial:
    """三级回退链解析出的素材（进程内缓存的最小单元）。"""
    kind: str                  # 'logo' | 'icon_text' | 'text'
    image_bytes: Optional[bytes] = None  # logo / favicon 原始字节
    text: Optional[str] = None  # L2 为名称；L3 Author 为 "名称@账号"、网站为站名


@dataclass
class ResolvedWatermark:
    """一次身份解析的最终决策。"""
    enabled: bool
    mode: str                       # 'corner' | 'tile'
    material: Optional[WatermarkMaterial] = None


# ---------- 身份解析（含 TTL 缓存） ----------

_material_cache: dict[tuple, tuple[float, ResolvedWatermark]] = {}


def invalidate_cache() -> None:
    """清空素材缓存（设置更新接口可主动调用，加速生效）。"""
    _material_cache.clear()


async def resolve_watermark(db: AsyncSession, user) -> Optional[ResolvedWatermark]:
    """按当前用户角色解析水印配置与素材。

    返回 None 表示完全不需要水印（开关关闭）。
    """
    from app.models.data.siteconfig import SiteConfig
    from app.models.data.user_blog import UserBlogConfig
    from app.utils.roles import UserRole

    role = getattr(user, 'role', None)
    username = getattr(user, 'username', '') or ''
    is_author = role == UserRole.AUTHOR.value

    cache_key = ('blog', user.id) if is_author else ('site',)
    cached = _material_cache.get(cache_key)
    now = time.monotonic()
    if cached and cached[0] > now:
        return cached[1] if cached[1].enabled else None

    site = (await db.execute(select(SiteConfig))).scalar_one_or_none()
    site_enabled = bool(site and site.watermark_enabled)
    site_mode = (site.watermark_mode if site and site.watermark_mode in ('corner', 'tile') else 'corner')
    site_title = (site.site_title if site and site.site_title else 'My Blog')

    if not is_author:
        # Admin / Editor / Contributor → 网站身份
        resolved = _build_site_resolution(site_enabled, site_mode, site_title, site)
        _material_cache[cache_key] = (now + MATERIAL_CACHE_TTL, resolved)
        return resolved if resolved.enabled else None

    # Author → 博客身份，博客级设置覆盖全站（NULL=跟随全站）
    blog = (await db.execute(
        select(UserBlogConfig).where(UserBlogConfig.user_id == user.id)
    )).scalar_one_or_none()

    if blog is None:
        enabled, mode = site_enabled, site_mode
        display_name = username
        logo_url = favicon_url = None
    else:
        enabled = site_enabled if blog.watermark_enabled is None else bool(blog.watermark_enabled)
        mode = (blog.watermark_mode if blog.watermark_mode in ('corner', 'tile')
                else site_mode)
        display_name = blog.blog_name or username   # blog_name 空 → 回退用户名
        logo_url, favicon_url = blog.logo, blog.favicon

    material = _resolve_blog_material(logo_url, favicon_url, display_name, username)
    resolved = ResolvedWatermark(enabled=enabled, mode=mode, material=material)
    _material_cache[cache_key] = (now + MATERIAL_CACHE_TTL, resolved)
    return resolved if resolved.enabled else None


def _build_site_resolution(enabled: bool, mode: str, site_title: str, site) -> ResolvedWatermark:
    """网站身份素材：site_logo → site_favicon+站名 → 站名（机构署名不带 @账号）。"""
    logo_url = getattr(site, 'site_logo', None) if site else None
    favicon_url = getattr(site, 'site_favicon', None) if site else None

    logo_bytes = _read_material(logo_url)
    if logo_bytes:
        return ResolvedWatermark(enabled, mode, WatermarkMaterial('logo', image_bytes=logo_bytes))

    favicon_bytes = _read_material(favicon_url)
    if favicon_bytes:
        return ResolvedWatermark(enabled, mode,
                                 WatermarkMaterial('icon_text', image_bytes=favicon_bytes, text=site_title))

    return ResolvedWatermark(enabled, mode, WatermarkMaterial('text', text=site_title))


def _resolve_blog_material(logo_url, favicon_url, display_name: str, username: str) -> WatermarkMaterial:
    """博客身份素材：logo → favicon+名称 → "名称@账号"（名称空时只显示账号，避免重复）。"""
    logo_bytes = _read_material(logo_url)
    if logo_bytes:
        return WatermarkMaterial('logo', image_bytes=logo_bytes)

    favicon_bytes = _read_material(favicon_url)
    if favicon_bytes:
        return WatermarkMaterial('icon_text', image_bytes=favicon_bytes, text=display_name)

    text = f'{display_name}@{username}' if display_name != username else username
    return WatermarkMaterial('text', text=text)


def _read_material(static_url: Optional[str]) -> Optional[bytes]:
    """把 /static/YYYYMMDD/xxx 形式的素材 URL 映射到本地 uploads 目录读取。

    读取失败（路径异常 / 文件缺失 / 损坏）返回 None，由调用方降级到下一级素材。
    """
    if not static_url:
        return None
    try:
        path_part = static_url.split('://', 1)[-1]        # 去掉协议
        path_part = '/' + path_part.split('/', 1)[-1]      # 去掉域名，保留 /static/...
        if '/static/' in path_part:
            rel = path_part.split('/static/', 1)[1]
        else:
            rel = path_part.lstrip('/')
        local = (_UPLOADS_DIR / rel.lstrip('/')).resolve()
        # 防目录穿越：解析后的路径必须位于 uploads 下
        if not str(local).startswith(str(_UPLOADS_DIR.resolve())):
            return None
        if not local.is_file():
            return None
        return local.read_bytes()
    except (OSError, ValueError) as exc:
        upload_logger.warning(f'水印素材读取失败: {static_url}, 原因: {exc}')
        return None


# ---------- 渲染（同步，Pillow CPU 操作） ----------

def apply_watermark(content: bytes, ext: str, resolved: ResolvedWatermark) -> Optional[bytes]:
    """给图片字节合成水印；返回 None 表示无需处理（格式不符 / 图太小）。

    抛出的异常由调用方捕获（fail-open 按原图落盘）。
    """
    from PIL import Image, ImageDraw, ImageFont

    if ext not in WATERMARK_IMAGE_EXTENSIONS or not resolved.material:
        return None

    img = Image.open(BytesIO(content))
    img.load()
    width, height = img.size
    if width < MIN_IMAGE_EDGE or height < MIN_IMAGE_EDGE:
        return None

    if resolved.mode == 'tile':
        layer = _build_tile_layer((width, height), resolved.material)
    else:
        layer = _build_corner_layer((width, height), resolved.material)

    base = img.convert('RGBA')
    base.alpha_composite(layer)

    out = BytesIO()
    if ext in ('.jpg', '.jpeg'):
        base.convert('RGB').save(out, format='JPEG', quality=85)
    elif ext == '.webp':
        # 上传管线先经 image_optimize 转 webp，水印在其后合成
        base.save(out, format='WEBP', quality=85)
    else:
        base.save(out, format='PNG')
    return out.getvalue()


def _build_corner_layer(size, material: WatermarkMaterial) -> 'Image':
    """右下角单戳：生成与目标图同尺寸的透明层并贴入水印。"""
    from PIL import Image

    width, height = size
    wm = _render_material(size, material)
    margin = max(MARGIN_MIN, int(min(width, height) * MARGIN_RATIO))
    x = max(0, width - wm.width - margin)
    y = max(0, height - wm.height - margin)

    layer = Image.new('RGBA', size, (0, 0, 0, 0))
    layer.paste(wm, (x, y), wm)
    return layer


def _build_tile_layer(size, material: WatermarkMaterial) -> 'Image':
    """45° 斜向平铺：在大画布上铺满旋转后的水印，再居中裁回目标尺寸。"""
    from PIL import Image

    width, height = size
    # 平铺用短边 × TILE_BASE_RATIO 基准的水印，间隔 0.4 倍，保证密度
    wm = _render_material((int(min(width, height) * TILE_BASE_RATIO),) * 2, material, tile=True)
    rotated = wm.rotate(45, expand=True, resample=Image.BICUBIC)
    rw, rh = rotated.size
    step_x, step_y = int(rw * (1 + TILE_SPACING_RATIO)), int(rh * (1 + TILE_SPACING_RATIO))

    canvas = Image.new('RGBA', (width + 2 * rw, height + 2 * rh), (0, 0, 0, 0))
    for cy in range(0, canvas.height, step_y):
        for cx in range(0, canvas.width, step_x):
            canvas.paste(rotated, (cx, cy), rotated)

    left = (canvas.width - width) // 2
    top = (canvas.height - height) // 2
    return canvas.crop((left, top, left + width, top + height))


def _render_material(target_size, material: WatermarkMaterial, tile: bool = False) -> 'Image':
    """按素材类型渲染单个水印图（RGBA，已应用透明度）。

    corner 模式 target_size 为目标图尺寸，按比例推算各元素大小；
    tile 模式 target_size 为 (基准边, 基准边)，字号取基准的 16%（钳 16~48）。
    """
    from PIL import Image

    short_edge = min(target_size)
    if tile:
        opacity = TILE_OPACITY
        font_size = _clamp(int(short_edge * TILE_FONT_RATIO), TILE_FONT_MIN, TILE_FONT_MAX)
        icon_h = _clamp(int(short_edge * TILE_ICON_RATIO), 16, 48)
        logo_w = min(int(short_edge * 0.8), 320)
    else:
        opacity = None
        font_size = _clamp(int(short_edge * TEXT_SIZE_RATIO), TEXT_SIZE_MIN, TEXT_SIZE_MAX)
        icon_h = _clamp(int(short_edge * ICON_HEIGHT_RATIO), ICON_HEIGHT_MIN, ICON_HEIGHT_MAX)
        logo_w = min(int(target_size[0] * LOGO_WIDTH_RATIO), LOGO_MAX_WIDTH)

    if material.kind == 'logo':
        return _render_logo(material.image_bytes, logo_w, opacity or LOGO_OPACITY)
    if material.kind == 'icon_text':
        return _render_icon_text(material.image_bytes, material.text, icon_h, font_size,
                                 opacity or TEXT_OPACITY)
    return _render_text(material.text or '', font_size, opacity or TEXT_OPACITY)


def _render_logo(logo_bytes: bytes, logo_w: int, opacity: float) -> 'Image':
    from PIL import Image

    logo = Image.open(BytesIO(logo_bytes)).convert('RGBA')
    logo_w = max(1, logo_w)
    ratio = logo_w / logo.width
    logo_h = max(1, int(logo.height * ratio))
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
    return _apply_opacity(logo, opacity)


def _render_icon_text(icon_bytes: bytes, text: str, icon_h: int, font_size: int, opacity: float) -> 'Image':
    from PIL import Image

    icon = Image.open(BytesIO(icon_bytes)).convert('RGBA')
    icon_w = max(1, int(icon.width * (icon_h / icon.height)))
    icon = icon.resize((icon_w, icon_h), Image.LANCZOS)

    font = _load_font(font_size)
    t_w, t_h = _measure_text(text, font)
    gap = max(2, int(icon_h * 0.35))
    total_w, total_h = icon_w + gap + t_w, max(icon_h, t_h)

    wm = Image.new('RGBA', (total_w, total_h), (0, 0, 0, 0))
    wm.paste(icon, (0, (total_h - icon_h) // 2), icon)
    _draw_text(wm, (icon_w + gap, (total_h - t_h) // 2), text, font, opacity)
    return wm


def _render_text(text: str, font_size: int, opacity: float) -> 'Image':
    from PIL import Image

    font = _load_font(font_size)
    t_w, t_h = _measure_text(text, font)

    wm = Image.new('RGBA', (t_w, t_h), (0, 0, 0, 0))
    _draw_text(wm, (0, 0), text, font, opacity)
    return wm


def _draw_text(image, pos, text: str, font, opacity: float) -> None:
    """白字 + 黑描边，保证任意底色可读。"""
    from PIL import ImageDraw

    draw = ImageDraw.Draw(image)
    stroke = max(1, font.size // 14)
    draw.text(
        pos, text, font=font,
        fill=(255, 255, 255, int(255 * opacity)),
        stroke_width=stroke, stroke_fill=(0, 0, 0, int(255 * opacity * 0.7)),
    )


def _measure_text(text: str, font) -> tuple:
    from PIL import Image, ImageDraw

    canvas = Image.new('RGBA', (1, 1))
    bbox = ImageDraw.Draw(canvas).textbbox((0, 0), text, font=font,
                                           stroke_width=max(1, font.size // 14))
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _load_font(size: int):
    """加载内置中文字体；缺失时回退默认位图字体并告警（中文将显示为方块）。"""
    from PIL import ImageFont

    global _font_object
    try:
        return ImageFont.truetype(str(_FONT_PATH), size)
    except (OSError, ImportError) as exc:
        if _font_object is None:
            upload_logger.warning(f'水印字体缺失（{exc}），文字水印将回退默认字体: {_FONT_PATH}')
            _font_object = ImageFont.load_default()
        return _font_object


def _apply_opacity(image, opacity: float):
    """整体降低水印透明度（与原图自身的 alpha 相乘）。"""
    alpha = image.split()[-1]  # RGBA→alpha 通道；无 alpha 时为灰度（当亮度用）
    image.putalpha(alpha.point(lambda v: int(v * opacity)))
    return image


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))
