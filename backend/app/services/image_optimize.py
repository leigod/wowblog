"""图片优化服务：上传图片统一压缩 + 转 WebP。

动机：手机直出照片（4032×3024、2~4MB JPEG）作为文章封面/正文图上传后，
低带宽下加载 3~6 秒。统一管线处理：

1. EXIF 方向应用（exif_transpose，竖拍照片不横躺）；
2. 长边钳制到 MAX_DIMENSION（Retina 2x 下 1280 显示位足够）；
3. 转 WebP（quality=82 视觉近无损，比 JPEG 小 30~50%）。

适用范围：.jpg/.jpeg/.png（GIF 保动画不动；.ico/.pdf 等非照片管线）。
调用方语义（/upload/ 的 purpose 参数）：
  - content: optimize + 水印（正文图）
  - cover:   仅 optimize（封面/OG/分类等展示图，不加水印）
  - material: 完全跳过（logo/favicon 素材，保持原格式原字节）

失败策略 fail-open：任何异常按原字节返回，不阻断上传。
转换结果反而变大时（纯色小图等罕见情况）同样保留原格式。
同步 CPU 函数，调用方需经 anyio.to_thread 运行。
"""
import logging
from io import BytesIO

logger = logging.getLogger('upload')

MAX_DIMENSION = 2560        # 长边上限
WEBP_QUALITY = 82           # 视觉近无损的常用档位
WEBP_METHOD = 6             # 编码努力 0-6：6 压缩率最高，上传低频可接受
OPTIMIZE_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png'}


def optimize_image(content: bytes, ext: str) -> tuple[bytes, str]:
    """压缩并转 WebP；返回 (新字节, 新扩展名)。

    不适用（扩展名不符）、失败或结果反而更大时，原样返回输入。
    """
    if ext not in OPTIMIZE_IMAGE_EXTENSIONS:
        return content, ext

    try:
        from PIL import Image, ImageOps

        img = Image.open(BytesIO(content))
        img.load()

        # 手机竖拍照片的 EXIF 方向应用到像素，避免 resize 后方向丢失
        img = ImageOps.exif_transpose(img)

        # 长边钳制（等比缩小；小图不放大）
        w, h = img.size
        if max(w, h) > MAX_DIMENSION:
            ratio = MAX_DIMENSION / max(w, h)
            img = img.resize((max(1, int(w * ratio)), max(1, int(h * ratio))),
                             Image.LANCZOS)

        # WebP 不支持 P/CMYK 等 mode：带透明通道走 RGBA，其余走 RGB
        base = img.convert('RGBA') if ('transparency' in img.info or 'A' in img.getbands()) \
            else img.convert('RGB')

        out = BytesIO()
        base.save(out, format='WEBP', quality=WEBP_QUALITY, method=WEBP_METHOD)
        webp_bytes = out.getvalue()

        if len(webp_bytes) >= len(content):
            # 罕见：输入已是高度压缩/纯色小图，保留原格式
            return content, ext
        return webp_bytes, '.webp'
    except Exception as exc:  # noqa: BLE001 - fail-open
        logger.warning(f'图片优化失败，按原文件保存: {exc}')
        return content, ext
