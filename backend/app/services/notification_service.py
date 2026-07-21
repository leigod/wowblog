"""
通知服务 - 用于创建各种类型的通知
"""
import app.models.schemas.notifications as schemas
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import re


class NotificationService:
    """通知服务"""

    @staticmethod
    def _build_target_url(target_type: str, target_id: int) -> Optional[str]:
        """根据目标类型构建URL"""
        url_map = {
            'article': f'/article/{target_id}',  # 需要调整为实际slug
            'comment': f'/article/{target_id}',  # 评论的target_id是文章ID
            'doc': f'/docs/{target_id}',
        }
        return url_map.get(target_type)

    @staticmethod
    async def create_comment_notification(
        db: AsyncSession,
        recipient_user_id: int,
        actor_id: int,
        actor_name: str,
        actor_avatar: str,
        article_id: int,
        article_title: str,
        article_slug: str,
        comment_content: str
    ):
        """创建评论通知"""
        notification = schemas.NotificationCreate(
            user_id=recipient_user_id,
            type='comment',
            title=f'{actor_name} 评论了你的文章',
            content=NotificationService.strip_html(comment_content)[:100] if comment_content else '',
            actor_id=actor_id,
            actor_name=actor_name,
            actor_avatar=actor_avatar,
            target_type='article',
            target_id=article_id,
            target_title=article_title,
            target_url=f'/article/{article_slug}'
        )
        from app.crud.notifications import create_notification
        return await create_notification(db, notification)

    @staticmethod
    async def create_reply_notification(
        db: AsyncSession,
        recipient_user_id: int,
        actor_id: int,
        actor_name: str,
        actor_avatar: str,
        article_id: int,
        article_title: str,
        article_slug: str,
        reply_content: str
    ):
        """创建回复通知"""
        notification = schemas.NotificationCreate(
            user_id=recipient_user_id,
            type='reply',
            title=f'{actor_name} 回复了你的评论',
            content=NotificationService.strip_html(reply_content)[:100] if reply_content else '',
            actor_id=actor_id,
            actor_name=actor_name,
            actor_avatar=actor_avatar,
            target_type='comment',
            target_id=article_id,
            target_title=article_title,
            target_url=f'/article/{article_slug}'
        )
        from app.crud.notifications import create_notification
        return await create_notification(db, notification)

    @staticmethod
    async def create_article_mention_notification(
        db: AsyncSession,
        recipient_user_id: int,
        actor_id: int,
        actor_name: str,
        actor_avatar: str,
        article_id: int,
        article_title: str,
        article_slug: str,
        mention_context: str
    ):
        """创建文章@提及通知"""
        notification = schemas.NotificationCreate(
            user_id=recipient_user_id,
            type='article_mention',
            title=f'{actor_name} 在文章中提到了你',
            content=NotificationService.strip_html(mention_context)[:100] if mention_context else '',
            actor_id=actor_id,
            actor_name=actor_name,
            actor_avatar=actor_avatar,
            target_type='article',
            target_id=article_id,
            target_title=article_title,
            target_url=f'/article/{article_slug}'
        )
        from app.crud.notifications import create_notification
        return await create_notification(db, notification)

    @staticmethod
    async def create_comment_mention_notification(
        db: AsyncSession,
        recipient_user_id: int,
        actor_id: int,
        actor_name: str,
        actor_avatar: str,
        article_id: int,
        article_title: str,
        article_slug: str,
        comment_content: str
    ):
        """创建评论@提及通知"""
        notification = schemas.NotificationCreate(
            user_id=recipient_user_id,
            type='comment_mention',
            title=f'{actor_name} 在评论中提到了你',
            content=NotificationService.strip_html(comment_content)[:100] if comment_content else '',
            actor_id=actor_id,
            actor_name=actor_name,
            actor_avatar=actor_avatar,
            target_type='comment',
            target_id=article_id,
            target_title=article_title,
            target_url=f'/article/{article_slug}'
        )
        from app.crud.notifications import create_notification
        return await create_notification(db, notification)

    @staticmethod
    async def create_like_notification(
        db: AsyncSession,
        recipient_user_id: int,
        actor_id: int,
        actor_name: str,
        actor_avatar: str,
        article_id: int,
        article_title: str,
        article_slug: str
    ):
        """创建点赞通知"""
        notification = schemas.NotificationCreate(
            user_id=recipient_user_id,
            type='like',
            title=f'{actor_name} 赞了你的文章',
            content=f'{actor_name} 赞了《{article_title}》',
            actor_id=actor_id,
            actor_name=actor_name,
            actor_avatar=actor_avatar,
            target_type='article',
            target_id=article_id,
            target_title=article_title,
            target_url=f'/article/{article_slug}'
        )
        from app.crud.notifications import create_notification
        return await create_notification(db, notification)

    @staticmethod
    async def create_bookmark_notification(
        db: AsyncSession,
        recipient_user_id: int,
        actor_id: int,
        actor_name: str,
        actor_avatar: str,
        article_id: int,
        article_title: str,
        article_slug: str
    ):
        """创建收藏通知"""
        notification = schemas.NotificationCreate(
            user_id=recipient_user_id,
            type='bookmark',
            title=f'{actor_name} 收藏了你的文章',
            content=f'{actor_name} 收藏了《{article_title}》',
            actor_id=actor_id,
            actor_name=actor_name,
            actor_avatar=actor_avatar,
            target_type='article',
            target_id=article_id,
            target_title=article_title,
            target_url=f'/article/{article_slug}'
        )
        from app.crud.notifications import create_notification
        return await create_notification(db, notification)

    @staticmethod
    def parse_mentions(content: str) -> List[str]:
        """解析内容中的@提及用户名"""
        # 匹配 @username 格式，用户名支持字母、数字、下划线、中文
        mention_pattern = r'@([a-zA-Z0-9_一-龥]+)'
        matches = re.findall(mention_pattern, content)
        return list(set(matches))  # 去重

    @staticmethod
    def strip_html(html: str) -> str:
        """去除 HTML 标签，只保留纯文本"""
        if not html:
            return ""
        # 移除 HTML 标签
        text = re.sub(r'<[^>]+>', '', html)
        # 清理多余的空白字符
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @staticmethod
    async def create_mentions_notifications(
        db: AsyncSession,
        content: str,
        actor_id: int,
        actor_name: str,
        actor_avatar: str,
        article_id: int,
        article_title: str,
        article_slug: str,
        mention_type: str,  # 'article' or 'comment'
        exclude_user_id: Optional[int] = None
    ):
        """批量创建@提及通知"""
        from app.crud.notifications import create_notifications_batch
        from app.crud.users import get_user_by_username

        mentions = NotificationService.parse_mentions(content)
        notifications = []

        for username in mentions:
            # 获取被提及的用户
            user = await get_user_by_username(db, username)
            if not user:
                continue

            # 排除自己
            if exclude_user_id and user.id == exclude_user_id:
                continue

            if mention_type == 'article':
                notification = schemas.NotificationCreate(
                    user_id=user.id,
                    type='article_mention',
                    title=f'{actor_name} 在文章中提到了你',
                    content=NotificationService.strip_html(content)[:100],
                    actor_id=actor_id,
                    actor_name=actor_name,
                    actor_avatar=actor_avatar,
                    target_type='article',
                    target_id=article_id,
                    target_title=article_title,
                    target_url=f'/article/{article_slug}'
                )
            else:  # comment
                notification = schemas.NotificationCreate(
                    user_id=user.id,
                    type='comment_mention',
                    title=f'{actor_name} 在评论中提到了你',
                    content=NotificationService.strip_html(content)[:100],
                    actor_id=actor_id,
                    actor_name=actor_name,
                    actor_avatar=actor_avatar,
                    target_type='comment',
                    target_id=article_id,
                    target_title=article_title,
                    target_url=f'/article/{article_slug}'
                )

            notifications.append(notification)

        if notifications:
            await create_notifications_batch(db, notifications)

        return len(notifications)
