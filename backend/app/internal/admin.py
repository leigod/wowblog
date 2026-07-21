from fastapi import APIRouter, Depends, HTTPException, Form, Path, Body

from app.models.response import ApiResponse
from app.database import get_db
from app.utils.response import success, error
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Annotated, Optional
import app.models.schemas.navs as schemasNavs
import app.models.schemas.pages as schemasPages
import app.models.schemas.series as schemasSeries
import app.models.schemas.category as schemasCategory
import app.models.schemas.users as schemasUsers
import app.models.schemas.tags as schemasTags
import app.models.schemas.siteconfig as schemasSiteConfig
import app.models.data.articles as modelsArticles
import app.models.data.comments as modelsComments
import app.crud.siteconfig as crudSiteConfig
import app.crud.navs as crudNavs
import app.crud.pages as crudPages
import app.crud.series as crudSeries
import app.crud.category as crudCategory
import app.crud.users as crudUsers
import app.crud.tags as crudTags
from fastapi.responses import JSONResponse
import re

router = APIRouter()


###########
# 导航管理
###########

# 导航列表
@router.get('/navs/list', response_model=ApiResponse[List[schemasNavs.BlogNav]])
async def get_nav_list(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    navlist = await crudNavs.get_navs(db, skip=skip, limit=limit)
    return success(data=navlist)


# 添加导航
@router.post('/navs/add', response_model=ApiResponse[schemasNavs.BlogNav])
async def add_nav(
        label: Annotated[str, Form()],
        type: Annotated[str, Form()],
        value: Annotated[str, Form()],
        db: AsyncSession = Depends(get_db)):
    nav_data = schemasNavs.BlogNavCreate(label=label, nav_type='user', type=type, value=value, sort=0, status=1)
    new_nav = await crudNavs.create_nav(db, nav_data)
    return success(data=new_nav)


# 修改导航
@router.post('/navs/edit/{nav_id}', response_model=ApiResponse[schemasNavs.BlogNav])
async def update_nav(
        nav_id: Annotated[int, Path()],
        label: Annotated[str, Form()],
        type: Annotated[str, Form()],
        value: Annotated[str, Form()],
        db: AsyncSession = Depends(get_db)):
    nav_data = schemasNavs.BlogNavUpdate(label=label, type=type, value=value)
    new_nav = await crudNavs.update_nav(db, nav_id, nav_data)
    if new_nav:
        return success(data=new_nav)
    return error(data={'error': '导航不存在或已被删除'})


# 修改导航排序
@router.post('/navs/sort/{nav_id}', response_model=ApiResponse[schemasNavs.BlogNav])
async def update_nav_sort(
        nav_id: Annotated[int, Path()],
        sort: Annotated[int, Form()],
        db: AsyncSession = Depends(get_db)):
    nav_data = schemasNavs.BlogNavUpdateSort(sort=sort)
    new_nav = await crudNavs.update_nav_sort(db, nav_id, nav_data)
    if new_nav:
        return success(data=new_nav)
    return error(data={'error': '导航不存在或已被删除'})


# 批量修改导航排序
@router.post('/navs/sortbatch', response_model=ApiResponse[List[schemasNavs.BlogNav]])
async def batch_update_navs_sort(
        nav_ids: Annotated[str, Form(..., description="导航ID列表，格式如：4,2,1")],
        db: AsyncSession = Depends(get_db)):
    try:
        # 将字符串转换为List[int]
        nav_ids_list = [int(id_str.strip()) for id_str in nav_ids.split(',')]
        # 调用CRUD方法
        updated_navs = await crudNavs.update_navs_sort(db, nav_ids_list)
        if updated_navs:
            return success(data=updated_navs)
        return error(msg="未找到任何导航记录")
    except ValueError:
        return error(msg="无效的ID格式，请确保输入为逗号分隔的整数，如：4,2,1")


# 修改导航状态
@router.post('/navs/status/{nav_id}', response_model=ApiResponse[schemasNavs.BlogNav])
async def update_nav_status(
        nav_id: Annotated[int, Path()],
        status: Annotated[int, Form()],
        db: AsyncSession = Depends(get_db)):
    if status not in [0, 1]:
        return error(data={'error': '状态值错误'})
    nav_data = schemasNavs.BlogNavUpdateStatus(status=status)
    new_nav = await crudNavs.update_nav_status(db, nav_id, nav_data)
    if new_nav:
        return success(data=new_nav)
    return error(data={'error': '导航不存在或已被删除'})


# 删除导航
@router.delete('/navs/delete/{nav_id}', response_model=ApiResponse[schemasNavs.BlogNav])
async def delete_nav(
        nav_id: Annotated[int, Path()],
        db: AsyncSession = Depends(get_db)):
    new_nav = await crudNavs.delete_nav(db, nav_id)
    if new_nav:
        return success(msg='删除成功', data=new_nav)
    return error(data={'error': '导航不存在或已被删除'})


###########
# 页面管理
###########

# 获取页面列表
@router.get('/page/list', response_model=ApiResponse[List[schemasPages.BlogPage]])
async def get_page_list(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    pagelist = await crudPages.get_pages(db, skip=skip, limit=limit)
    return success(data=pagelist)


# 新建页面
@router.post('/page/add', response_model=ApiResponse[schemasPages.BlogPage])
async def add_page(pageitem: schemasPages.BlogPageCreate, db: AsyncSession = Depends(get_db)):
    page_data = schemasPages.BlogPageCreate(
        title=pageitem.title,
        content=pageitem.content,
        slug=pageitem.slug
    )
    new_page = await crudPages.create_page(db, page_data)
    return success(data=new_page)


# 修改页面
@router.post('/page/edit/{page_id}', response_model=ApiResponse[schemasPages.BlogPage])
async def update_page(
        page_id: Annotated[int, Path()],
        pageitem: schemasPages.BlogPageUpdate,
        db: AsyncSession = Depends(get_db)):
    page_data = schemasPages.BlogPageUpdate(
        title=pageitem.title,
        content=pageitem.content,
        slug=pageitem.slug,
        image=pageitem.image,
        seo_desc=pageitem.seo_desc
    )
    new_page = await crudPages.update_page(db, page_id, page_data)
    if new_page:
        return success(data=new_page)
    return error(data={'error': '页面不存在或已被删除'})


# 修改页面状态
@router.post('/page/status/{page_id}', response_model=ApiResponse[schemasPages.BlogPage])
async def update_page_status(
        page_id: Annotated[int, Path()],
        status: Annotated[str, Form()],
        db: AsyncSession = Depends(get_db)):
    if status not in ['normal', 'hidden']:
        return error(data={'error': '状态值错误'})
    page_data = schemasPages.BlogPageUpdateStatus(status=status)
    new_page = await crudPages.update_page_status(db, page_id, page_data)
    if new_page:
        return success(data=new_page)
    return error(data={'error': '页面不存在或已被删除'})


# 删除导航
@router.delete('/page/delete/{page_id}', response_model=ApiResponse[schemasPages.BlogPage])
async def delete_nav(
        page_id: Annotated[int, Path()],
        db: AsyncSession = Depends(get_db)):
    new_page = await crudPages.delete_page(db, page_id)
    if new_page:
        return success(msg='删除成功', data=new_page)
    return error(data={'error': '页面不存在或已被删除'})


# 获取页面详情
@router.get('/page/detail/{page_id}', response_model=ApiResponse[schemasPages.BlogPage])
async def get_page_detail(
        page_id: Annotated[int, Path()],
        db: AsyncSession = Depends(get_db)):
    page = await crudPages.get_page(db, page_id)
    if page:
        return success(data=page)
    return error(data={'error': '页面不存在或已被删除'})


###########
# 系列管理
###########

# 获取系列列表
@router.get('/series/list', response_model=ApiResponse[List[schemasSeries.BlogSeries]])
async def get_series_list(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    serieslist = await crudSeries.get_series_list(db, skip=skip, limit=limit)
    return success(data=serieslist)


# 新建系列
@router.post('/series/add', response_model=ApiResponse[schemasSeries.BlogSeries])
async def add_series(seriesitem: schemasSeries.BlogSeriesCreate, db: AsyncSession = Depends(get_db)):
    if seriesitem.articles_order not in ['asc', 'desc']:
        return error(data={'error': '系列文章排序值错误'})
    series_data = schemasSeries.BlogSeriesCreate(
        name=seriesitem.name,
        series_desc=seriesitem.series_desc,
        articles_order=seriesitem.articles_order,
        image=seriesitem.image,
        slug=seriesitem.slug
    )
    new_series = await crudSeries.create_series(db, series_data)
    return success(data=new_series)


# 修改系列
@router.post('/series/edit/{series_id}', response_model=ApiResponse[schemasSeries.BlogSeries])
async def update_series(
        series_id: Annotated[int, Path()],
        seriesitem: schemasSeries.BlogSeriesUpdate,
        db: AsyncSession = Depends(get_db)):
    if seriesitem.articles_order not in ['asc', 'desc']:
        return error(data={'error': '系列文章排序值错误'})
    series_data = schemasSeries.BlogSeriesUpdate(
        name=seriesitem.name,
        series_desc=seriesitem.series_desc,
        articles_order=seriesitem.articles_order,
        image=seriesitem.image,
        slug=seriesitem.slug
    )
    new_series = await crudSeries.update_series(db, series_id, series_data)
    if new_series:
        return success(data=new_series)
    return error(data={'error': '系列不存在或已被删除'})


# 批量修改系列排序
@router.post('/series/sortbatch', response_model=ApiResponse[List[schemasSeries.BlogSeries]])
async def batch_update_series_sort(
        series_ids: Annotated[str, Form(..., description="系列ID列表，格式如：4,2,1")],
        db: AsyncSession = Depends(get_db)):
    try:
        # 将字符串转换为List[int]
        series_ids_list = [int(id_str.strip()) for id_str in series_ids.split(',')]
        # 调用CRUD方法
        updated_series = await crudSeries.update_series_sort(db, series_ids_list)
        if updated_series:
            return success(data=updated_series)
        return error(msg="未找到任何系列记录")
    except ValueError:
        return error(msg="无效的ID格式，请确保输入为逗号分隔的整数，如：4,2,1")

# 删除系列
@router.delete('/series/delete/{series_id}', response_model=ApiResponse[schemasSeries.BlogSeries])
async def delete_series(
        series_id: Annotated[int, Path()],
        db: AsyncSession = Depends(get_db)):
    new_series = await crudSeries.delete_series(db, series_id)
    if new_series:
        return success(msg='删除成功', data=new_series)
    return error(data={'error': '系列不存在或已被删除'})


# 获取系列详情
@router.get('/series/detail/{series_id}', response_model=ApiResponse[schemasSeries.BlogSeries])
async def get_series_detail(
        series_id: Annotated[int, Path()],
        db: AsyncSession = Depends(get_db)):
    series = await crudSeries.get_series(db, series_id)
    if series:
        return success(data=series)
    return error(data={'error': '系列不存在或已被删除'})


###########
# 分类管理
###########

# 获取分类列表
@router.get('/category/list', response_model=ApiResponse[List[schemasCategory.BlogCategory]])
async def get_category_list(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    categorylist = await crudCategory.get_category_list(db, skip=skip, limit=limit)
    return success(data=categorylist)


# 新建分类
@router.post('/category/add', response_model=ApiResponse[schemasCategory.BlogCategory])
async def add_category(categoryitem: schemasCategory.BlogCategoryCreate, db: AsyncSession = Depends(get_db)):
    if categoryitem.articles_order not in ['id desc', 'views desc', 'pubtime asc']:
        return error(data={'error': '分类文章排序值错误'})
    category_data = schemasCategory.BlogCategoryCreate(
        name=categoryitem.name,
        pid=categoryitem.pid,
        cat_desc=categoryitem.cat_desc,
        articles_order=categoryitem.articles_order,
        image=categoryitem.image,
        slug=categoryitem.slug
    )
    new_category = await crudCategory.create_category(db, category_data)
    return success(data=new_category)


# 修改分类
@router.post('/category/edit/{category_id}', response_model=ApiResponse[schemasCategory.BlogCategory])
async def update_category(
        category_id: Annotated[int, Path()],
        categoryitem: schemasCategory.BlogCategoryUpdate,
        db: AsyncSession = Depends(get_db)):
    if categoryitem.articles_order not in ['id desc', 'views desc', 'pubtime asc']:
        return error(data={'error': '分类文章排序值错误'})
    category_data = schemasCategory.BlogCategoryUpdate(
        name=categoryitem.name,
        pid=categoryitem.pid,
        cat_desc=categoryitem.cat_desc,
        articles_order=categoryitem.articles_order,
        image=categoryitem.image,
        slug=categoryitem.slug
    )
    new_category = await crudCategory.update_category(db, category_id, category_data)
    if new_category:
        return success(data=new_category)
    return error(data={'error': '分类不存在或已被删除'})


# 删除分类
@router.delete('/category/delete/{category_id}', response_model=ApiResponse[schemasCategory.BlogCategory])
async def delete_category(
        category_id: Annotated[int, Path()],
        db: AsyncSession = Depends(get_db)):
    new_category = await crudCategory.delete_category(db, category_id)
    if new_category:
        return success(msg='删除成功', data=new_category)
    return error(data={'error': '分类不存在或已被删除'})


# 获取分类详情
@router.get('/category/detail/{category_id}', response_model=ApiResponse[schemasCategory.BlogCategory])
async def get_category_detail(
        category_id: Annotated[int, Path()],
        db: AsyncSession = Depends(get_db)):
    category = await crudCategory.get_category(db, category_id)
    if category:
        return success(data=category)
    return error(data={'error': '分类不存在或已被删除'})


# 修改分类排序
@router.post('/category/sort/{category_id}', response_model=ApiResponse[schemasCategory.BlogCategory])
async def update_category_sort(
        category_id: Annotated[int, Path()],
        pid: Annotated[int, Form()],
        sort: Annotated[int, Form()],
        db: AsyncSession = Depends(get_db)):
    new_category = await crudCategory.update_category_sort(db, category_id, pid, sort)
    if new_category:
        return success(data=new_category)
    return error(data={'error': '分类不存在或已被删除'})


# 修改分类下文章排序
@router.post('/category/articles/sort/{category_id}', response_model=ApiResponse[schemasCategory.BlogCategory])
async def update_category_articles_sort(
        category_id: Annotated[int, Path()],
        category: schemasCategory.BlogCategoryUpdateArticlesOrder,
        db: AsyncSession = Depends(get_db)):
    if category.articles_order not in ['id desc', 'views desc', 'pubtime asc']:
        return error(data={'error': '分类文章排序值错误'})
    new_category = await crudCategory.update_category_articles_sort(db, category_id, category)
    if new_category:
        return success(data=new_category)
    return error(data={'error': '分类不存在或已被删除'})


###########
# 成员管理
###########

# 获取成员列表
@router.get("/members/list", response_model=ApiResponse[List[schemasUsers.Member]])
async def get_member_list(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    memberlist = await crudUsers.get_member_list(db, skip=skip, limit=limit)
    return success(data=memberlist)


# 创建成员
@router.post('/members/add', response_model=ApiResponse[schemasUsers.Member])
async def add_member(member: schemasUsers.MemberCreateBase, db: AsyncSession = Depends(get_db)):
    if member.email == '':
        member.email = None
    else:
        pattern = r'^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$'
        if not re.match(pattern, member.email):
            return error(msg='邮箱格式错误', data={'error': '邮箱格式错误', 'field': 'email', 'value': member.email})
    if member.mobile == '':
        member.mobile = None
    else:
        pattern = r'^1[3-9]\d{9}$'
        if not re.match(pattern, member.mobile):
            return error(msg='手机号格式错误')
    checkUser = schemasUsers.UserCheck(username=member.username, email=member.email, mobile=member.mobile)
    check_result = await crudUsers.check_user_unique(db, checkUser)
    if check_result == 1:
        return error(msg='用户名已存在')
    if check_result == 2:
        return error(msg='邮箱已存在')
    if check_result == 3:
        return error(msg='手机号已存在')
    new_member = await crudUsers.create_member(member, db)
    if new_member:
        return success(data=new_member)
    return error(data={'error': '创建失败'})


# 更新管理成员禁用状态
@router.post('/members/status/{member_id}', response_model=ApiResponse[schemasUsers.Member])
async def update_member_status(
        member_id: Annotated[int, Path()],
        status: Annotated[str, Form()],
        db: AsyncSession = Depends(get_db)):
    if status not in ['normal', 'block']:
        return error(data={'error': '状态值错误'})
    member_data = schemasUsers.MemberUpdateStatus(status=status)
    new_member = await crudUsers.update_member_status(db, member_id, member_data)
    if new_member:
        return success(data=new_member)
    return error(data={'error': '成员不存在或已被删除'})


# 更新管理成员对外公开状态
@router.post('/members/visible/{member_id}', response_model=ApiResponse[schemasUsers.Member])
async def update_member_visible(
        member_id: Annotated[int, Path()],
        visible: Annotated[str, Form()],
        db: AsyncSession = Depends(get_db)):
    if visible not in ['Public', 'Private']:
        return error(data={'error': '公开隐私状态传值错误'})
    member_data = schemasUsers.MemberUpdateVisibility(visibility=visible)
    new_member = await crudUsers.update_member_visibility(db, member_id, member_data)
    if new_member:
        return success(data=new_member)
    return error(data={'error': '成员不存在或已被删除'})


# 删除管理成员
@router.delete('/members/delete/{member_id}', response_model=ApiResponse[schemasUsers.Member])
async def delete_member(
        member_id: Annotated[int, Path()],
        db: AsyncSession = Depends(get_db)):
    new_member = await crudUsers.delete_member(db, member_id)
    if new_member:
        return success(msg='删除成功', data=new_member)
    return error(data={'error': '成员不存在或已被删除'})


# 更新管理成员
@router.post('/members/update/{member_id}', response_model=ApiResponse[schemasUsers.Member])
async def update_member(
        member_id: Annotated[int, Path()],
        member: schemasUsers.MemberUpdate,
        db: AsyncSession = Depends(get_db)):
    if member.email == '':
        member.email = None
    else:
        pattern = r'^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$'
        if not re.match(pattern, member.email):
            return error(msg='邮箱格式错误', data={'error': '邮箱格式错误', 'field': 'email', 'value': member.email})
    if member.mobile == '':
        member.mobile = None
    else:
        pattern = r'^1[3-9]\d{9}$'
        if not re.match(pattern, member.mobile):
            return error(msg='手机号格式错误')
    user = await crudUsers.get_member_info(member_id, db)
    if user is None:
        return error(msg='用户不存在')
    if user.username != member.username:
        check = await crudUsers.check_user_unique(db, schemasUsers.UserCheck(username=member.username))
        if check == 1:
            return error(msg='用户名已存在')
    if user.email != member.email:
        check = await crudUsers.check_user_unique(db, schemasUsers.UserCheck(email=member.email))
        if check == 2:
            return error(msg='邮箱已存在')
    if user.mobile != member.mobile:
        check = await crudUsers.check_user_unique(db, schemasUsers.UserCheck(mobile=member.mobile))
        if check == 3:
            return error(msg='手机号已存在')
    new_member = await crudUsers.update_member(db, member_id, member)
    if new_member:
        return success(data=new_member)
    return error(msg='更新失败', data={'error': '成员不存在或已被删除'})


# 获取管理成员信息
@router.get('/members/info/{member_id}', response_model=ApiResponse[schemasUsers.Member])
async def get_member_info(member_id: int, db: AsyncSession = Depends(get_db)):
    member_to_update = await crudUsers.get_member_info(member_id, db)
    if member_to_update:
        return success(data=member_to_update)
    return error(msg='成员不存在或已被删除', data={'error': '成员不存在或已被删除'})


# 按姓名关键字查询作者
@router.get('/members/searchauthor/{author_id}/{search}', response_model=ApiResponse[List[schemasUsers.Member]])
async def search_member(author_id: int, search: str, db: AsyncSession = Depends(get_db)):
    members = await crudUsers.search_member(author_id, search, db)
    if members:
        return success(data=members)
    return error(msg='未查询到作者', data={'error': '未查询到作者'})


# 搜索共同创作者
@router.get('/members/searchcoauthor/{search}', response_model=ApiResponse[List[schemasUsers.Member]])
async def search_common_author(search: str, db: AsyncSession = Depends(get_db)):
    members = await crudUsers.search_common_author(search, db)
    if members:
        return success(data=members)
    return error(msg='未查询到共同创作者', data={'error': '未查询到共同创作者'})


###########
# 用户管理（系统所有注册用户）
###########

# 获取用户列表（分页）
@router.get("/users", response_model=ApiResponse[dict])
async def get_user_list(
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    keyword: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    """获取系统所有用户列表（包括普通用户）"""
    # 确保页码和每页数量为正数
    page = max(1, page)
    page_size = max(1, min(page_size, 100))
    skip = (page - 1) * page_size

    userlist, total = await crudUsers.get_user_list(db, skip=skip, limit=page_size, status=status, keyword=keyword)

    # 获取所有用户ID
    user_ids = [user.id for user in userlist]

    # 统计每个用户的文章数
    articles_count_query = select(
        modelsArticles.BlogArticle.author,
        func.count(modelsArticles.BlogArticle.id).label('count')
    ).where(
        modelsArticles.BlogArticle.author.in_(user_ids),
        modelsArticles.BlogArticle.status == 'published'
    ).group_by(modelsArticles.BlogArticle.author)

    articles_result = await db.execute(articles_count_query)
    articles_counts = {row.author: row.count for row in articles_result}

    # 统计每个用户的评论数
    comments_count_query = select(
        modelsComments.BlogComments.user_id,
        func.count(modelsComments.BlogComments.id).label('count')
    ).where(
        modelsComments.BlogComments.user_id.in_(user_ids),
        modelsComments.BlogComments.status == 1
    ).group_by(modelsComments.BlogComments.user_id)

    comments_result = await db.execute(comments_count_query)
    comments_counts = {row.user_id: row.count for row in comments_result}

    # 构建返回数据
    users_data = []
    for user in userlist:
        users_data.append({
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'email': user.email,
            'mobile': user.mobile,
            'role': user.role,
            'status': user.status,
            'profile_image': user.profile_image,
            'profile_bio': getattr(user, 'profile_bio', None),
            'gender': getattr(user, 'gender', 0),
            'articles_count': articles_counts.get(user.id, 0),
            'comments_count': comments_counts.get(user.id, 0),
            'created_at': user.createtime,
            'updated_at': getattr(user, 'updatetime', None)
        })

    return success(data={
        'users': users_data,
        'total': total,
        'page': page,
        'page_size': page_size
    })


# 获取用户详情
@router.get("/users/{user_id}", response_model=ApiResponse[dict])
async def get_user_detail(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取用户详情"""
    # 直接查询数据库获取原始模型对象
    from app.models.data.users import User
    from sqlalchemy import select

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        return error(msg='用户不存在', data={'error': '用户不存在'})

    user_data = {
        'id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'email': user.email,
        'mobile': user.mobile,
        'role': user.role,
        'status': user.status,
        'profile_image': user.profile_image,
        'profile_bio': getattr(user, 'profile_bio', None),
        'gender': getattr(user, 'gender', 0),
        'articles_count': getattr(user, 'articles_count', 0),
        'comments_count': getattr(user, 'comments_count', 0),
        'created_at': user.createtime,
        'updated_at': getattr(user, 'updatetime', None)
    }
    return success(data=user_data)


# 更新用户状态
@router.put("/users/{user_id}/status", response_model=ApiResponse[dict])
async def update_user_status(
    user_id: int,
    status_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """更新用户状态（normal/disabled）"""
    status = status_data.get('status')
    if status not in ['normal', 'disabled', 'block']:
        return error(msg='状态值错误', data={'error': '状态值错误'})

    user = await crudUsers.get_user_by_id(db, user_id)
    if not user:
        return error(msg='用户不存在', data={'error': '用户不存在'})

    # 更新状态
    updated_user = await crudUsers.update_user_status_field(db, user_id, status)
    if updated_user:
        return success(msg='状态更新成功', data={
            'id': updated_user.id,
            'status': updated_user.status
        })
    return error(msg='状态更新失败', data={'error': '状态更新失败'})


# 更新用户角色
@router.put("/users/{user_id}/role", response_model=ApiResponse[dict])
async def update_user_role(
    user_id: int,
    role_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """更新用户角色（Admin/Author/Contributor/User）"""
    role = role_data.get('role')
    valid_roles = ['Admin', 'Author', 'Contributor', 'User', 'Editor']
    if role not in valid_roles:
        return error(msg='角色值错误', data={'error': '角色值错误'})

    user = await crudUsers.get_user_by_id(db, user_id)
    if not user:
        return error(msg='用户不存在', data={'error': '用户不存在'})

    # 更新角色
    updated_user = await crudUsers.update_user_role_field(db, user_id, role)
    if updated_user:
        return success(msg='角色更新成功', data={
            'id': updated_user.id,
            'role': updated_user.role
        })
    return error(msg='角色更新失败', data={'error': '角色更新失败'})


# 重置用户密码
@router.post("/users/{user_id}/reset-password", response_model=ApiResponse[dict])
async def reset_user_password(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """重置用户密码（生成新密码并发送到用户邮箱）"""
    user = await crudUsers.get_user_by_id(db, user_id)
    if not user:
        return error(msg='用户不存在', data={'error': '用户不存在'})

    # TODO: 生成新密码并发送到用户邮箱
    # 这里只是模拟实现
    import secrets
    import string
    new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))

    # TODO: 更新数据库中的密码
    # TODO: 发送邮件给用户

    return success(msg='密码重置成功，新密码已发送到用户邮箱', data={
        'new_password': new_password  # 测试时返回，生产环境不返回
    })


# 删除用户
@router.delete("/users/{user_id}", response_model=ApiResponse[dict])
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除用户"""
    # 保护系统所有者（ID 为 1）不被删除
    if user_id == 1:
        return error(msg='无法删除系统所有者', data={'error': '无法删除系统所有者'})

    result = await crudUsers.delete_user_by_id(db, user_id)
    if result:
        return success(msg='用户删除成功')
    return error(msg='用户不存在或已被删除', data={'error': '用户不存在或已被删除'})


# 发送用户消息
@router.post("/users/{user_id}/message", response_model=ApiResponse[dict])
async def send_user_message(
    user_id: int,
    message_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """发送消息给用户"""
    user = await crudUsers.get_user_by_id(db, user_id)
    if not user:
        return error(msg='用户不存在', data={'error': '用户不存在'})

    msg_type = message_data.get('type', 'system')
    title = message_data.get('title', '')
    content = message_data.get('content', '')

    if not title or not content:
        return error(msg='消息标题和内容不能为空', data={'error': '消息标题和内容不能为空'})

    # 创建通知
    from app.crud.notifications import create_notification
    from app.models.schemas.notifications import NotificationCreate

    notification = NotificationCreate(
        user_id=user_id,
        type='system',
        title=title,
        content=content,
        actor_id=None,  # 系统消息没有发送者
        actor_name='系统',
        actor_avatar=None,
        target_type=None,
        target_id=None,
        target_title=None,
        target_url=None
    )

    await create_notification(db, notification)

    return success(msg='消息发送成功')


###########
# 标签管理
###########

# 获取标签列表
@router.get('/tag/list', response_model=ApiResponse[dict])
async def get_tag_list(currentpage: int = 1, pagesize: int = 100, keyword: str = '', db: AsyncSession = Depends(get_db)):
    # 确保页码和每页数量为正数
    currentPage = max(1, currentpage)
    pageSize = max(1, pagesize)

    # 计算偏移量
    skip = (currentPage - 1) * pageSize

    taglist = await crudTags.get_tags(db, skip=skip, limit=pageSize, keyword=keyword)
    total = await crudTags.get_tags_count(db, keyword=keyword)
    return success(data={
        "list": taglist,
        "total": total,
        "page": currentPage,
        "pageSize": pageSize
    })


# 新建标签
@router.post('/tag/add', response_model=ApiResponse[schemasTags.BlogTag])
async def add_tag(tagitem: schemasTags.BlogTagCreate, db: AsyncSession = Depends(get_db)):
    if await crudTags.get_tag_by_name(db, tagitem.name):
        return error(msg='标签已存在', data={'error': '标签已存在'})
    if await crudTags.get_tag_by_slug(db, tagitem.slug):
        return error(msg='标签已存在', data={'error': '标签已存在'})
    if tagitem.type not in ['sys', 'user']:
        return error(msg='标签类型错误', data={'error': '标签类型错误'})
    if tagitem.status not in ['normal', 'hidden']:
        return error(msg='标签状态错误', data={'error': '标签状态值错误'})
    tag_data = schemasTags.BlogTagCreate(
        name=tagitem.name,
        tag_desc=tagitem.tag_desc,
        slug=tagitem.slug,
        type=tagitem.type,
        image=tagitem.image,
        status=tagitem.status
    )
    new_tag = await crudTags.create_tag(db, tag_data)
    if new_tag:
        return success(data=new_tag)
    return error(msg='标签创建失败', data={'error': '标签创建失败'})


# 修改标签
@router.post('/tag/edit/{tag_id}', response_model=ApiResponse[schemasTags.BlogTag])
async def update_tag(
        tag_id: Annotated[int, Path()],
        tagitem: schemasTags.BlogTagUpdate,
        db: AsyncSession = Depends(get_db)):
    old_tag = await crudTags.get_tag(db, tag_id)
    if not old_tag:
        return error(msg='标签不存在或已被删除', data={'error': '标签不存在或已被删除'})
    if old_tag.name != tagitem.name:
        if await crudTags.get_tag_by_name(db, tagitem.name):
            return error(msg='标签名已存在', data={'error': '标签已存在'})
    if old_tag.slug != tagitem.slug:
        if await crudTags.get_tag_by_slug(db, tagitem.slug):
            return error(msg='标签 slug 已存在', data={'error': '标签slug 已存在'})
    if tagitem.type not in ['sys', 'user']:
        return error(msg='标签类型错误', data={'error': '标签类型错误'})
    if tagitem.status not in ['normal', 'hidden']:
        return error(msg='标签状态错误', data={'error': '标签状态值错误'})
    tag_data = schemasTags.BlogTagUpdate(
        name=tagitem.name,
        slug=tagitem.slug,
        tag_desc=tagitem.tag_desc,
        type=tagitem.type,
        image=tagitem.image,
        status=tagitem.status,
    )
    new_tag = await crudTags.update_tag(db, tag_id, tag_data)
    if new_tag:
        return success(data=new_tag)
    return error(msg='标签不存在或已被删除', data={'error': '标签不存在或已被删除'})


# 修改标签状态
@router.post('/tag/status/{tag_id}', response_model=ApiResponse[schemasTags.BlogTag])
async def update_tag_status(
        tag_id: Annotated[int, Path()],
        status: Annotated[str, Form()],
        db: AsyncSession = Depends(get_db)):
    if status not in ['normal', 'hidden']:
        return error(data={'error': '状态值错误'})
    tag_data = schemasTags.BlogTagUpdateStatus(status=status)
    new_tag = await crudTags.update_tag_status(db, tag_id, tag_data)
    if new_tag:
        return success(data=new_tag)
    return error(data={'error': '页面不存在或已被删除'})


# 删除标签
@router.delete('/tag/delete/{tag_id}', response_model=ApiResponse[schemasTags.BlogTag])
async def delete_tag(
        tag_id: Annotated[int, Path()],
        db: AsyncSession = Depends(get_db)):
    new_tag = await crudTags.delete_tag(db, tag_id)
    if new_tag:
        return success(msg='删除成功', data=new_tag)
    return error(data={'error': '标签不存在或已被删除'})


# 获取标签详情
@router.get('/tag/detail/{tag_id}', response_model=ApiResponse[schemasTags.BlogTag])
async def get_tag_detail(
        tag_id: Annotated[int, Path()],
        db: AsyncSession = Depends(get_db)):
    tag = await crudTags.get_tag(db, tag_id)
    if tag:
        return success(data=tag)
    return error(msg='标签不存在或已被删除', data={'error': '标签不存在或已被删除'})


# 按关键字查询标签
@router.get('/tag/search/{keyword}', response_model=ApiResponse[List[schemasTags.BlogTag]])
async def search_tag(
        keyword: Annotated[str, Path()],
        db: AsyncSession = Depends(get_db)):
    tags = await crudTags.search_tag(db, keyword)
    if tags:
        return success(data=tags)
    return success(data=[])



###########
# 系统配置
###########

# 获取系统配置
@router.get("/setting", response_model=ApiResponse[schemasSiteConfig.SiteConfig])
async def get_site_config(db: AsyncSession = Depends(get_db)):
    config = await crudSiteConfig.get_site_config(db)
    if config:
        return success(data=config)
    return error(msg='系统配置不存在', data={'error': '系统配置不存在'})


# 更新系统配置
@router.post("/setting/update", response_model=ApiResponse[schemasSiteConfig.SiteConfig])
async def update_site_config(
        site_config: schemasSiteConfig.SiteConfig,
        db: AsyncSession = Depends(get_db)):
    config = await crudSiteConfig.update_site_config(db, site_config)
    if config:
        return success(data=config)
    return error(msg='系统配置不存在', data={'error': '系统配置不存在'})
