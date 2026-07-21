"""
密码哈希工具

统一使用 bcrypt 进行密码哈希与校验。
- get_password_hash(password)：bcrypt 哈希（60 字符）
- verify_password(plain, hashed)：明文与哈希比对

历史遗留的 MD5 + salt 方案已移除，旧用户请通过
reset_passwords_to_bcrypt.py 迁移脚本统一重置为 bcrypt。
"""
from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    使用 bcrypt 校验明文密码与哈希是否匹配。

    Args:
        plain_password: 用户输入的明文密码
        hashed_password: 数据库中存储的 bcrypt 哈希

    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    使用 bcrypt 哈希密码。

    Args:
        password: 明文密码

    Returns:
        str: bcrypt 哈希（60 字符）
    """
    return pwd_context.hash(password)
