from fastapi import APIRouter, File, Form, UploadFile, Request, Depends, HTTPException

from app.models.response import ApiResponse
from app.utils.response import success, error
from app.dependencies.authentication import get_current_user
from app.database import get_db
from app.services import image_optimize, watermark_service
import os
import pathlib
import anyio.to_thread
from datetime import datetime
from app.utils.logger import upload_logger, security_logger

router = APIRouter()

# 上传文件大小限制 2M
UPLOAD_FILE_MAX_SIZE = 1024 * 1024 * 2

# 扩展名白名单：移除 .svg（存储型 XSS 风险，SVG 可内嵌 <script>）；保留 .ico
UPLOAD_FILE_ALLOWED_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx',
    '.xls', '.xlsx', '.ppt', '.pptx', '.ico',
}

# 扩展名 → 合法 MIME 集合（content_type 必须落在其中）
EXT_MIME_MAP: dict[str, set[str]] = {
    '.jpg': {'image/jpeg'},
    '.jpeg': {'image/jpeg'},
    '.png': {'image/png'},
    '.gif': {'image/gif'},
    '.ico': {'image/x-icon', 'image/vnd.microsoft.icon', 'image/ico'},
    '.pdf': {'application/pdf'},
    '.doc': {'application/msword'},
    '.docx': {'application/vnd.openxmlformats-officedocument.wordprocessingml.document'},
    '.xls': {'application/vnd.ms-excel'},
    '.xlsx': {'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'},
    '.ppt': {'application/vnd.ms-powerpoint'},
    '.pptx': {'application/vnd.openxmlformats-officedocument.presentationml.presentation'},
}

# 文件头魔数（magic number）签名 → 该签名可对应的扩展名集合。
# 用于校验文件真实内容，防止伪造扩展名/Content-Type 绕过白名单。
MAGIC_SIGNATURES: list[tuple[bytes, set[str]]] = [
    (b'\xff\xd8\xff', {'.jpg', '.jpeg'}),                       # JPEG
    (b'\x89PNG\r\n\x1a\n', {'.png'}),                           # PNG
    (b'GIF87a', {'.gif'}),                                      # GIF87a
    (b'GIF89a', {'.gif'}),                                      # GIF89a
    (b'%PDF', {'.pdf'}),                                        # PDF
    (b'\x00\x00\x01\x00', {'.ico'}),                            # ICO
    # Office 97-2003（doc/xls/ppt）共用的 OLE 复合文档头
    (b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1', {'.doc', '.xls', '.ppt'}),
    # OOXML（docx/xlsx/pptx）是 ZIP 容器，统一以 PK\x03\x04 开头
    (b'PK\x03\x04', {'.docx', '.xlsx', '.pptx'}),
]


def _detect_exts_by_magic(content: bytes) -> set[str]:
    """根据文件头魔数推断可能的扩展名集合；无法识别时返回空集。"""
    for signature, exts in MAGIC_SIGNATURES:
        if content.startswith(signature):
            return exts
    return set()


@router.post("/upload/", response_model=ApiResponse)
async def upload_file(
    request: Request,
    file: UploadFile = File(),
    purpose: str = Form("content"),
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    """通用文件上传。

    purpose:
      - content（默认）: 文章图片（正文、文章封面、文章 OG 图），优化（压缩转 WebP）
        + 按上传者身份合成水印（Admin/Editor/Contributor → 网站，Author → 个人博客）；
      - cover: 分类/系列/页面/文档等站点素材图，仅优化不加水印；
      - material: logo/favicon 等标识素材，完全跳过图片管线（保持原格式原字节）。
    """
    try:
        client_ip = request.client.host
        upload_logger.info(f"用户 {current_user.username} (IP: {client_ip}) 请求上传文件: {file.filename}")

        content = await file.read()
        origin_filename = file.filename
        _, ext = os.path.splitext(origin_filename or '')
        ext = ext.lower()

        # 1. 大小校验
        if len(content) > UPLOAD_FILE_MAX_SIZE:
            return error(msg="文件过大！请上传小于{}M的文件！".format(UPLOAD_FILE_MAX_SIZE / 1024 / 1024))

        # 2. 扩展名白名单（已移除 .svg）
        if ext not in UPLOAD_FILE_ALLOWED_EXTENSIONS:
            return error(msg="文件类型不支持！请上传{}类型的文件！".format(', '.join(sorted(UPLOAD_FILE_ALLOWED_EXTENSIONS))))

        # 3. MIME 校验：声明的 content_type 必须与扩展名一致
        allowed_mimes = EXT_MIME_MAP.get(ext, set())
        if allowed_mimes and file.content_type and file.content_type not in allowed_mimes:
            security_logger.warning(
                f"上传 MIME 不匹配 - 用户: {current_user.username}, 扩展名: {ext}, "
                f"声明 MIME: {file.content_type}, 允许: {allowed_mimes}"
            )
            return error(msg="文件类型与内容不符！")

        # 4. magic number 校验：文件真实头必须匹配扩展名（防伪造扩展名/Content-Type）
        detected = _detect_exts_by_magic(content)
        if detected and ext not in detected:
            security_logger.warning(
                f"上传 magic number 不匹配 - 用户: {current_user.username}, "
                f"扩展名: {ext}, 实际检测为: {detected}"
            )
            return error(msg="文件内容与扩展名不符！")

        # 5. 图片优化管线（均 fail-open：异常记日志按原文件落盘，不阻断上传）
        #    - optimize（压缩+转 WebP）：purpose=cover/content 的照片类图片
        #      （封面/OG 等展示图 700KB~1.4MB 的主要治理手段）
        #    - 水印：仅 purpose=content；GIF 跳过以保全动图
        if purpose != "material" and ext in image_optimize.OPTIMIZE_IMAGE_EXTENSIONS:
            try:
                content, ext = await anyio.to_thread.run_sync(
                    image_optimize.optimize_image, content, ext
                )
            except Exception as exc:
                upload_logger.warning(
                    f"图片优化失败，按原文件保存 - 用户: {current_user.username}, "
                    f"文件: {file.filename}, 错误: {exc}"
                )

        if purpose == "content" and ext in watermark_service.WATERMARK_IMAGE_EXTENSIONS:
            try:
                resolved = await watermark_service.resolve_watermark(db, current_user)
                if resolved is not None and resolved.material is not None:
                    watermarked = await anyio.to_thread.run_sync(
                        watermark_service.apply_watermark, content, ext, resolved
                    )
                    if watermarked is not None:
                        content = watermarked
            except Exception as exc:
                upload_logger.warning(
                    f"水印合成失败，按原图保存 - 用户: {current_user.username}, "
                    f"文件: {file.filename}, 错误: {exc}"
                )

        # 生成 16 字节随机文件名 + 扩展名
        filename = f"{os.urandom(16).hex()}{ext}"

        app_dir = pathlib.Path(__file__).resolve().parent.parent
        current_date = datetime.now().strftime("%Y%m%d")
        upload_dir = app_dir / "uploads" / current_date
        os.makedirs(upload_dir, exist_ok=True)

        with open(upload_dir / filename, "wb") as f:
            f.write(content)

        return success(data={
            "file_size": len(content),
            "filename": filename,
            "origin_filename": origin_filename,
            "file_type": file.content_type,
            "url": f"/static/{current_date}/{filename}",
            "full_url": f"{request.url.scheme}://{request.url.netloc}/static/{current_date}/{filename}"
        })
    except Exception as e:
        client_ip = request.client.host if request.client else "unknown"
        security_logger.error(f"文件上传失败 - 用户: {getattr(current_user, 'username', 'unknown')}, IP: {client_ip}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail="文件上传失败")
