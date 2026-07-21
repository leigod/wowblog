"""
媒体相关API路由
处理视频嵌入、解析等功能
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import re
import httpx

from app.models.response import ApiResponse
from app.utils.response import success, error

router = APIRouter()


class DouyinVideoRequest(BaseModel):
    """抖音视频解析请求"""
    url: str


class DouyinVideoResponse(BaseModel):
    """抖音视频解析响应"""
    video_id: str
    embed_url: str
    original_url: str


@router.post("/media/douyin/parse", response_model=ApiResponse[dict])
async def parse_douyin_video(request: DouyinVideoRequest):
    """
    解析抖音视频链接，获取视频ID和嵌入代码

    支持的链接格式:
    - 短链接: https://v.douyin.com/xxxxx/
    - 完整链接: https://www.douyin.com/video/xxxxx/
    - 分享链接: https://www.douyin.com/user/.../video/xxxxx/
    """
    url = request.url.strip()

    if not url:
        return error('请提供抖音视频链接')

    try:
        # 处理短链接 - 先重定向获取真实URL
        if 'v.douyin.com' in url:
            real_url = await resolve_short_url(url)
            if not real_url:
                return error('无法解析短链接，请检查链接是否有效')
            url = real_url

        # 从URL中提取视频ID
        video_id = extract_douyin_video_id(url)

        if not video_id:
            return error('无法从链接中提取视频ID，请检查链接格式')

        # 构建嵌入URL (使用抖音官方embed方式)
        embed_url = f"https://open.douyin.com/player/video?vid={video_id}"

        return success(data={
            "video_id": video_id,
            "embed_url": embed_url,
            "original_url": url
        })

    except Exception as e:
        return error(f'解析失败: {str(e)}')


async def resolve_short_url(short_url: str) -> Optional[str]:
    """
    解析短链接，获取真实URL

    Args:
        short_url: 短链接地址

    Returns:
        真实URL或None
    """
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            # 发送HEAD请求获取重定向后的URL
            response = await client.head(short_url)
            return str(response.url)
    except Exception as e:
        print(f"解析短链接失败: {e}")
        return None


def extract_douyin_video_id(url: str) -> Optional[str]:
    """
    从抖音URL中提取视频ID

    支持的URL格式:
    - /video/730xxxxx/
    - /share/video/730xxxxx/
    - 参数中的 video_id=730xxxxx

    Args:
        url: 抖音视频URL

    Returns:
        视频ID或None
    """
    # 模式1: /video/数字ID/
    pattern1 = r'/video/(\d+)'
    match1 = re.search(pattern1, url)
    if match1:
        return match1.group(1)

    # 模式2: /share/video/数字ID/
    pattern2 = r'/share/video/(\d+)'
    match2 = re.search(pattern2, url)
    if match2:
        return match2.group(1)

    # 模式3: 参数中的 video_id
    pattern3 = r'[?&]video_id=(\d+)'
    match3 = re.search(pattern3, url)
    if match3:
        return match3.group(1)

    return None


@router.get("/media/douyin/test", response_model=ApiResponse[dict])
async def test_douyin_api():
    """测试抖音API是否正常"""
    return success(data={
        "message": "抖音视频解析API正常",
        "supported_formats": [
            "https://v.douyin.com/xxxxx/",
            "https://www.douyin.com/video/xxxxx/",
            "https://www.douyin.com/user/.../video/xxxxx/"
        ]
    })
