from fastapi import APIRouter, File, UploadFile, Request, Depends, HTTPException

from app.models.response import ApiResponse
from app.utils.response import success, error
from app.dependencies.authentication import get_current_user
import os
import pathlib
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
async def upload_file(request: Request, file: UploadFile = File(), current_user: str = Depends(get_current_user)):
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
