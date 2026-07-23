from fastapi import APIRouter, Depends, Form, HTTPException, status, Request
from sqlalchemy.orm import Session
import uvicorn

import app.crud.users as crud
import app.crud.member_invitations as crud_invitations
import app.models.data.users as models
import app.models.schemas.users as schemas
import app.models.schemas.siteconfig as schemasSiteConfig
import app.crud.siteconfig as crudSiteConfig
from app.models.response import ApiResponse
from app.database import get_db
from app.utils.response import success, error
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated, Optional
from app.dependencies.authentication import authenticate_user, create_access_token, get_current_user, \
    get_current_active_user, get_current_user_id, ACCESS_TOKEN_EXPIRE_MINUTES, require_temporary_token, create_temporary_token
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import os
from app.utils.logger import security_logger, api_logger, exception_logger
from app.services.email_service import EmailConfig, send_reset_password_email
from app.utils.auth import verify_password, get_password_hash
from pydantic import BaseModel, Field

router = APIRouter()


@router.post("/login", response_model=ApiResponse[schemas.Token])
async def login_for_access_token(
    request: Request,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    res_data = schemas.Token(access_token=access_token, token_type="bearer")
    # 更新用户登录IP和时间
    await crud.update_user_login_info(db, user.username, request)
    return success('ok', res_data)


@router.get("/users/me/", response_model=ApiResponse[schemas.User])
async def read_users_me(
        current_user: Annotated[schemas.User, Depends(get_current_active_user)],
):
    return success(data=current_user)


# 针对访问者获取临时token
@router.get("/get_temp_token", response_model=ApiResponse[dict])
async def get_temp_token():
    # 可以添加简单的验证（如IP限制、频率限制等）
    jti = os.urandom(16).hex()  # 生成唯一标识
    token = create_temporary_token({"jti": jti})
    return success('ok', {"access_token": token, "token_type": "bearer"})


@router.post("/users/register", response_model=ApiResponse[List[dict]])
async def user_register(request: Request, user:Annotated[schemas.UserRegisterFormData, Form()], temp_user = Depends(require_temporary_token), db: AsyncSession = Depends(get_db)):
    user_in_db = await crud.get_user_in_db(db, user.username)
    if user_in_db:
        return error('用户名已存在', [{'msg': '用户名已存在'}])
    try:
        user = await crud.create_user(db, user, request)
    except HTTPException as e:
        # 使用具体的错误消息
        error_msg = e.detail if e.detail else '创建用户失败'
        return error(error_msg, [{'msg': error_msg}])
    return success('ok', [{"username": user.username}])


# 获取用户资料
@router.get("/users/profile/{username}", response_model=ApiResponse[schemas.UserFullInfo])
async def read_user(username: str, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_full_info(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return success(data=user)


# 访问者获取网站配置信息（公开接口，不需要认证）
@router.get("/blog/config", response_model=ApiResponse[schemasSiteConfig.SiteConfig])
async def get_site_config(db: AsyncSession = Depends(get_db)):
    config = await crudSiteConfig.get_site_config(db)
    if config:
        return success(data=config)
    return success(data=[])


# 获取前端公共配置（包含消息推送设置等）
@router.get("/config/public")
async def get_public_config(db: AsyncSession = Depends(get_db)):
    """
    获取前端需要的公共配置
    包含消息推送方式、WebSocket地址等前端需要的信息
    """
    config = await crudSiteConfig.get_site_config(db)
    if not config:
        # 如果没有配置，返回默认值
        return success(data={
            'websocket_enabled': True,
            'polling_interval': 30,
            'websocket_url': '',
            'message_push_method': 'websocket'
        })

    return success(data={
        'websocket_enabled': config.message_push_method == 'websocket',
        'polling_interval': config.polling_interval,
        'websocket_url': '',  # 前端根据当前域名自动组装
        'message_push_method': config.message_push_method
    })


# 搜索可提及的用户（用于编辑器 Mention 功能）
@router.get("/users/search/{query}", response_model=ApiResponse[List[schemas.User]])
async def search_users_for_mention(query: str, db: AsyncSession = Depends(get_db)):
    """搜索用户，支持按用户名或全名搜索，用于编辑器 @ 提及功能"""
    if not query or len(query.strip()) == 0:
        return success(data=[])
    users = await crud.search_users_for_mention(db, query.strip())
    return success(data=users)


# 更新用户个人资料
@router.put("/users/profile/update", response_model=ApiResponse[schemas.UserFullInfo])
async def update_user_profile(
    profile_data: schemas.UserProfileUpdate,
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """更新当前登录用户的个人资料"""
    updated_user = await crud.update_user_profile(db, current_user.id, profile_data.model_dump(exclude_unset=True))
    if not updated_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return success(data=schemas.UserFullInfo.model_validate(updated_user))


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(min_length=6, max_length=20)
    new_password: str = Field(min_length=6, max_length=20)


@router.post("/users/change-password", response_model=ApiResponse[dict])
async def change_password(
    req: ChangePasswordRequest,
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """当前登录用户修改自己的密码（需验证当前密码）"""
    user = await crud.get_user_by_username(db, current_user.username)
    if not user or not verify_password(req.old_password, user.password):
        return error('当前密码错误', [{'msg': '当前密码错误'}])
    if req.old_password == req.new_password:
        return error('新密码不能与当前密码相同', [{'msg': '新密码不能与当前密码相同'}])
    user.password = get_password_hash(req.new_password)
    user.salt = None
    await db.commit()
    return success(msg="密码修改成功", data={"username": current_user.username})


# 获取用户最近活动
@router.get("/users/{username}/activity", response_model=ApiResponse[dict])
async def get_user_activity(
    username: str,
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """获取用户最近活动记录"""
    # 先获取用户信息
    user = await crud.get_user(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 获取用户活动数据（已过滤掉未发布文章的活动）
    activity_data = await crud.get_user_activities(db, user.id, limit, offset)
    return success(data=activity_data)


# ==================== 用户关注功能 ====================

# 检查用户关注状态
@router.get("/users/{username}/follow-status", response_model=ApiResponse[dict])
async def check_user_follow_status(
    username: str,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """检查当前用户是否关注了目标用户"""
    # 获取目标用户信息
    target_user = await crud.get_user(db, username)
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 检查关注状态
    is_following = await crud.check_follow_user(target_user.id, current_user_id, db)
    return success(data={'is_following': is_following})


# 关注/取消关注用户
@router.post("/users/{username}/follow", response_model=ApiResponse[dict])
async def toggle_user_follow(
    username: str,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """关注或取消关注用户"""
    # 获取目标用户信息
    target_user = await crud.get_user(db, username)
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 检查当前关注状态
    is_following = await crud.check_follow_user(target_user.id, current_user_id, db)

    if is_following:
        # 取消关注
        await crud.unfollow_user(target_user.id, current_user_id, db)
        return success(data={'is_following': False, 'message': '已取消关注'})
    else:
        # 关注
        await crud.follow_user(target_user.id, current_user_id, db)
        return success(data={'is_following': True, 'message': '关注成功'})


# ==================== 密码重置功能 ====================

class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    username: str
    language: Optional[str] = 'zh-CN'


@router.post("/users/reset-password", response_model=ApiResponse[dict])
async def reset_password(
    request_data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    重置用户密码并发送邮件

    功能：
    1. 根据用户名查找用户
    2. 检查用户是否有关联邮箱
    3. 生成新随机密码并更新数据库
    4. 发送包含新密码的邮件到用户邮箱

    返回：
    - 成功：返回成功消息（无论是否发送邮件，都返回成功以避免用户枚举）
    - 失败：返回错误消息
    """
    username = request_data.username
    language = request_data.language or 'zh-CN'

    # 查找用户并重置密码
    success_reset, message, email, new_password = await crud.reset_user_password(db, username)

    if not success_reset:
        # 用户不存在或没有邮箱
        # 为了安全起见，返回统一的错误消息
        return error(msg=message, code=0)

    # 获取邮件配置
    email_settings = await crud_invitations.get_active_email_settings(db)
    if not email_settings:
        # 邮件未配置，返回密码已重置但未发送邮件
        return error(msg='密码已重置，但邮件服务未配置，请联系管理员获取新密码', code=0)

    # 构建邮件配置
    email_config = EmailConfig(
        smtp_host=email_settings.smtp_host,
        smtp_port=email_settings.smtp_port,
        smtp_user=email_settings.smtp_user,
        smtp_pass=email_settings.smtp_pass,
        from_email=email_settings.from_email,
        from_name=email_settings.from_name,
        use_tls=email_settings.use_tls,
        use_ssl=(email_settings.smtp_port == 465)
    )

    # 发送重置密码邮件
    email_sent, error_msg = send_reset_password_email(
        email_config=email_config,
        to_email=email,
        username=username,
        new_password=new_password,
        language=language
    )

    if not email_sent:
        # 邮件发送失败，但密码已重置
        return error(msg=f'密码已重置，但邮件发送失败：{error_msg}，请联系管理员获取新密码', code=0)

    return success(msg='密码重置成功，新密码已发送到您的邮箱，请查收邮件')