"""
API 速率限制

RateLimiter 支持 Redis 后端（多 worker / 多实例共享计数，生产推荐），
未配置 REDIS_HOST 时自动回退内存存储（仅单 worker 有效，开发可用）。
全局兜底由 main.py 的中间件应用，关键端点（登录/注册）用更严格的依赖。
"""

import time
import os
import asyncio
from collections import defaultdict
from fastapi import Request, HTTPException, status
from typing import Dict, Tuple
import logging

try:
    import redis.asyncio as aioredis
except ImportError:  # pragma: no cover
    aioredis = None

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    速率限制器：Redis 后端优先（多 worker 共享），回退内存。
    """

    def __init__(self):
        # 内存回退存储：{ip: [timestamp, ...]}
        self.requests: Dict[str, list] = defaultdict(list)
        self._lock = asyncio.Lock()
        self._redis = None
        self._redis_checked = False

    async def _get_redis(self):
        """惰性获取 Redis 连接；未配置 REDIS_HOST 或连接失败则返回 None（回退内存）"""
        if not self._redis_checked:
            self._redis_checked = True
            host = os.getenv("REDIS_HOST")
            if host and aioredis is not None:
                try:
                    password = os.getenv("REDIS_PASSWORD")
                    auth = f"{password}@" if password else ""
                    url = f"redis://{auth}{host}:{os.getenv('REDIS_PORT', '6379')}/{os.getenv('REDIS_DB', '0')}"
                    self._redis = aioredis.from_url(url, decode_responses=True)
                except Exception as e:
                    logger.warning(f"Redis 连接失败，回退内存限流: {e}")
                    self._redis = None
        return self._redis

    async def is_allowed(
        self,
        key: str,
        max_requests: int = 100,
        window_seconds: int = 60
    ) -> Tuple[bool, int]:
        """
        检查是否允许请求

        Returns:
            (是否允许, 重置时间戳/剩余请求数)
        """
        redis = await self._get_redis()
        if redis is not None:
            return await self._is_allowed_redis(redis, key, max_requests, window_seconds)
        return await self._is_allowed_memory(key, max_requests, window_seconds)

    async def _is_allowed_redis(self, redis, key, max_requests, window_seconds) -> Tuple[bool, int]:
        """Redis 固定窗口计数（INCR + EXPIRE nx），多 worker 共享"""
        pipe = redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, window_seconds, nx=True)  # 仅首次请求设置窗口 TTL
        count, _ = await pipe.execute()
        if count > max_requests:
            ttl = await redis.ttl(key)
            reset = int(time.time() + (ttl if ttl and ttl > 0 else window_seconds))
            return False, reset
        return True, max_requests - count

    async def _is_allowed_memory(self, key, max_requests, window_seconds) -> Tuple[bool, int]:
        """内存滑动窗口（单 worker 回退）"""
        current_time = time.time()
        window_start = current_time - window_seconds
        async with self._lock:
            self.requests[key] = [t for t in self.requests[key] if t > window_start]
            if len(self.requests[key]) >= max_requests:
                oldest_request = self.requests[key][0]
                return False, int(oldest_request + window_seconds)
            self.requests[key].append(current_time)
            return True, max_requests - len(self.requests[key])

    async def cleanup_old_entries(self, max_age_seconds: int = 3600):
        """清理过期条目（仅内存模式需要；Redis 模式靠 key TTL 自管理）"""
        if await self._get_redis() is not None:
            return
        current_time = time.time()
        cutoff_time = current_time - max_age_seconds
        async with self._lock:
            keys_to_remove = []
            for key, request_times in self.requests.items():
                self.requests[key] = [t for t in request_times if t > cutoff_time]
                if not self.requests[key]:
                    keys_to_remove.append(key)
            for key in keys_to_remove:
                del self.requests[key]
        if keys_to_remove:
            logger.debug(f"清理了 {len(keys_to_remove)} 个过期的速率限制条目")


# 全局限流器实例
limiter = RateLimiter()


def get_client_ip(request: Request) -> str:
    """获取客户端真实 IP（支持 X-Forwarded-For / X-Real-IP 代理头）"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    if request.client:
        return request.client.host

    return "unknown"


async def check_rate_limit(
    request: Request,
    max_requests: int = 100,
    window_seconds: int = 60,
    key_prefix: str = ""
) -> None:
    """检查速率限制，超限抛 429"""
    client_ip = get_client_ip(request)
    limit_key = f"{key_prefix}:{client_ip}"

    allowed, reset_info = await limiter.is_allowed(
        key=limit_key,
        max_requests=max_requests,
        window_seconds=window_seconds
    )

    if not allowed:
        reset_time = reset_info
        retry_after = max(1, reset_time - int(time.time()))
        logger.warning(
            f"速率限制触发: IP={client_ip}, 限制={max_requests}/{window_seconds}s"
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "请求过于频繁，请稍后再试",
                "retry_after": retry_after,
                "limit": max_requests,
                "window": window_seconds
            },
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(max_requests),
                "X-RateLimit-Reset": str(reset_time),
            }
        )


# 预定义的速率限制配置
RATE_LIMITS = {
    "default": (300, 60),     # 默认：300/分钟（全局兜底）
    "auth": (10, 60),         # 认证：10/分钟
    "login": (5, 60),         # 登录：5/分钟
    "register": (3, 300),     # 注册：3/5分钟
    "api": (60, 60),          # 一般 API：60/分钟
    "upload": (10, 60),       # 上传：10/分钟
    "admin": (200, 60),       # 管理后台：200/分钟
}


async def rate_limit_middleware(
    request: Request,
    limit_type: str = "default"
) -> None:
    """速率限制依赖（在路由 Depends 中使用）"""
    max_requests, window_seconds = RATE_LIMITS.get(limit_type, RATE_LIMITS["default"])
    await check_rate_limit(
        request=request,
        max_requests=max_requests,
        window_seconds=window_seconds,
        key_prefix=limit_type
    )


async def start_cleanup_task(interval_seconds: int = 300):
    """定期清理任务（内存模式才需要；Redis 模式 TTL 自管理）。可在 lifespan 中启动。"""
    while True:
        await asyncio.sleep(interval_seconds)
        await limiter.cleanup_old_entries()
