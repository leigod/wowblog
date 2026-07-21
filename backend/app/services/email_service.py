"""
邮件服务模块
支持 Gmail, Outlook, QQ Mail 等多种 SMTP
"""
import os
import ssl
from typing import Optional
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from ssl import create_default_context


@dataclass
class EmailConfig:
    """邮件配置"""
    smtp_host: str
    smtp_port: int
    smtp_user: Optional[str] = None
    smtp_pass: Optional[str] = None
    from_email: str = 'noreply@example.com'
    from_name: Optional[str] = None
    use_tls: bool = True
    use_ssl: bool = False  # 新增：是否使用 SSL（端口 465）


class EmailService:
    """邮件服务类"""

    def __init__(self, config: EmailConfig):
        self.config = config

    def _create_connection(self):
        """创建 SMTP 连接"""
        # 端口 465 通常使用 SSL，端口 587 使用 TLS
        if self.config.use_ssl or self.config.smtp_port == 465:
            # SSL 连接（端口 465）
            # 注意：在开发环境中，如果遇到证书验证问题，可以临时禁用证书验证
            # 生产环境建议正确配置 SSL 证书
            context = create_default_context()
            # 临时禁用证书验证以解决开发环境中的证书问题
            # 生产环境应移除此行或正确配置证书
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            server = smtplib.SMTP_SSL(self.config.smtp_host, self.config.smtp_port, context=context)
        elif self.config.use_tls:
            # TLS 连接（端口 587）
            context = create_default_context()
            server = smtplib.SMTP(self.config.smtp_host, self.config.smtp_port)
            server.starttls(context=context)
        else:
            # 普通连接
            server = smtplib.SMTP(self.config.smtp_host, self.config.smtp_port)

        if self.config.smtp_user and self.config.smtp_pass:
            server.login(self.config.smtp_user, self.config.smtp_pass)

        return server

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> tuple[bool, str]:
        """发送邮件
        返回: (是否成功, 错误信息)
        """
        try:
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.config.from_name or 'Blog'} <{self.config.from_email}>"
            msg['To'] = to_email

            # 添加纯文本版本
            if text_content:
                msg.attach(MIMEText(text_content, 'plain', 'utf-8'))

            # 添加 HTML 版本
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))

            # 发送邮件
            with self._create_connection() as server:
                server.send_message(msg)

            return True, ''
        except smtplib.SMTPAuthenticationError as e:
            return False, f'SMTP 认证失败：用户名或密码错误 ({str(e)})'
        except smtplib.SMTPException as e:
            return False, f'SMTP 错误：{str(e)}'
        except Exception as e:
            return False, f'发送邮件失败：{str(e)}'


class EmailTemplateService:
    """邮件模板服务"""

    # 中文重置密码邮件模板
    TEMPLATE_RESET_PASSWORD_ZH_CN = """
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0;">密码重置通知</h1>
        </div>
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
            <p style="color: #333; font-size: 16px; line-height: 1.6;">
                您好 <strong>{username}</strong>，
            </p>
            <p style="color: #666; font-size: 14px; line-height: 1.6; margin: 20px 0;">
                您的密码已成功重置。新密码如下：
            </p>
            <div style="background: #fff; padding: 20px; margin: 20px 0; border-radius: 8px; border: 2px dashed #667eea; text-align: center;">
                <p style="font-size: 24px; font-weight: bold; color: #667eea; margin: 0; letter-spacing: 2px;">{new_password}</p>
            </div>
            <p style="color: #666; font-size: 14px; line-height: 1.6;">
                为了安全起见，建议您在登录后立即修改密码。
            </p>
            <p style="color: #999; font-size: 14px; margin-top: 30px;">
                如果这不是您本人操作，请立即联系管理员。
            </p>
        </div>
    </div>
    """

    # 英文重置密码邮件模板
    TEMPLATE_RESET_PASSWORD_EN_US = """
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0;">Password Reset Notice</h1>
        </div>
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
            <p style="color: #333; font-size: 16px; line-height: 1.6;">
                Hello <strong>{username}</strong>,
            </p>
            <p style="color: #666; font-size: 14px; line-height: 1.6; margin: 20px 0;">
                Your password has been successfully reset. Your new password is:
            </p>
            <div style="background: #fff; padding: 20px; margin: 20px 0; border-radius: 8px; border: 2px dashed #667eea; text-align: center;">
                <p style="font-size: 24px; font-weight: bold; color: #667eea; margin: 0; letter-spacing: 2px;">{new_password}</p>
            </div>
            <p style="color: #666; font-size: 14px; line-height: 1.6;">
                For security reasons, we recommend changing your password immediately after logging in.
            </p>
            <p style="color: #999; font-size: 14px; margin-top: 30px;">
                If this wasn't you, please contact an administrator immediately.
            </p>
        </div>
    </div>
    """

    # 中文邮件模板
    TEMPLATE_ZH_CN = """
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0;">邀请加入团队</h1>
        </div>
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
            <p style="color: #333; font-size: 16px; line-height: 1.6;">
                <strong>{admin_name}</strong> 邀请您加入 <strong>{blog_name}</strong>，担任 <strong>{role}</strong> 角色。
            </p>
            <p style="color: #666; font-size: 14px; line-height: 1.6; margin: 20px 0;">
                作为 {role}，您将能够：{permissions}
            </p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{accept_url}" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">接受邀请</a>
            </div>
            <p style="color: #999; font-size: 14px; text-align: center; margin: 20px 0;">或复制以下链接到浏览器：</p>
            <p style="background: #eee; padding: 10px; border-radius: 5px; word-break: break-all; color: #666; font-size: 13px;">{accept_url}</p>
            <p style="color: #999; font-size: 14px; margin-top: 30px;">
                如果您不想加入，可以忽略此邮件。
            </p>
        </div>
    </div>
    """

    # 英文邮件模板
    TEMPLATE_EN_US = """
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0;">You've Been Invited to Join</h1>
        </div>
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
            <p style="color: #333; font-size: 16px; line-height: 1.6;">
                <strong>{admin_name}</strong> has invited you to join <strong>{blog_name}</strong> as a <strong>{role}</strong>.
            </p>
            <p style="color: #666; font-size: 14px; line-height: 1.6; margin: 20px 0;">
                As an {role}, you'll be able to: {permissions}
            </p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{accept_url}" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">Accept Invitation</a>
            </div>
            <p style="color: #999; font-size: 14px; text-align: center; margin: 20px 0;">Or copy and paste this link into your browser:</p>
            <p style="background: #eee; padding: 10px; border-radius: 5px; word-break: break-all; color: #666; font-size: 13px;">{accept_url}</p>
            <p style="color: #999; font-size: 14px; margin-top: 30px;">
                If you don't want to join this publication, you can safely ignore this email.
            </p>
        </div>
    </div>
    """

    @classmethod
    def render_invitation_email(
        cls,
        blog_name: str,
        admin_name: str,
        role: str,
        permissions: str,
        accept_url: str,
        language: str = 'zh-CN'
    ) -> tuple[str, str]:
        """
        渲染邀请邮件
        返回: (主题, HTML内容)
        """
        if language == 'zh-CN':
            subject = f'邀请加入 {blog_name}'
            template = cls.TEMPLATE_ZH_CN
        else:
            subject = f"You've been invited to join {blog_name}"
            template = cls.TEMPLATE_EN_US

        html_content = template.format(
            blog_name=blog_name,
            admin_name=admin_name,
            role=role,
            permissions=permissions,
            accept_url=accept_url
        )

        return subject, html_content

    @classmethod
    def render_reset_password_email(
        cls,
        username: str,
        new_password: str,
        language: str = 'zh-CN'
    ) -> tuple[str, str]:
        """
        渲染重置密码邮件
        返回: (主题, HTML内容)
        """
        if language == 'zh-CN':
            subject = '密码重置通知'
            template = cls.TEMPLATE_RESET_PASSWORD_ZH_CN
        else:
            subject = 'Password Reset Notice'
            template = cls.TEMPLATE_RESET_PASSWORD_EN_US

        html_content = template.format(
            username=username,
            new_password=new_password
        )

        return subject, html_content


def send_invitation_email(
    email_config: EmailConfig,
    to_email: str,
    blog_name: str,
    admin_name: str,
    role: str,
    permissions: str,
    accept_url: str,
    language: str = 'zh-CN'
) -> tuple[bool, str]:
    """
    发送邀请邮件

    参数:
    - email_config: 邮件配置
    - to_email: 收件人邮箱
    - blog_name: 博客名称
    - admin_name: 管理员名称
    - role: 角色
    - permissions: 权限描述
    - accept_url: 接受邀请链接
    - language: 邮件语言

    返回: (是否成功, 错误信息)
    """
    email_service = EmailService(email_config)
    subject, html_content = EmailTemplateService.render_invitation_email(
        blog_name=blog_name,
        admin_name=admin_name,
        role=role,
        permissions=permissions,
        accept_url=accept_url,
        language=language
    )

    return email_service.send_email(
        to_email=to_email,
        subject=subject,
        html_content=html_content
    )


def send_reset_password_email(
    email_config: EmailConfig,
    to_email: str,
    username: str,
    new_password: str,
    language: str = 'zh-CN'
) -> tuple[bool, str]:
    """
    发送重置密码邮件

    参数:
    - email_config: 邮件配置
    - to_email: 收件人邮箱
    - username: 用户名
    - new_password: 新密码
    - language: 邮件语言

    返回: (是否成功, 错误信息)
    """
    email_service = EmailService(email_config)
    subject, html_content = EmailTemplateService.render_reset_password_email(
        username=username,
        new_password=new_password,
        language=language
    )

    return email_service.send_email(
        to_email=to_email,
        subject=subject,
        html_content=html_content
    )


class ArticleReviewNotificationService:
    """文章审核通知邮件服务"""

    # 中文文章审核通知邮件模板
    TEMPLATE_ARTICLE_REVIEW_ZH_CN = """
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0;">📝 文章待审核</h1>
        </div>
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
            <p style="color: #333; font-size: 16px; line-height: 1.6;">
                您好 <strong>{reviewer_name}</strong>，
            </p>
            <p style="color: #666; font-size: 14px; line-height: 1.6; margin: 20px 0;">
                投稿者 <strong>{author_name}</strong> 创建了一篇新文章，等待您的审核。
            </p>
            <div style="background: #fff; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #667eea;">
                <h2 style="color: #333; font-size: 18px; margin: 0 0 10px 0;">{article_title}</h2>
                <p style="color: #666; font-size: 14px; line-height: 1.6; margin: 10px 0;">
                    {article_summary}
                </p>
                <p style="color: #999; font-size: 13px; margin: 15px 0 0 0;">
                    作者：{author_name} | 提交时间：{submit_time}
                </p>
            </div>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{review_url}" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">前往审核</a>
            </div>
            <p style="color: #999; font-size: 14px; text-align: center; margin: 20px 0;">或复制以下链接到浏览器：</p>
            <p style="background: #eee; padding: 10px; border-radius: 5px; word-break: break-all; color: #666; font-size: 13px;">{review_url}</p>
        </div>
    </div>
    """

    # 英文文章审核通知邮件模板
    TEMPLATE_ARTICLE_REVIEW_EN_US = """
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0;">📝 Article Pending Review</h1>
        </div>
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
            <p style="color: #333; font-size: 16px; line-height: 1.6;">
                Hello <strong>{reviewer_name}</strong>,
            </p>
            <p style="color: #666; font-size: 14px; line-height: 1.6; margin: 20px 0;">
                Contributor <strong>{author_name}</strong> has created a new article that awaits your review.
            </p>
            <div style="background: #fff; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #667eea;">
                <h2 style="color: #333; font-size: 18px; margin: 0 0 10px 0;">{article_title}</h2>
                <p style="color: #666; font-size: 14px; line-height: 1.6; margin: 10px 0;">
                    {article_summary}
                </p>
                <p style="color: #999; font-size: 13px; margin: 15px 0 0 0;">
                    Author: {author_name} | Submitted: {submit_time}
                </p>
            </div>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{review_url}" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">Review Article</a>
            </div>
            <p style="color: #999; font-size: 14px; text-align: center; margin: 20px 0;">Or copy and paste this link into your browser:</p>
            <p style="background: #eee; padding: 10px; border-radius: 5px; word-break: break-all; color: #666; font-size: 13px;">{review_url}</p>
        </div>
    </div>
    """

    @classmethod
    def render_article_review_email(
        cls,
        reviewer_name: str,
        author_name: str,
        article_title: str,
        article_summary: str,
        submit_time: str,
        review_url: str,
        language: str = 'zh-CN'
    ) -> tuple[str, str]:
        """
        渲染文章审核通知邮件
        返回: (主题, HTML内容)
        """
        if language == 'zh-CN':
            subject = f'📝 文章待审核：{article_title}'
            template = cls.TEMPLATE_ARTICLE_REVIEW_ZH_CN
        else:
            subject = f'📝 Article Pending Review: {article_title}'
            template = cls.TEMPLATE_ARTICLE_REVIEW_EN_US

        # 限制摘要长度
        if len(article_summary) > 200:
            article_summary = article_summary[:200] + '...'

        html_content = template.format(
            reviewer_name=reviewer_name,
            author_name=author_name,
            article_title=article_title,
            article_summary=article_summary,
            submit_time=submit_time,
            review_url=review_url
        )

        return subject, html_content


def send_article_review_notification(
    email_config: EmailConfig,
    to_email: str,
    reviewer_name: str,
    author_name: str,
    article_title: str,
    article_summary: str,
    submit_time: str,
    review_url: str,
    language: str = 'zh-CN'
) -> tuple[bool, str]:
    """
    发送文章审核通知邮件

    参数:
    - email_config: 邮件配置
    - to_email: 收件人邮箱
    - reviewer_name: 审核人姓名
    - author_name: 作者姓名
    - article_title: 文章标题
    - article_summary: 文章摘要
    - submit_time: 提交时间
    - review_url: 审核链接
    - language: 邮件语言

    返回: (是否成功, 错误信息)
    """
    email_service = EmailService(email_config)
    subject, html_content = ArticleReviewNotificationService.render_article_review_email(
        reviewer_name=reviewer_name,
        author_name=author_name,
        article_title=article_title,
        article_summary=article_summary,
        submit_time=submit_time,
        review_url=review_url,
        language=language
    )

    return email_service.send_email(
        to_email=to_email,
        subject=subject,
        html_content=html_content
    )


# 常用 SMTP 配置预设
SMTP_PRESETS = {
    'gmail': {
        'smtp_host': 'smtp.gmail.com',
        'smtp_port': 587,
        'use_tls': True,
        'use_ssl': False
    },
    'outlook': {
        'smtp_host': 'smtp.office365.com',
        'smtp_port': 587,
        'use_tls': True,
        'use_ssl': False
    },
    'qq': {
        'smtp_host': 'smtp.qq.com',
        'smtp_port': 465,
        'use_tls': False,
        'use_ssl': True  # QQ 邮箱 465 端口使用 SSL
    },
    '163': {
        'smtp_host': 'smtp.163.com',
        'smtp_port': 465,
        'use_tls': False,
        'use_ssl': True  # 163 邮箱 465 端口使用 SSL
    },
    'yahoo': {
        'smtp_host': 'smtp.mail.yahoo.com',
        'smtp_port': 587,
        'use_tls': True,
        'use_ssl': False
    }
}
