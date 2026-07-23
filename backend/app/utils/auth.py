"""
密码哈希工具

直接使用 bcrypt 库进行密码哈希与校验。

注意：passlib 1.7.4 与 bcrypt 4.x 存在后端初始化不兼容问题
（detect_wrap_bug 触发 "password cannot be longer than 72 bytes" 异常），
hash/verify 均无法工作，故绕过 passlib 直接调用 bcrypt 库。
"""
import bcrypt
import logging

logger = logging.getLogger(__name__)

# bcrypt 单次密码上限为 72 字节，超出部分截断（bcrypt 自身行为）
_BCRYPT_MAX_BYTES = 72


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    使用 bcrypt 校验明文密码与哈希是否匹配。

    Args:
        plain_password: 用户输入的明文密码
        hashed_password: 数据库中存储的 bcrypt 哈希

    Returns:
        bool: 密码是否匹配；哈希格式非法时返回 False（不抛异常）
    """
    try:
        pwd_bytes = plain_password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except (ValueError, TypeError):
        return False


def get_password_hash(password: str) -> str:
    """
    使用 bcrypt 哈希密码。

    Args:
        password: 明文密码

    Returns:
        str: bcrypt 哈希（60 字符，$2b$ 格式）
    """
    pwd_bytes = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.hashpw(pwd_bytes, bcrypt.gensalt()).decode("utf-8")
