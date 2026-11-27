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

# 右下角模式的尺寸按「图宽」取比例：封面常以 760px（文章头图）甚至 320px（列表卡片）
# 的宽度显示，若按短边取比例并设 32px 上限，水印缩放后会小到看不见。
MARGIN_RATIO = 0.025           # 边距 = 图宽 × 2.5%
MARGIN_MIN = 12
LOGO_WIDTH_RATIO = 0.18        # logo 宽 = 图宽 × 18%
LOGO_MAX_WIDTH = 320
LOGO_OPACITY = 0.9
TEXT_WIDTH_RATIO = 0.026       # 字号 = 图宽 × 2.6%（1376 宽的封面约 36px，缩到 760px 显示约 20px）
TEXT_SIZE_MIN, TEXT_SIZE_MAX = 16, 64
ICON_FONT_RATIO = 1.15         # favicon 高 = 字号 × 1.15

# 对比度：白字 + 深色描边 + 柔和投影三者叠加，浅色、深色、花哨底上都能读
TEXT_FILL_ALPHA = 0.95
TEXT_STROKE_ALPHA = 0.7
SHADOW_ALPHA = 0.6

# 平铺模式（防裁剪）：强度低于右下角模式，全图可辨但不抢画面（在真实封面上按 760px 显示调出）
TILE_STRENGTH = 0.65
TILE_BASE_RATIO = 0.35         # 平铺单个水印基准 = 目标图短边 × 35%
TILE_FONT_RATIO = 0.16         # 平铺字号 = 基准 × 16%
TILE_FONT_MIN, TILE_FONT_MAX = 16, 48
TILE_ICON_RATIO = 0.14         # 平铺图标高 = 基准 × 14%
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
    wm, pad = _render_material(size, material)
    margin = max(MARGIN_MIN, int(width * MARGIN_RATIO))
    # wm 四周有 pad 像素的投影缓冲区，按主体尺寸定位，视觉边距才准确
    x = max(0, width - (wm.width - 2 * pad) - margin) - pad
    y = max(0, height - (wm.height - 2 * pad) - margin) - pad

    layer = Image.new('RGBA', size, (0, 0, 0, 0))
    _composite_at(layer, wm, (x, y))
    return layer


def _build_tile_layer(size, material: WatermarkMaterial) -> 'Image':
    """45° 斜向平铺：在大画布上铺满旋转后的水印，再居中裁回目标尺寸。"""
    from PIL import Image

    width, height = size
    # 平铺用短边 × TILE_BASE_RATIO 基准的水印，间隔 0.4 倍，保证密度
    wm, _pad = _render_material((int(min(width, height) * TILE_BASE_RATIO),) * 2, material, tile=True)
    rotated = wm.rotate(45, expand=True, resample=Image.BICUBIC)
    rw, rh = rotated.size
    step_x, step_y = int(rw * (1 + TILE_SPACING_RATIO)), int(rh * (1 + TILE_SPACING_RATIO))

    canvas = Image.new('RGBA', (width + 2 * rw, height + 2 * rh), (0, 0, 0, 0))
    for cy in range(0, canvas.height, step_y):
        for cx in range(0, canvas.width, step_x):
            canvas.alpha_composite(rotated, (cx, cy))

    left = (canvas.width - width) // 2
    top = (canvas.height - height) // 2
    return canvas.crop((left, top, left + width, top + height))


def _render_material(target_size, material: WatermarkMaterial, tile: bool = False) -> tuple:
    """按素材类型渲染单个水印，返回 (RGBA 图, 留边 pad)。

    图中四周 pad 像素是投影的缓冲区，定位时按主体尺寸（宽高各减 2*pad）计算。
    corner 模式 target_size 为目标图尺寸，各元素按图宽取比例；
    tile 模式 target_size 为 (基准边, 基准边)，整体强度降为 TILE_STRENGTH。
    """
    if tile:
        base = min(target_size)
        font_size = _clamp(round(base * TILE_FONT_RATIO), TILE_FONT_MIN, TILE_FONT_MAX)
        icon_h = _clamp(round(base * TILE_ICON_RATIO), 16, 56)
        logo_w = min(round(base * 0.8), 320)
        strength = TILE_STRENGTH
    else:
        width = target_size[0]
        font_size = _clamp(round(width * TEXT_WIDTH_RATIO), TEXT_SIZE_MIN, TEXT_SIZE_MAX)
        icon_h = _clamp(round(font_size * ICON_FONT_RATIO), 16, 72)
        logo_w = min(round(width * LOGO_WIDTH_RATIO), LOGO_MAX_WIDTH)
        strength = 1.0

    if material.kind == 'logo':
        return _render_logo(material.image_bytes, logo_w, strength)
    if material.kind == 'icon_text':
        return _render_icon_text(material.image_bytes, material.text, icon_h, font_size, strength)
    return _render_text(material.text or '', font_size, strength)


def _render_logo(logo_bytes: bytes, logo_w: int, strength: float) -> tuple:
    """logo 水印：等比缩放 + 投影（logo 自身颜色不定，靠投影保证浅色底上可辨）。"""
    from PIL import Image

    logo = _load_rgba(logo_bytes)
    logo_w = max(1, logo_w)
    logo_h = max(1, round(logo.height * logo_w / logo.width))
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
    _apply_opacity(logo, LOGO_OPACITY * strength)
    return _with_shadow(logo, max(1.0, logo_h / 8), strength)


def _render_icon_text(icon_bytes: bytes, text: str, icon_h: int, font_size: int, strength: float) -> tuple:
    """favicon 小图标 + 名称，整体带投影。"""
    from PIL import Image, ImageDraw

    icon_h = max(1, icon_h)
    icon = _load_rgba(icon_bytes)
    icon_w = max(1, round(icon.width * icon_h / icon.height))
    icon = icon.resize((icon_w, icon_h), Image.LANCZOS)
    _apply_opacity(icon, LOGO_OPACITY * strength)

    font = _load_font(font_size)
    stroke = _stroke_width(font_size)
    t_w, t_h, offset_x, offset_y = _text_bbox(text or '', font, stroke)
    gap = max(4, round(font_size * 0.45))

    body = Image.new('RGBA', (icon_w + gap + t_w, max(icon_h, t_h)), (0, 0, 0, 0))
    body.paste(icon, (0, (body.height - icon_h) // 2), icon)
    ImageDraw.Draw(body).text(
        (icon_w + gap - offset_x, (body.height - t_h) // 2 - offset_y), text or '', font=font,
        fill=(255, 255, 255, _alpha(TEXT_FILL_ALPHA, strength)),
        stroke_width=stroke, stroke_fill=(0, 0, 0, _alpha(TEXT_STROKE_ALPHA, strength)),
    )
    return _with_shadow(body, max(1.0, max(font_size, icon_h) / 8), strength)


def _render_text(text: str, font_size: int, strength: float) -> tuple:
    """纯文字水印：白字 + 深色描边 + 投影。"""
    from PIL import Image, ImageDraw

    font = _load_font(font_size)
    stroke = _stroke_width(font_size)
    t_w, t_h, offset_x, offset_y = _text_bbox(text, font, stroke)

    body = Image.new('RGBA', (max(1, t_w), max(1, t_h)), (0, 0, 0, 0))
    ImageDraw.Draw(body).text(
        (-offset_x, -offset_y), text, font=font,
        fill=(255, 255, 255, _alpha(TEXT_FILL_ALPHA, strength)),
        stroke_width=stroke, stroke_fill=(0, 0, 0, _alpha(TEXT_STROKE_ALPHA, strength)),
    )
    return _with_shadow(body, max(1.0, font_size / 7), strength)


def _load_rgba(image_bytes: bytes) -> 'Image':
    from PIL import Image

    return Image.open(BytesIO(image_bytes)).convert('RGBA')


def _with_shadow(body: 'Image', blur: float, strength: float) -> tuple:
    """给主体加一圈柔和的深色投影，返回 (带留边的图, 留边 pad)。

    投影取主体 alpha 通道做高斯模糊得到，所以对文字、logo、图标一视同仁；
    纯白主体落在浅色区域时，靠这圈暗色光晕与背景分开。
    """
    from PIL import Image, ImageFilter

    pad = int(2 * blur) + 2
    size = (body.width + 2 * pad, body.height + 2 * pad)
    halo = Image.new('L', size, 0)
    halo.paste(
        body.filter(ImageFilter.GaussianBlur(blur)).split()[3]
        .point(lambda v: int(v * SHADOW_ALPHA * strength)),
        (pad, pad),
    )
    out = Image.new('RGBA', size, (0, 0, 0, 0))
    out.putalpha(halo)  # RGB 保持全 0，即黑色投影
    out.alpha_composite(body, (pad, pad))
    return out, pad


def _composite_at(dst: 'Image', src: 'Image', pos: tuple) -> None:
    """把 src 以 'over' 方式合成到 dst 上，越界部分自动裁掉。

    不能用 paste(src, pos, src)：以 alpha 作遮罩贴图会把透明度再乘一次，
    描边设计的 0.7 实际只剩约 0.42，浅色底上就糊了。
    """
    x, y = pos
    crop_left, crop_top = max(0, -x), max(0, -y)
    if crop_left >= src.width or crop_top >= src.height:
        return
    x, y = max(0, x), max(0, y)
    if crop_left or crop_top:
        src = src.crop((crop_left, crop_top, src.width, src.height))
    dst.alpha_composite(src, (x, y))


def _stroke_width(size: int) -> int:
    """描边宽度：太细压不住浅色底，太粗会把汉字内部的空隙糊死。"""
    return max(1, round(size / 16))


def _alpha(base_alpha: float, strength: float) -> int:
    return int(255 * min(1.0, base_alpha * strength))


def _text_bbox(text: str, font, stroke: int) -> tuple:
    """文字（含描边）的包围盒：返回 (宽, 高, 左偏移, 上偏移)。"""
    from PIL import Image, ImageDraw

    canvas = Image.new('RGBA', (1, 1))
    left, top, right, bottom = ImageDraw.Draw(canvas).textbbox(
        (0, 0), text, font=font, stroke_width=stroke
    )
    return right - left, bottom - top, left, top


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
