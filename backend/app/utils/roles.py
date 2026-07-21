"""
角色权限配置
定义系统中的角色及其对应的权限
"""

from enum import Enum
from typing import Set, List

# 角色枚举
class UserRole(str, Enum):
    """用户角色枚举"""
    ADMIN = "Admin"           # 管理员 - 所有权限
    EDITOR = "Editor"         # 编辑 - 发布和管理文章
    AUTHOR = "Author"         # 作者 - 创建和管理自己的文章
    CONTRIBUTOR = "Contributor"  # 贡献者 - 创建草稿（需审核）
    USER = "User"             # 普通用户 - 基础权限


# 权限定义
class Permission(str, Enum):
    """权限枚举"""
    # 用户管理
    MANAGE_USERS = "manage_users"           # 管理用户
    MANAGE_ROLES = "manage_roles"           # 管理角色

    # 文章管理
    CREATE_ARTICLE = "create_article"       # 创建文章
    PUBLISH_ARTICLE = "publish_article"     # 发布文章
    EDIT_OWN_ARTICLE = "edit_own_article"   # 编辑自己的文章
    EDIT_ALL_ARTICLES = "edit_all_articles" # 编辑所有文章
    DELETE_OWN_ARTICLE = "delete_own_article" # 删除自己的文章
    DELETE_ALL_ARTICLES = "delete_all_articles" # 删除所有文章

    # 评论管理
    MANAGE_COMMENTS = "manage_comments"     # 管理评论

    # 系统设置
    MANAGE_SETTINGS = "manage_settings"     # 管理系统设置
    MANAGE_MEDIA = "manage_media"           # 管理媒体文件

    # 标签/分类/系列
    MANAGE_TAGS = "manage_tags"             # 管理标签
    MANAGE_CATEGORIES = "manage_categories" # 管理分类
    MANAGE_SERIES = "manage_series"         # 管理系列

    # 邀件管理
    MANAGE_INVITATIONS = "manage_invitations" # 管理成员邀请


# 角色权限映射
ROLE_PERMISSIONS: dict[UserRole, Set[Permission]] = {
    UserRole.ADMIN: {
        # 管理员拥有所有权限
        Permission.MANAGE_USERS,
        Permission.MANAGE_ROLES,
        Permission.CREATE_ARTICLE,
        Permission.PUBLISH_ARTICLE,
        Permission.EDIT_OWN_ARTICLE,
        Permission.EDIT_ALL_ARTICLES,
        Permission.DELETE_OWN_ARTICLE,
        Permission.DELETE_ALL_ARTICLES,
        Permission.MANAGE_COMMENTS,
        Permission.MANAGE_SETTINGS,
        Permission.MANAGE_MEDIA,
        Permission.MANAGE_TAGS,
        Permission.MANAGE_CATEGORIES,
        Permission.MANAGE_SERIES,
        Permission.MANAGE_INVITATIONS,
    },

    UserRole.EDITOR: {
        # 编辑可以发布和管理所有文章
        Permission.CREATE_ARTICLE,
        Permission.PUBLISH_ARTICLE,
        Permission.EDIT_OWN_ARTICLE,
        Permission.EDIT_ALL_ARTICLES,
        Permission.DELETE_OWN_ARTICLE,
        Permission.DELETE_ALL_ARTICLES,
        Permission.MANAGE_COMMENTS,
        Permission.MANAGE_MEDIA,
        Permission.MANAGE_TAGS,
        Permission.MANAGE_CATEGORIES,
        Permission.MANAGE_SERIES,
    },

    UserRole.AUTHOR: {
        # 作者只能创建和管理自己的文章
        Permission.CREATE_ARTICLE,
        Permission.PUBLISH_ARTICLE,
        Permission.EDIT_OWN_ARTICLE,
        Permission.DELETE_OWN_ARTICLE,
        Permission.MANAGE_MEDIA,
    },

    UserRole.CONTRIBUTOR: {
        # 贡献者只能创建草稿（不能直接发布）
        Permission.CREATE_ARTICLE,
        Permission.EDIT_OWN_ARTICLE,
        # 注意：没有 PUBLISH_ARTICLE 权限
    },

    UserRole.USER: {
        # 普通用户只有基础权限（评论等）
    }
}


# 角色层级（用于判断是否可以管理下级角色）
ROLE_HIERARCHY: dict[UserRole, int] = {
    UserRole.ADMIN: 100,
    UserRole.EDITOR: 50,
    UserRole.AUTHOR: 30,
    UserRole.CONTRIBUTOR: 20,
    UserRole.USER: 10,
}


def get_role_permissions(role: str) -> Set[Permission]:
    """获取角色的权限集合"""
    try:
        role_enum = UserRole(role)
        return ROLE_PERMISSIONS.get(role_enum, set())
    except ValueError:
        return set()


def has_permission(role: str, permission: Permission) -> bool:
    """检查角色是否拥有指定权限"""
    permissions = get_role_permissions(role)
    return permission in permissions


def has_any_permission(role: str, permissions: List[Permission]) -> bool:
    """检查角色是否拥有任一指定权限"""
    role_permissions = get_role_permissions(role)
    return any(perm in role_permissions for perm in permissions)


def has_all_permissions(role: str, permissions: List[Permission]) -> bool:
    """检查角色是否拥有所有指定权限"""
    role_permissions = get_role_permissions(role)
    return all(perm in role_permissions for perm in permissions)


def can_manage_role(manager_role: str, target_role: str) -> bool:
    """检查管理角色是否可以管理目标角色"""
    manager_level = ROLE_HIERARCHY.get(UserRole(manager_role), 0)
    target_level = ROLE_HIERARCHY.get(UserRole(target_role), 0)
    return manager_level > target_level


def is_admin_or_editor(role: str) -> bool:
    """检查是否是管理员或编辑"""
    return role in [UserRole.ADMIN.value, UserRole.EDITOR.value]


def is_admin_editor_or_author(role: str) -> bool:
    """检查是否是管理员、编辑或作者"""
    return role in [UserRole.ADMIN.value, UserRole.EDITOR.value, UserRole.AUTHOR.value]


def is_content_creator(role: str) -> bool:
    """检查是否可以创建内容（编辑、作者、贡献者）"""
    return role in [UserRole.ADMIN.value, UserRole.EDITOR.value, UserRole.AUTHOR.value, UserRole.CONTRIBUTOR.value]
