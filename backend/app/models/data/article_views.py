"""
文章浏览记录表模型
用于记录用户/访客的文章浏览行为，支持后台统计分析
"""
from sqlalchemy import Column, Integer, String, Boolean, Index
from app.database import Base


class ArticleView(Base):
    """文章浏览记录表"""
    __tablename__ = 'wb_article_views'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    user_id = Column(Integer, nullable=True, default=None, comment='用户ID (未登录时为NULL)')
    article_id = Column(Integer, nullable=False, comment='文章ID')
    view_time = Column(Integer, nullable=False, comment='浏览时间 (Unix时间戳)')
    view_duration = Column(Integer, nullable=False, default=0, comment='停留时长 (秒)')
    is_deep_read = Column(Integer, nullable=False, default=0, comment='是否认真阅读 (停留>30秒为1, 否则0)')
    ip_address = Column(String(45), nullable=True, comment='IP地址')
    user_agent = Column(String(500), nullable=True, comment='浏览器UA')
    device_type = Column(String(20), nullable=True, comment='设备类型: mobile/tablet/desktop')
    source = Column(String(50), nullable=True, comment='来源: direct/search/social/link')
    device_fingerprint = Column(String(100), nullable=True, default=None, comment='设备指纹 (用于未登录用户去重)')
    is_logged_in = Column(Integer, nullable=False, default=1, comment='是否登录用户 (1=是, 0=否)')

    # 索引
    __table_args__ = (
        Index('idx_user_time', 'user_id', 'view_time'),  # 用户查询优化
        Index('idx_article_time', 'article_id', 'view_time'),  # 文章查询优化
        Index('idx_stats_time', 'view_time'),  # 统计查询优化
        Index('idx_fingerprint_time', 'device_fingerprint', 'view_time'),  # 未登录用户查询
        {'comment': '文章浏览记录表'}
    )
