"""
管理员操作日志表

记录 Admin/Editor 在管理后台的写操作（POST/PUT/PATCH/DELETE /api/admin/*）
及登录/登出行为。由审计中间件自动写入（app/middleware/admin_audit.py），
业务代码零侵入。只记"改"不记"看"（业界操作审计惯例）。
"""
from sqlalchemy import Column, Integer, String, Text, Index
from app.database import Base


class AdminLog(Base):
    __tablename__ = 'wb_admin_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, comment='操作人用户ID（登录失败等场景可能为空）')
    username = Column(String(50), comment='操作人用户名（冗余存储，防用户被删后无法追溯）')
    role = Column(String(20), comment='操作人角色')
    action = Column(String(100), comment='动作: login/logout 或 METHOD:path')
    method = Column(String(10), comment='HTTP 方法')
    path = Column(String(200), comment='请求路径（不含域名）')
    detail = Column(Text, comment='请求体 JSON（敏感字段已脱敏为***）')
    status_code = Column(Integer, comment='响应状态码')
    ip = Column(String(45), comment='客户端IP（兼容IPv6）')
    user_agent = Column(String(500), comment='User-Agent')
    createtime = Column(Integer, comment='创建时间戳')

    __table_args__ = (
        Index('idx_al_user_id', 'user_id'),
        Index('idx_al_action', 'action'),
        Index('idx_al_createtime', 'createtime'),
    )
