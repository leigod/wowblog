from pydantic import BaseModel, Field, model_validator
from pydantic.config import ConfigDict
from typing import Optional, List, Literal
import time


class Token(BaseModel):
    access_token: str
    token_type: str
    model_config = ConfigDict(from_attributes=True)


class TokenData(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    username: str
    email: str | None = None
    mobile: str | None = None
    full_name: str | None = None
    profile_image: str | None = None
    status: str
    role: str
    # 隐私设置
    privacy_show_bookmarks: int | None = 1
    privacy_show_likes: int | None = 1
    privacy_show_comments: int | None = 1
    privacy_show_views: int | None = 1
    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserBase):
    salt: str | None = None
    password: str = ""


class UserCheck(BaseModel):
    username: str | None = None
    email: str | None = None
    mobile: str | None = None


class UserRegisterFormData(BaseModel):
    username: str = Field(description="用户名仅支持英文、数字、下划线，长度限制在3-20位之间", min_length=3, max_length=20,
                          pattern="^[A-Za-z][A-Za-z0-9_]{2,19}$")
    password: str = Field(description="密码仅支持英文、数字、下划线，长度限制在6-20位之间", min_length=6, max_length=20)
    full_name: str = Field(description="用户名长度限制在20位之间", min_length=3, max_length=20)
    email: str | None = None
    mobile: str | None = None
    profile_image: str | None = None
    gender: int | None = Field(default=0, description="性别，1表示男，0表示女")


class UserRegister(BaseModel):
    username: str = Field(description="用户名仅支持英文、数字、下划线，长度限制在3-20位之间", min_length=3, max_length=20,
                          pattern="^[A-Za-z][A-Za-z0-9_]{2,19}$")
    password: str = Field(description="密码长度限制在6-20位之间", min_length=6, max_length=64)
    salt: str = Field(max_length=32, description="盐值长度限制在32位之间")
    full_name: str | None = Field(None, min_length=3,max_length=20, description="用户名长度限制在20位之间")
    email: str | None = None
    mobile: str | None = None
    status: Literal['normal', 'block'] = "normal"
    profile_image: str | None = None
    gender: int | None = Field(default=0, description="性别，1表示男，0表示女")
    role: Literal['User'] = 'User'
    join_ip: str | None = None
    createtime: int = int(time.time())


class UserCreate(BaseModel):
    username: str = Field(description="用户名仅支持英文、数字、下划线，长度限制在3-20位之间", min_length=3, max_length=20,
                          pattern="^[A-Za-z][A-Za-z0-9_]{2,19}$")
    password: str = Field(max_length=64)
    salt: str = Field(max_length=32, description="盐值长度限制在32位之间")
    createtime: int = int(time.time())


# blog管理团队成员模型
class MemberBase(UserBase):
    gender: int
    visibility: str


class MemberCreateBase(BaseModel):
    username: str = Field(description="用户名仅支持英文、数字、下划线，长度限制在3-20位之间", min_length=3, max_length=20,
                          pattern="^[A-Za-z][A-Za-z0-9_]{2,19}$")
    full_name: str | None = Field(None, max_length=20, description="用户名长度限制在20位之间")
    email: str | None = None
    mobile: str | None = None
    profile_image: str | None = None
    gender: int | None = None
    role: Literal['Admin', 'Editor', 'Contributor'] = 'Contributor'


# blog管理团队成员创建模型
class MemberCreate(MemberCreateBase):
    password: str = Field(max_length=64)
    salt: str = Field(max_length=32, description="盐值长度限制在32位之间")
    visibility: Literal['Public', 'Private'] = "Private"
    status: Literal['normal', 'block'] = "normal"
    createtime: int = int(time.time())


class MemberUpdate(MemberCreateBase):
    updatetime: int = int(time.time())


class MemberUpdateStatus(BaseModel):
    status: Literal['normal', 'block'] = "normal"


class MemberUpdateVisibility(BaseModel):
    visibility: Literal['Public', 'Private'] = "Private"


class Member(MemberBase):
    id: int


class UserLogin(BaseModel):
    login_ip: str | None = None
    login_time: int | None = int(time.time())


class UserFullInfo(UserBase):
    id: int
    profile_tagline: str | None = None
    location: str | None = None
    gender: int | None = None
    birthday: int | None = None
    school: str | None = None
    profile_bio: str | None = None
    tech_stack: list[str] | None = None
    available_for: str | None = None
    social_profiles: dict | None = None
    createtime: int
    followers_count: int | None = 0


# 用户个人资料更新模型
class UserProfileUpdate(BaseModel):
    full_name: str | None = Field(None, max_length=20)
    profile_tagline: str | None = Field(None, max_length=100)
    email: str | None = None
    mobile: str | None = None
    location: str | None = Field(None, max_length=100)
    gender: int | None = None
    birthday: str | None = None  # 前端传入日期字符串 ISO 格式
    school: str | None = Field(None, max_length=100)
    profile_bio: str | None = Field(None, max_length=500)
    tech_stack: List[str] | None = None  # 前端传入数组，后端转换为逗号分隔字符串
    available_for: str | None = Field(None, max_length=300)
    social_profiles: dict | None = None  # 前端传入字典，后端转换为JSON字符串
    profile_image: str | None = None

class User(UserBase):
    id: int

    class Config:
        orm_mode = True


# 用户隐私设置更新模型
class UserPrivacyUpdate(BaseModel):
    privacy_show_bookmarks: int | None = None
    privacy_show_likes: int | None = None
    privacy_show_comments: int | None = None
    privacy_show_views: int | None = None
