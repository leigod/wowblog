from sqlalchemy.orm import Session
import app.models.data.users as models
import app.models.schemas.users as schemas
import app.models.data.tags as models_tags
import app.crud.tags as crud_tags
import app.models.schemas.tags as schemas_tags
from sqlalchemy import and_, func, insert, select, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
import os
import time
from fastapi import HTTPException, Request
from app.utils.auth import get_password_hash
from typing import TypedDict


async def get_user(db: AsyncSession, username: str):
    result = await db.execute(
        select(models.User).where(models.User.username == username)
    )
    user = result.scalar_one_or_none()
    if user:
        return schemas.User.model_validate(user)
    return None


async def get_user_by_id(db: AsyncSession, user_id: int):
    """根据用户ID获取用户信息"""
    result = await db.execute(
        select(models.User).where(models.User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if user:
        return schemas.User.model_validate(user)
    return None


async def get_user_by_username(db: AsyncSession, username: str):
    """根据用户名获取用户信息（返回原始模型对象）"""
    result = await db.execute(
        select(models.User).where(models.User.username == username)
    )
    return result.scalar_one_or_none()


async def get_user_full_info(db: AsyncSession, username: str):
    result = await db.execute(
        select(models.User).where(models.User.username == username)
    )
    user = result.scalar_one_or_none()
    if user:
        # 将tech_stack从ID字符串转换为标签名称数组（用于前端显示）
        tag_names = []
        tech_stack_value = getattr(user, 'tech_stack', None)
        if tech_stack_value:
            tag_ids = tech_stack_value.split(',') if tech_stack_value else []
            for tag_id in tag_ids:
                tag = await crud_tags.get_tag(db, int(tag_id))
                if tag:
                    tag_names.append(tag.name)

        # 解析 social_profiles
        social_profiles_dict = None
        social_profiles_value = getattr(user, 'social_profiles', None)
        if social_profiles_value:
            import json
            try:
                social_profiles_dict = json.loads(social_profiles_value)
            except json.JSONDecodeError:
                social_profiles_dict = {}

        # 获取关注者数量
        followers_count = await get_followers_count(user.id, db)

        # 构建返回数据
        result_data = {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'email': user.email,
            'mobile': user.mobile,
            'profile_image': user.profile_image,
            'status': user.status,
            'role': user.role,
            'gender': user.gender,
            'visibility': user.visibility,
            'login_ip': user.login_ip,
            'login_time': user.login_time,
            'join_ip': user.join_ip,
            'createtime': user.createtime,
            'profile_tagline': getattr(user, 'profile_tagline', None),
            'location': getattr(user, 'location', None),
            'birthday': getattr(user, 'birthday', None),
            'school': getattr(user, 'school', None),
            'profile_bio': getattr(user, 'profile_bio', None),
            'tech_stack': tag_names if tag_names else None,
            'available_for': getattr(user, 'available_for', None),
            'social_profiles': social_profiles_dict,
            'followers_count': followers_count
        }

        return schemas.UserFullInfo.model_validate(result_data)
    return None


async def get_user_in_db(db: AsyncSession, username: str):
    # 先尝试按 username 查找
    result = await db.execute(
        select(models.User).where(models.User.username == username)
    )
    user = result.scalar_one_or_none()
    if user:
        return schemas.UserInDB.model_validate(user)

    # 如果没有找到，尝试按 email 查找
    result = await db.execute(
        select(models.User).where(models.User.email == username)
    )
    user = result.scalar_one_or_none()
    if user:
        return schemas.UserInDB.model_validate(user)

    return None


async def check_user_unique(db: AsyncSession, user: schemas.UserCheck):
    if user.username:
        result = await db.execute(
            select(models.User).where(models.User.username == user.username)
        )
        userdata = result.scalar_one_or_none()
        if userdata:
            return 1
    if user.email:
        result = await db.execute(
            select(models.User).where(models.User.email == user.email)
        )
        email_user = result.scalar_one_or_none()
        if email_user:
            return 2
    if user.mobile:
        result = await db.execute(
            select(models.User).where(models.User.mobile == user.mobile)
        )
        mobile_user = result.scalar_one_or_none()
        if mobile_user:
            return 3
    return 'ok'


# 网站用户注册
async def create_user(db: AsyncSession, user: schemas.UserRegister, request: Request):
    # 检查邮箱唯一性
    if user.email:
        email_check = await db.execute(
            select(models.User).where(models.User.email == user.email).limit(1)
        )
        if email_check.first():
            raise HTTPException(status_code=400, detail='该邮箱已被注册')

    # 检查手机号唯一性
    if user.mobile:
        mobile_check = await db.execute(
            select(models.User).where(models.User.mobile == user.mobile).limit(1)
        )
        if mobile_check.first():
            raise HTTPException(status_code=400, detail='该手机号已被注册')

    # 获取系统配置中的默认注册角色
    import app.crud.siteconfig as crud_config
    site_config = await crud_config.get_site_config(db)
    default_role = 'User'  # 默认角色
    if site_config and hasattr(site_config, 'register_role') and site_config.register_role:
        default_role = site_config.register_role

    # 密码使用 bcrypt 哈希（salt 由 bcrypt 内部管理，user.salt 置空）
    encrypted_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        password=encrypted_password,
        salt=None,
        full_name=user.full_name,
        email=user.email or None,
        mobile=user.mobile or None,
        profile_image=user.profile_image,
        role=default_role,
        status='normal',
        join_ip=request.client.host,
        createtime=int(time.time())
    )
    try:
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return schemas.User.model_validate(db_user)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"数据库错误: {str(e)}")


# 更新用户登录信息
async def update_user_login_info(db: AsyncSession, username: str, request: Request):
    result = await db.execute(
        select(models.User).where(models.User.username == username)
    )
    user = result.scalar_one_or_none()
    if user:
        user.login_ip = request.client.host
        user.login_time = int(time.time())
        await db.commit()
        await db.refresh(user)

        # 解析 social_profiles
        social_profiles_dict = None
        social_profiles_value = getattr(user, 'social_profiles', None)
        if social_profiles_value:
            import json
            try:
                social_profiles_dict = json.loads(social_profiles_value)
            except json.JSONDecodeError:
                social_profiles_dict = {}

        # 构建返回数据
        result_data = {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'email': user.email,
            'mobile': user.mobile,
            'profile_image': user.profile_image,
            'status': user.status,
            'role': user.role,
            'gender': user.gender,
            'visibility': user.visibility,
            'login_ip': user.login_ip,
            'login_time': user.login_time,
            'join_ip': user.join_ip,
            'createtime': user.createtime,
            'profile_tagline': getattr(user, 'profile_tagline', None),
            'location': getattr(user, 'location', None),
            'birthday': getattr(user, 'birthday', None),
            'school': getattr(user, 'school', None),
            'profile_bio': getattr(user, 'profile_bio', None),
            'tech_stack': None,  # 登录时不需要返回技术栈
            'available_for': getattr(user, 'available_for', None),
            'social_profiles': social_profiles_dict
        }

        return schemas.UserFullInfo.model_validate(result_data)
    return None



async def get_member_list(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.User).offset(skip).limit(limit).order_by(models.User.id.desc()).where(models.User.role.in_(
            ['Admin', 'Editor', 'Contributor']))
    )
    return [schemas.Member.model_validate(member) for member in result.scalars().all()]


# 管理后台创建成员
async def create_member(member: schemas.MemberCreateBase, db: AsyncSession):
    # 成员默认密码（首次登录后应修改）;可通过环境变量 DEFAULT_MEMBER_PASSWORD 配置
    password = os.getenv("DEFAULT_MEMBER_PASSWORD", "changeme123")
    # 密码使用 bcrypt 哈希（salt 由 bcrypt 内部管理，user.salt 置空）
    encrypted_password = get_password_hash(password)
    db_member = models.User(
        username=member.username,
        password=encrypted_password,
        salt=None,
        role=member.role,
        gender=member.gender if member.gender is not None else 0,
        full_name=member.full_name,
        email=member.email or None,
        mobile=member.mobile or None,
        profile_image=member.profile_image,
        visibility='Private',
        status='normal'
    )
    try:
        db.add(db_member)
        await db.commit()
        await db.refresh(db_member)
        return schemas.Member.model_validate(db_member)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"数据库错误: {str(e)}")



# 修改管理成员禁用状态
async def update_member_status(db: AsyncSession, member_id: int, member: schemas.MemberUpdateStatus):
    result = await db.execute(
        select(models.User).where(models.User.id == member_id)
    )
    member_to_update = result.scalar_one_or_none()
    if member_to_update:
        update_data = member.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(member_to_update, key, value)
        await db.commit()
        await db.refresh(member_to_update)
        return member_to_update
    return None


# 修改管理成员对外公开状态
async def update_member_visibility(db: AsyncSession, member_id: int, member: schemas.MemberUpdateVisibility):
    result = await db.execute(
        select(models.User).where(models.User.id == member_id)
    )
    member_to_update = result.scalar_one_or_none()
    if member_to_update:
        update_data = member.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(member_to_update, key, value)
        await db.commit()
        await db.refresh(member_to_update)
        return member_to_update
    return None


# 删除管理成员
async def delete_member(db: AsyncSession, member_id: int):
    # 保护系统 Owner（用户 ID 为 1）不被删除
    if member_id == 1:
        raise HTTPException(status_code=403, detail="无法删除系统所有者")

    result = await db.execute(
        select(models.User).where(models.User.id == member_id)
    )
    member_to_delete = result.scalar_one_or_none()
    if member_to_delete:
        await db.delete(member_to_delete)
        await db.commit()
        return member_to_delete
    return None


# 更新管理成员
async def update_member(db: AsyncSession, member_id: int, member: schemas.MemberUpdate):
    result = await db.execute(
        select(models.User).where(models.User.id == member_id)
    )
    member_to_update = result.scalar_one_or_none()
    if member_to_update:
        update_data = member.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(member_to_update, key, value)
        await db.commit()
        await db.refresh(member_to_update)
        return member_to_update
    return None


# 获取成员详情
async def get_member_info(member_id: int, db: AsyncSession):
    result = await db.execute(
        select(models.User).where(models.User.id == member_id)
    )
    member_to_update = result.scalar_one_or_none()
    if member_to_update:
        return member_to_update
    return None


# 查询作者
async def search_member(author_id: int, search: str, db: AsyncSession):
    result = await db.execute(
        select(models.User).where(models.User.id != author_id, or_(models.User.full_name.like(f'%{search}%'), models.User.username.like(f'%{search}%')), models.User.status == 'normal', models.User.role.in_(['Admin', 'Editor', 'Contributor']))
    )
    return [schemas.Member.model_validate(item) for item in result.scalars().all()]


# 查询共同创作者
async def search_common_author(search: str, db: AsyncSession):
    result = await db.execute(
        select(models.User).where(models.User.role.in_(['Admin', 'Editor', 'Contributor']), or_(models.User.full_name.like(f'%{search}%'), models.User.username.like(f'%{search}%')), models.User.status == 'normal')
    )
    return [schemas.Member.model_validate(item) for item in result.scalars().all()]


# 搜索可提及的用户（用于编辑器 Mention 功能）
async def search_users_for_mention(db: AsyncSession, query: str, limit: int = 10):
    """搜索用户，支持按用户名或全名搜索，返回正常状态的用户"""
    result = await db.execute(
        select(models.User).where(
            models.User.status == 'normal',
            or_(
                models.User.username.like(f'%{query}%'),
                models.User.full_name.like(f'%{query}%')
            )
        ).limit(limit)
    )
    return [schemas.User.model_validate(item) for item in result.scalars().all()]


# 关注标签
# 同时更新标签关注数
async def follow_tag(tag_id: int, user_id: int, db: AsyncSession):
    # 验证tag是否存在
    tag = await crud_tags.get_tag(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    # 查询是否已经存在这条交互数据，如已存在，若状态为已关注，则更新updatetime，若为未关注则更新状态为已关注，并更新updatetime
    # 若不存在，则添加
    user_action = await db.execute(
        select(models.UserInteractionData).where(
            and_(
                models.UserInteractionData.target_id == tag_id,
                models.UserInteractionData.user_id == user_id,
                models.UserInteractionData.type == "FOLLOW_TAG"
            )
        )
    )
    user_action = user_action.scalars().first()
    
    if user_action:
        # 已存在数据，无论状态是否已关注都更新为已关注
        await db.execute(
            update(models.UserInteractionData).where(
                models.UserInteractionData.id == user_action.id
            ).values(
                status=1,
                updatetime=int(time.time())
            )
        )
    else:
        # 添加用户交互行为
        user_interaction = models.UserInteractionData(
            user_id=user_id,
            target_id=tag_id,
            type="FOLLOW_TAG"
        )
        db.add(user_interaction)
        await db.flush()
        
    # 更新标签关注数
    await db.execute(
        update(models_tags.BlogTag)
        .where(models_tags.BlogTag.id == tag_id)
        .values(follows=func.coalesce(models_tags.BlogTag.follows, 0) + 1)
    )

    await db.commit()
    
    return True


# 取消关注标签
# 同时更新标签关注数
async def unfollow_tag(tag_id: int, user_id: int, db: AsyncSession):
    # 验证tag是否存在
    tag = await crud_tags.get_tag(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    # 更新用户交互行为
    query = (
        update(models.UserInteractionData)
        .where(
            and_(
                models.UserInteractionData.user_id == user_id,
                models.UserInteractionData.target_id == tag_id,
                models.UserInteractionData.type == "FOLLOW_TAG"
            )
        )
        .values(
            status=0,
            updatetime=int(time.time()),
        )
    )
    await db.execute(query)
    await db.execute(
        update(models_tags.BlogTag)
        .where(models_tags.BlogTag.id == tag_id)
        .values(follows=func.coalesce(models_tags.BlogTag.follows, 0) - 1)
    )
    await db.commit()
    return True


# 查询标签关注状态
async def check_follow_tag(tag_id: int, user_id: int, db: AsyncSession):
    # 验证tag是否存在
    tag = await crud_tags.get_tag(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    # 查询用户是否关注了该标签
    query = (
        select(models.UserInteractionData)
        .where(
            and_(
                models.UserInteractionData.user_id == user_id,
                models.UserInteractionData.target_id == tag_id,
                models.UserInteractionData.type == "FOLLOW_TAG"
            )
        )
    )
    result = await db.execute(query)
    result = result.scalars().first()
    if result:
        if result.status == 1:
            return True
        return False
    return False


# ==================== 用户关注功能 ====================

# 关注用户
async def follow_user(target_user_id: int, current_user_id: int, db: AsyncSession):
    """关注用户"""
    # 验证目标用户是否存在
    target_user = await get_user_by_id(db, target_user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 不能关注自己
    if target_user_id == current_user_id:
        raise HTTPException(status_code=400, detail="不能关注自己")

    # 查询是否已经存在这条交互数据
    user_action = await db.execute(
        select(models.UserInteractionData).where(
            and_(
                models.UserInteractionData.target_id == target_user_id,
                models.UserInteractionData.user_id == current_user_id,
                models.UserInteractionData.type == "FOLLOW_USER"
            )
        )
    )
    user_action = user_action.scalars().first()

    if user_action:
        # 已存在数据，更新为已关注
        if user_action.status == 1:
            return True  # 已经关注了
        await db.execute(
            update(models.UserInteractionData).where(
                models.UserInteractionData.id == user_action.id
            ).values(
                status=1,
                updatetime=int(time.time())
            )
        )
    else:
        # 添加关注记录
        user_interaction = models.UserInteractionData(
            user_id=current_user_id,
            target_id=target_user_id,
            type="FOLLOW_USER"
        )
        db.add(user_interaction)
        await db.flush()

    await db.commit()
    return True


# 取消关注用户
async def unfollow_user(target_user_id: int, current_user_id: int, db: AsyncSession):
    """取消关注用户"""
    # 验证目标用户是否存在
    target_user = await get_user_by_id(db, target_user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 查询关注记录
    user_action = await db.execute(
        select(models.UserInteractionData).where(
            and_(
                models.UserInteractionData.target_id == target_user_id,
                models.UserInteractionData.user_id == current_user_id,
                models.UserInteractionData.type == "FOLLOW_USER"
            )
        )
    )
    user_action = user_action.scalars().first()

    if user_action:
        # 更新为未关注状态
        await db.execute(
            update(models.UserInteractionData).where(
                models.UserInteractionData.id == user_action.id
            ).values(
                status=0,
                updatetime=int(time.time())
            )
        )
    else:
        # 没有关注记录，视为已取消
        return True

    await db.commit()
    return True


# 检查是否关注用户
async def check_follow_user(target_user_id: int, current_user_id: int, db: AsyncSession):
    """检查当前用户是否关注了目标用户"""
    query = (
        select(models.UserInteractionData)
        .where(
            and_(
                models.UserInteractionData.target_id == target_user_id,
                models.UserInteractionData.user_id == current_user_id,
                models.UserInteractionData.type == "FOLLOW_USER"
            )
        )
    )
    result = await db.execute(query)
    result = result.scalars().first()
    if result:
        if result.status == 1:
            return True
        return False
    return False


async def get_followers_count(user_id: int, db: AsyncSession) -> int:
    """获取用户的关注者数量"""
    query = (
        select(func.count(models.UserInteractionData.id))
        .where(
            and_(
                models.UserInteractionData.target_id == user_id,
                models.UserInteractionData.type == "FOLLOW_USER",
                models.UserInteractionData.status == 1
            )
        )
    )
    result = await db.execute(query)
    return result.scalar() or 0


# 更新用户个人资料
async def update_user_profile(db: AsyncSession, user_id: int, profile_data: dict):
    result = await db.execute(
        select(models.User).where(models.User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        return None

    # 更新允许的字段
    update_data = {}
    if 'full_name' in profile_data and profile_data['full_name'] is not None:
        update_data['full_name'] = profile_data['full_name']
    if 'profile_tagline' in profile_data:
        update_data['profile_tagline'] = profile_data['profile_tagline']
    if 'email' in profile_data:
        update_data['email'] = profile_data['email']
    if 'mobile' in profile_data:
        update_data['mobile'] = profile_data['mobile']
    if 'location' in profile_data:
        update_data['location'] = profile_data['location']
    if 'gender' in profile_data:
        update_data['gender'] = profile_data['gender']
    if 'birthday' in profile_data:
        # 将日期字符串转换为时间戳
        if profile_data['birthday']:
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(profile_data['birthday'].replace('Z', '+00:00'))
                update_data['birthday'] = int(dt.timestamp())
            except (ValueError, AttributeError):
                update_data['birthday'] = None
        else:
            update_data['birthday'] = None
    if 'school' in profile_data:
        update_data['school'] = profile_data['school']
    if 'profile_bio' in profile_data:
        update_data['profile_bio'] = profile_data['profile_bio']
    if 'tech_stack' in profile_data:
        # 处理技术栈标签：验重或创建，存储为逗号分隔的标签ID
        import pypinyin
        import re
        if profile_data['tech_stack'] and isinstance(profile_data['tech_stack'], list):
            tag_ids = []
            for tag_name in profile_data['tech_stack']:
                tag_name = tag_name.strip()
                if not tag_name:
                    continue
                # 检查标签是否已存在
                tag = await crud_tags.get_tag_by_name(db, tag_name)
                if not tag:
                    # 创建新标签
                    tag_slug = "_".join(pypinyin.lazy_pinyin(tag_name))
                    tag_slug = tag_slug.replace(" ", "_").lower()
                    tag_slug = tag_slug.replace("/", "_")
                    tag_slug = re.sub(r"[^a-zA-Z0-9_-]", "", tag_slug)
                    tag_data = schemas_tags.BlogTagCreate(
                        name=tag_name,
                        tag_desc=tag_name,
                        slug=tag_slug,
                        type="user",
                        image=None,
                        status="normal"
                    )
                    tag = await crud_tags.create_tag(db, tag_data)
                tag_ids.append(str(tag.id))
            update_data['tech_stack'] = ','.join(tag_ids) if tag_ids else None
        elif not profile_data['tech_stack']:
            update_data['tech_stack'] = None
    if 'available_for' in profile_data:
        update_data['available_for'] = profile_data['available_for']
    if 'social_profiles' in profile_data:
        # 将字典转换为 JSON 字符串存储，过滤掉空值
        import json
        if profile_data['social_profiles'] and isinstance(profile_data['social_profiles'], dict):
            # 过滤掉空字符串和None的值
            filtered_profiles = {k: v for k, v in profile_data['social_profiles'].items() if v}
            update_data['social_profiles'] = json.dumps(filtered_profiles) if filtered_profiles else None
        else:
            update_data['social_profiles'] = None
    if 'profile_image' in profile_data:
        update_data['profile_image'] = profile_data['profile_image']

    if update_data:
        for key, value in update_data.items():
            setattr(user, key, value)
        await db.commit()
        await db.refresh(user)

    # 将tech_stack从ID字符串转换为标签名称数组（用于前端显示）
    tag_names = []
    tech_stack_value = getattr(user, 'tech_stack', None)
    if tech_stack_value:
        tag_ids = tech_stack_value.split(',') if tech_stack_value else []
        for tag_id in tag_ids:
            tag = await crud_tags.get_tag(db, int(tag_id))
            if tag:
                tag_names.append(tag.name)

    # 创建返回数据，将social_profiles也解析为dict
    result_data = {
        'id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'email': user.email,
        'mobile': user.mobile,
        'profile_image': user.profile_image,
        'status': user.status,
        'role': user.role,
        'gender': user.gender,
        'visibility': user.visibility,
        'login_ip': user.login_ip,
        'login_time': user.login_time,
        'join_ip': user.join_ip,
        'createtime': user.createtime,
        'profile_tagline': getattr(user, 'profile_tagline', None),
        'location': getattr(user, 'location', None),
        'birthday': getattr(user, 'birthday', None),
        'school': getattr(user, 'school', None),
        'profile_bio': getattr(user, 'profile_bio', None),
        'tech_stack': tag_names if tag_names else None,
        'available_for': getattr(user, 'available_for', None),
        'social_profiles': None
    }

    # 解析 social_profiles
    social_profiles_value = getattr(user, 'social_profiles', None)
    if social_profiles_value:
        import json
        try:
            result_data['social_profiles'] = json.loads(social_profiles_value)
        except json.JSONDecodeError:
            result_data['social_profiles'] = {}

    return schemas.UserFullInfo.model_validate(result_data)


# 获取用户最近活动
async def get_user_activities(db: AsyncSession, user_id: int, limit: int = 10, offset: int = 0):
    """获取用户最近的互动活动记录"""
    # 导入模型
    import app.models.data.articles as models_articles
    import app.models.data.comments as models_comments

    # 与文章相关的活动类型
    article_related_types = ['LIKE', 'BOOKMARK', 'VIEW', 'COMMENT', 'ARTICLE']

    # 首先获取所有有效活动
    result = await db.execute(
        select(models.UserInteractionData)
        .where(models.UserInteractionData.user_id == user_id)
        .where(models.UserInteractionData.status == 1)  # 只返回有效的活动
        .order_by(models.UserInteractionData.updatetime.desc())
    )
    all_activities = result.scalars().all()

    # 过滤并格式化活动
    formatted_activities = []
    for activity in all_activities:
        activity_type = activity.type
        target_id = activity.target_id

        # 根据活动类型处理
        if activity_type in ['LIKE', 'BOOKMARK', 'VIEW']:
            # 检查文章状态
            article_result = await db.execute(
                select(models_articles.BlogArticle)
                .where(models_articles.BlogArticle.id == target_id)
                .where(models_articles.BlogArticle.status == 'published')  # 只要已发布的文章
            )
            article = article_result.scalar_one_or_none()
            if article:
                formatted_activities.append({
                    'type': activity_type.lower(),  # 转换为小写
                    'article_id': article.id,
                    'article_title': article.title,
                    'article_slug': article.slug,
                    'action': f"{activity_type.lower()}ed article",
                    'time': activity.updatetime
                })

        elif activity_type == 'COMMENT':
            # 检查文章状态
            comment_result = await db.execute(
                select(models_comments.Comment, models_articles.BlogArticle)
                .join(models_articles.BlogArticle, models_comments.Comment.subject_id == models_articles.BlogArticle.id)
                .where(models_comments.Comment.id == target_id)
                .where(models_articles.BlogArticle.status == 'published')
            )
            comment_with_article = comment_result.first()
            if comment_with_article:
                comment, article = comment_with_article
                formatted_activities.append({
                    'type': 'comment',
                    'article_id': article.id,
                    'article_title': article.title,
                    'article_slug': article.slug,
                    'comment_content': comment.content[:100] + '...' if len(comment.content) > 100 else comment.content,
                    'action': 'commented on article',
                    'time': activity.updatetime
                })

        elif activity_type == 'ARTICLE':
            # 检查文章状态（只显示已发布的文章）
            article_result = await db.execute(
                select(models_articles.BlogArticle)
                .where(models_articles.BlogArticle.id == target_id)
                .where(models_articles.BlogArticle.status == 'published')
            )
            article = article_result.scalar_one_or_none()
            if article:
                formatted_activities.append({
                    'type': 'article',
                    'article_id': article.id,
                    'title': article.title,
                    'slug': article.slug,
                    'action': 'published article',
                    'time': activity.updatetime
                })

        elif activity_type in ['FOLLOW_USER', 'FOLLOW_TAG']:
            # 关注类的活动不显示在活动记录中（或者可以单独处理）
            pass

    # 应用分页
    total = len(formatted_activities)
    paginated_activities = formatted_activities[offset:offset + limit]

    return {
        'activities': paginated_activities,
        'total': total,
        'has_more': offset + limit < total
    }


# ==================== 用户管理功能（管理员） ====================

async def get_user_list(db: AsyncSession, skip: int = 0, limit: int = 20, status: str | None = None, keyword: str | None = None):
    """获取用户列表（支持状态筛选和关键词搜索）"""
    # 构建查询条件
    conditions = []
    if status and status in ['normal', 'disabled', 'block']:
        conditions.append(models.User.status == status)
    if keyword:
        search_pattern = f'%{keyword}%'
        conditions.append(
            or_(
                models.User.username.like(search_pattern),
                models.User.full_name.like(search_pattern),
                models.User.email.like(search_pattern)
            )
        )

    # 执行查询
    query = select(models.User)
    if conditions:
        query = query.where(and_(*conditions))

    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # 获取分页数据
    result = await db.execute(
        query.offset(skip).limit(limit).order_by(models.User.createtime.desc())
    )

    return result.scalars().all(), total


async def get_users_by_roles(db: AsyncSession, roles: list[str]):
    """根据角色列表获取用户"""
    query = select(models.User).where(
        and_(
            models.User.role.in_(roles),
            models.User.status == 'normal'
        )
    )
    result = await db.execute(query)
    return result.scalars().all()


async def update_user_status_field(db: AsyncSession, user_id: int, status: str):
    """更新用户状态"""
    result = await db.execute(
        select(models.User).where(models.User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if user:
        user.status = status
        await db.commit()
        await db.refresh(user)
        return user
    return None


async def update_user_role_field(db: AsyncSession, user_id: int, role: str):
    """更新用户角色"""
    result = await db.execute(
        select(models.User).where(models.User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if user:
        user.role = role
        await db.commit()
        await db.refresh(user)
        return user
    return None


async def delete_user_by_id(db: AsyncSession, user_id: int):
    """根据用户ID删除用户"""
    result = await db.execute(
        select(models.User).where(models.User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if user:
        await db.delete(user)
        await db.commit()
        return True
    return False


async def reset_user_password(db: AsyncSession, username: str) -> tuple[bool, str, str, str]:
    """
    重置用户密码并返回新密码

    参数:
    - username: 用户名

    返回: (是否成功, 消息, 邮箱, 新密码)
    """
    # 查找用户
    result = await db.execute(
        select(models.User).where(models.User.username == username)
    )
    user = result.scalar_one_or_none()

    if not user:
        return False, '用户不存在', None, None

    # 检查用户是否有邮箱
    if not user.email:
        return False, '该用户未关联邮箱，无法重置密码', None, None

    # 生成随机密码（8位，包含字母和数字）
    import random
    import string
    characters = string.ascii_letters + string.digits
    new_password = ''.join(random.choice(characters) for _ in range(8))

    # 密码使用 bcrypt 哈希（salt 由 bcrypt 内部管理，user.salt 置空）
    encrypted_password = get_password_hash(new_password)

    # 更新用户密码
    user.password = encrypted_password
    user.salt = None

    try:
        await db.commit()
        await db.refresh(user)
        return True, '密码重置成功', user.email, new_password
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"数据库错误: {str(e)}")

