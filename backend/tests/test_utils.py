"""
工具模块单元测试
"""
from datetime import datetime

from app.utils.auth import verify_password, get_password_hash
from app.utils.roles import (
    Permission,
    has_permission,
    has_any_permission,
    has_all_permissions
)
from app.utils.response import success, error
from app.models.response import ApiResponse


# ==================== 认证工具测试 ====================

class TestAuthUtils:
    """测试认证工具函数（bcrypt）"""

    def test_get_password_hash_returns_bcrypt(self):
        """测试密码哈希返回 bcrypt 格式（60 字符）且同密码两次哈希不同"""
        password = "testpassword"

        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert isinstance(hash1, str)
        assert len(hash1) == 60  # bcrypt 哈希固定 60 字符
        # bcrypt 内置随机盐，相同密码应生成不同哈希
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """测试正确密码验证"""
        password = "testpassword"
        hashed = get_password_hash(password)

        result = verify_password(password, hashed)
        assert result is True

    def test_verify_password_incorrect(self):
        """测试错误密码验证"""
        password = "testpassword"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)

        result = verify_password(wrong_password, hashed)
        assert result is False

    def test_verify_password_case_sensitive(self):
        """测试密码区分大小写"""
        password = "TestPassword"
        hashed = get_password_hash(password)

        result = verify_password("testpassword", hashed)
        assert result is False


# ==================== 角色权限测试 ====================

class TestRolePermissions:
    """测试角色权限"""

    def test_permission_enum_values(self):
        """测试权限枚举值"""
        assert Permission.MANAGE_USERS == "manage_users"
        assert Permission.MANAGE_ROLES == "manage_roles"
        assert Permission.CREATE_ARTICLE == "create_article"
        assert Permission.PUBLISH_ARTICLE == "publish_article"
        assert Permission.DELETE_ALL_ARTICLES == "delete_all_articles"

    def test_admin_has_all_permissions(self):
        """测试管理员拥有所有权限"""
        for permission in Permission:
            assert has_permission("Admin", permission) is True

    def test_editor_has_specific_permissions(self):
        """测试编辑拥有特定权限"""
        assert has_permission("Editor", Permission.CREATE_ARTICLE) is True
        assert has_permission("Editor", Permission.PUBLISH_ARTICLE) is True
        assert has_permission("Editor", Permission.EDIT_ALL_ARTICLES) is True
        assert has_permission("Editor", Permission.MANAGE_USERS) is False
        assert has_permission("Editor", Permission.MANAGE_SETTINGS) is False

    def test_author_has_limited_permissions(self):
        """测试作者拥有有限权限"""
        assert has_permission("Author", Permission.CREATE_ARTICLE) is True
        assert has_permission("Author", Permission.EDIT_OWN_ARTICLE) is True
        assert has_permission("Author", Permission.DELETE_ALL_ARTICLES) is False
        assert has_permission("Author", Permission.MANAGE_COMMENTS) is False

    def test_user_has_minimal_permissions(self):
        """测试普通用户拥有最小权限"""
        assert has_permission("User", Permission.CREATE_ARTICLE) is False
        assert has_permission("User", Permission.EDIT_OWN_ARTICLE) is False

    def test_unknown_role_has_no_permissions(self):
        """测试未知角色没有权限"""
        assert has_permission("UnknownRole", Permission.CREATE_ARTICLE) is False
        assert has_permission("UnknownRole", Permission.MANAGE_USERS) is False

    def test_has_any_permission_with_editor(self):
        """测试编辑拥有任一指定权限"""
        assert has_any_permission("Editor", [Permission.CREATE_ARTICLE, Permission.MANAGE_USERS]) is True

    def test_has_any_permission_none_match(self):
        """测试没有任何权限匹配"""
        assert has_any_permission("User", [Permission.DELETE_ALL_ARTICLES, Permission.MANAGE_USERS]) is False

    def test_has_all_permissions_admin(self):
        """测试管理员拥有所有指定权限"""
        assert has_all_permissions("Admin", [Permission.CREATE_ARTICLE, Permission.PUBLISH_ARTICLE, Permission.DELETE_ALL_ARTICLES]) is True

    def test_has_all_permissions_user_limited(self):
        """测试普通用户不拥有所有指定权限"""
        assert has_all_permissions("User", [Permission.CREATE_ARTICLE, Permission.EDIT_OWN_ARTICLE]) is False


# ==================== 响应工具测试 ====================

class TestResponseUtils:
    """测试响应工具函数"""

    def test_success_returns_api_response(self):
        """测试 success 返回 ApiResponse"""
        result = success(data={"test": "data"}, msg="成功")

        assert isinstance(result, ApiResponse)
        assert result.code == 1
        assert result.msg == "成功"
        assert result.data == {"test": "data"}
        assert isinstance(result.time, int)

    def test_success_with_default_values(self):
        """测试 success 使用默认值"""
        result = success()

        assert result.code == 1
        assert result.msg == "ok"
        assert result.data is None

    def test_success_with_only_message(self):
        """测试 success 只提供消息"""
        result = success(msg="操作成功")

        assert result.code == 1
        assert result.msg == "操作成功"
        assert result.data is None

    def test_error_returns_json_response(self):
        """测试 error 返回 JSONResponse"""
        from starlette.responses import JSONResponse
        result = error("操作失败")

        assert isinstance(result, JSONResponse)
        assert result.status_code == 200

    def test_error_with_data(self):
        """测试 error 带数据"""
        from starlette.responses import JSONResponse
        result = error("验证失败", data={"field": "email"})

        assert isinstance(result, JSONResponse)
        assert result.status_code == 200

    def test_response_time_is_current(self):
        """测试响应时间是当前时间"""
        before = datetime.now().timestamp()
        result = success()
        after = datetime.now().timestamp()

        # time 是整数秒，所以允许 ±2 秒误差
        assert int(before) - 2 <= result.time <= int(after) + 2


# ==================== 异常处理测试 ====================

class TestExceptionHandling:
    """测试异常处理"""

    def test_none_value_handling(self):
        """测试 None 值处理"""
        result = success(data=None)

        assert result.data is None

    def test_empty_dict_handling(self):
        """测试空字典处理"""
        result = success(data={})

        assert result.data == {}

    def test_empty_list_handling(self):
        """测试空列表处理"""
        result = success(data=[])

        assert result.data == []
