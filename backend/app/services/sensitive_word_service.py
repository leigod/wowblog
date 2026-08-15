"""
敏感词检测服务

三档处理（对应 wb_sensitive_words.type）：
  - banned : 命中即拦截（blocked=True，调用方拒绝发布）
  - replace: 命中替换为 replacement（缺省用等长 *）
  - review : 命中标记待审核（need_review=True，调用方把评论 audit_status 置 pending）

总开关：wb_config.sensitive_words_enabled（0=关闭，1=启用），关闭时直接放行。
词库缓存：进程内 TTL 5 分钟；后台增删改敏感词后由 invalidate_sensitive_words_cache() 立即失效。
"""
import time
from dataclasses import dataclass
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.models.admin_comments as models_admin
from app.crud.siteconfig import get_site_config

_CACHE_TTL = 300  # 秒

_words_cache: List[models_admin.SensitiveWord] = []
_cache_at: float = 0.0


@dataclass
class CheckResult:
    blocked: bool = False
    text: str = ''
    need_review: bool = False


def invalidate_sensitive_words_cache() -> None:
    """词库变更后调用，立即失效进程内缓存（下次检测重新加载）。"""
    global _words_cache, _cache_at
    _words_cache = []
    _cache_at = 0.0


async def _get_active_words(db: AsyncSession) -> List[models_admin.SensitiveWord]:
    """获取启用中的敏感词（带 TTL 缓存）。"""
    global _words_cache, _cache_at
    now = time.time()
    if _words_cache and now - _cache_at < _CACHE_TTL:
        return _words_cache
    result = await db.execute(
        select(models_admin.SensitiveWord).where(
            models_admin.SensitiveWord.status == 'active'
        )
    )
    _words_cache = list(result.scalars().all())
    _cache_at = now
    return _words_cache


async def check_sensitive_content(db: AsyncSession, text: str) -> CheckResult:
    """
    检测评论文本。返回 CheckResult：
      blocked=True   → 调用方拒绝发布（提示含违禁词，不透露具体词，防绕过）
      text           → 处理后的文本（replace 已生效），调用方应使用该文本入库
      need_review=True → 调用方将评论 audit_status 置 'pending'
    """
    result = CheckResult(text=text or '')
    if not result.text:
        return result

    # 总开关（wb_config 单行查询，微秒级；词库缓存另算）
    config = await get_site_config(db)
    if not config or (config.sensitive_words_enabled or 0) != 1:
        return result

    words = await _get_active_words(db)
    for w in words:
        if not w.word:
            continue
        if w.type == 'banned':
            if w.word in result.text:
                result.blocked = True
                return result  # 拦截优先，直接终止
        elif w.type == 'replace':
            if w.word in result.text:
                result.text = result.text.replace(
                    w.word, w.replacement or '*' * max(len(w.word), 1)
                )
        elif w.type == 'review':
            if w.word in result.text:
                result.need_review = True
    return result
