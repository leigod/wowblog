"""图片优化服务测试：压缩/转 WebP/尺寸钳制/EXIF 方向/边界与 fail-open。"""
import pytest
from io import BytesIO

from PIL import Image

from app.services.image_optimize import optimize_image, MAX_DIMENSION


def make_jpeg(w, h, quality=92, exif_orientation=None) -> bytes:
    """带渐变的 JPEG（照片近似）；可注入 EXIF Orientation。"""
    img = Image.new('RGB', (w, h))
    px = img.load()
    for y in range(h):
        for x in range(0, w, 4):  # 步进4列提速，渐变足够平滑
            c = (x * 255 // w, y * 255 // h, (x + y) * 255 // (w + h))
            for dx in range(4):
                if x + dx < w:
                    px[x + dx, y] = c
    kwargs = {'quality': quality}
    if exif_orientation:
        exif = Image.Exif()
        exif[274] = exif_orientation  # Orientation tag
        kwargs['exif'] = exif
    buf = BytesIO()
    img.save(buf, 'JPEG', **kwargs)
    return buf.getvalue()


def make_png(w, h, alpha=False) -> bytes:
    mode = 'RGBA' if alpha else 'RGB'
    buf = BytesIO()
    Image.new(mode, (w, h), (200, 60, 60, 128) if alpha else (200, 60, 60)).save(buf, 'PNG')
    return buf.getvalue()


def test_large_jpeg_converted_and_resized():
    src = make_jpeg(4032, 3024)
    out, ext = optimize_image(src, '.jpg')
    assert ext == '.webp'
    img = Image.open(BytesIO(out))
    assert img.format == 'WEBP'
    assert max(img.size) == MAX_DIMENSION           # 长边被钳制
    assert len(out) < len(src)                      # 体积必须减小


def test_small_image_no_upscale_but_still_webp():
    src = make_jpeg(800, 600)
    out, ext = optimize_image(src, '.jpg')
    assert ext == '.webp'
    assert Image.open(BytesIO(out)).size == (800, 600)  # 小图不放大


def test_exif_orientation_applied():
    """竖拍（Orientation=6）照片：方向应应用到像素，宽高转置。"""
    src = make_jpeg(1600, 1200, exif_orientation=6)
    out, ext = optimize_image(src, '.jpg')
    img = Image.open(BytesIO(out))
    assert img.size == (1200, 1600)                 # EXIF 转置生效


def test_png_alpha_preserved_in_webp():
    src = make_png(600, 400, alpha=True)
    out, ext = optimize_image(src, '.png')
    assert ext == '.webp'
    img = Image.open(BytesIO(out))
    assert img.mode == 'RGBA'
    assert img.getpixel((10, 10))[3] == 128         # 半透明保留


def test_gif_and_others_untouched():
    assert optimize_image(b'GIF89a...', '.gif') == (b'GIF89a...', '.gif')
    assert optimize_image(b'%PDF-1.4', '.pdf') == (b'%PDF-1.4', '.pdf')
    assert optimize_image(b'\x00\x00\x01\x00', '.ico') == (b'\x00\x00\x01\x00', '.ico')


def test_fail_open_on_garbage():
    garbage = b'this is not an image at all'
    assert optimize_image(garbage, '.jpg') == (garbage, '.jpg')


def test_bigger_result_keeps_original():
    """优化结果反而变大时保留原字节（用已高度压缩的纯色 JPEG 模拟）。"""
    buf = BytesIO()
    Image.new('RGB', (300, 200), (10, 10, 10)).save(buf, 'JPEG', quality=30)
    src = buf.getvalue()
    out, ext = optimize_image(src, '.jpg')
    # 无论转或不转，结果必须不超过原体积
    assert len(out) <= len(src)
    if ext != '.webp':
        assert out == src
