-- phpMyAdmin SQL Dump
-- version 4.9.10
-- https://www.phpmyadmin.net/
--
-- 主机： localhost:8889
-- 生成日期： 2026-07-22 12:07:52
-- 服务器版本： 5.7.39
-- PHP 版本： 7.4.33

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 数据库： `wowblog`
--

-- --------------------------------------------------------

--
-- 表的结构 `alembic_version`
--

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 转存表中的数据 `alembic_version`
--

INSERT INTO `alembic_version` (`version_num`) VALUES
('cd6757a448f8');

-- --------------------------------------------------------

--
-- 表的结构 `wb_articles`
--

CREATE TABLE `wb_articles` (
  `id` int(11) NOT NULL,
  `title` varchar(100) NOT NULL COMMENT '文章标题',
  `subtitle` varchar(200) DEFAULT NULL COMMENT '文章副标题',
  `cover` varchar(100) DEFAULT NULL COMMENT '封面图片',
  `content` mediumtext NOT NULL COMMENT '内容',
  `author` int(10) NOT NULL COMMENT '作者',
  `co_authors` varchar(100) DEFAULT NULL COMMENT '共同作者',
  `category_id` int(10) NOT NULL COMMENT '所属分类',
  `series_id` int(10) DEFAULT NULL COMMENT '所属系列',
  `tags` varchar(100) DEFAULT NULL COMMENT '标签',
  `status` enum('draft','published','scheduled','deleted') NOT NULL COMMENT '状态',
  `pub_time` int(10) NOT NULL COMMENT '发布时间',
  `slug` varchar(100) NOT NULL COMMENT '文章Slug',
  `seo_title` varchar(100) DEFAULT NULL COMMENT 'SEO标题',
  `seo_desc` varchar(300) DEFAULT NULL COMMENT 'SEO描述',
  `og_image` varchar(100) DEFAULT NULL COMMENT '转发图片',
  `disable_comments` tinyint(2) NOT NULL COMMENT '禁用评论:0=否,1=是',
  `enable_table_content` tinyint(4) NOT NULL DEFAULT '0' COMMENT '启用内容目录:0=否,1=是',
  `sort` int(10) NOT NULL DEFAULT '0' COMMENT '文章排序',
  `is_pin` tinyint(2) NOT NULL COMMENT '是否置顶:0=否,1=是',
  `is_recommend` tinyint(4) NOT NULL DEFAULT '0' COMMENT '是否推荐:0=否,1=是',
  `is_featured` tinyint(4) NOT NULL DEFAULT '0' COMMENT '是否精选:0=否,1=是',
  `createtime` int(10) NOT NULL COMMENT '创建时间',
  `updatetime` int(10) DEFAULT NULL COMMENT '更新时间',
  `deletetime` int(10) DEFAULT NULL COMMENT '删除时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文章管理';


-- --------------------------------------------------------

--
-- 表的结构 `wb_articles_data`
--

CREATE TABLE `wb_articles_data` (
  `id` int(11) NOT NULL,
  `article_id` int(11) NOT NULL,
  `likes` int(11) DEFAULT '0',
  `comments` int(11) DEFAULT '0',
  `bookmarks` int(11) DEFAULT '0',
  `shares` int(11) DEFAULT '0',
  `views` int(11) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- --------------------------------------------------------

--
-- 表的结构 `wb_article_views`
--

CREATE TABLE `wb_article_views` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `article_id` int(11) NOT NULL,
  `view_time` int(11) NOT NULL,
  `view_duration` int(11) DEFAULT '0',
  `is_deep_read` int(11) DEFAULT '0',
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` varchar(500) DEFAULT NULL,
  `device_type` varchar(20) DEFAULT NULL,
  `source` varchar(50) DEFAULT NULL,
  `device_fingerprint` varchar(100) DEFAULT NULL,
  `is_logged_in` int(11) DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- --------------------------------------------------------

--
-- 表的结构 `wb_categories`
--

CREATE TABLE `wb_categories` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL COMMENT '分类名称',
  `pid` int(10) NOT NULL COMMENT '所属分类',
  `cat_desc` varchar(300) NOT NULL COMMENT '分类描述',
  `slug` varchar(20) NOT NULL COMMENT '分类Slug',
  `image` varchar(100) DEFAULT NULL COMMENT '分类封面',
  `articles_order` enum('id desc','views desc','pubtime asc') NOT NULL DEFAULT 'id desc' COMMENT '文章排序',
  `sort` int(10) NOT NULL DEFAULT '0' COMMENT '排序',
  `createtime` int(10) NOT NULL COMMENT '创建时间',
  `updatetime` int(10) DEFAULT NULL COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分类管理';


-- --------------------------------------------------------

--
-- 表的结构 `wb_comments`
--

CREATE TABLE `wb_comments` (
  `id` int(11) NOT NULL,
  `article_id` int(11) NOT NULL DEFAULT '0',
  `doc_id` int(11) NOT NULL DEFAULT '0',
  `user_id` int(11) NOT NULL,
  `comment` varchar(500) NOT NULL,
  `ip` varchar(15) NOT NULL,
  `likes` int(11) NOT NULL DEFAULT '0',
  `unlikes` int(11) NOT NULL DEFAULT '0',
  `replys` int(11) NOT NULL DEFAULT '0',
  `type` enum('subject','reply') NOT NULL DEFAULT 'reply',
  `subject_id` int(11) NOT NULL DEFAULT '0',
  `pid` int(11) NOT NULL DEFAULT '0',
  `sort` int(11) NOT NULL DEFAULT '0',
  `status` tinyint(4) NOT NULL DEFAULT '1',
  `createtime` int(10) NOT NULL,
  `deletetime` int(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- --------------------------------------------------------

--
-- 表的结构 `wb_config`
--

CREATE TABLE `wb_config` (
  `id` int(11) NOT NULL,
  `site_title` varchar(100) NOT NULL,
  `site_logo` varchar(100) DEFAULT NULL,
  `site_favicon` varchar(100) DEFAULT NULL,
  `language` varchar(10) NOT NULL,
  `dark_mode` enum('system','dark','light') NOT NULL,
  `disable_comment` tinyint(4) NOT NULL,
  `default_homepage` enum('blog','doc') DEFAULT 'blog' COMMENT '默认首页类型',
  `default_docbook_id` int(11) DEFAULT NULL COMMENT '默认文档书ID',
  `doc_subdomain` varchar(100) DEFAULT NULL COMMENT '文档模块子域名',
  `doc_comment` tinyint(4) NOT NULL COMMENT '禁用文档评论',
  `message_push_method` enum('websocket','polling') DEFAULT 'websocket' COMMENT '消息推送方式：websocket=实时推送，polling=定时轮询',
  `polling_interval` int(11) DEFAULT '30' COMMENT '轮询间隔（秒），仅当push_method为polling时有效',
  `footer_config` text,
  `enable_register` tinyint(4) NOT NULL COMMENT '是否开启注册',
  `register_role` varchar(20) NOT NULL COMMENT '用户默认角色',
  `enable_article_review_notification` tinyint(4) NOT NULL COMMENT '开启文章审核提醒，0不开启，1开启',
  `article_review_notification_roles` text NOT NULL COMMENT '文章审核提醒接收者角色'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 转存表中的数据 `wb_config`
--

INSERT INTO `wb_config` (`id`, `site_title`, `site_logo`, `site_favicon`, `language`, `dark_mode`, `disable_comment`, `default_homepage`, `default_docbook_id`, `doc_subdomain`, `doc_comment`, `message_push_method`, `polling_interval`, `footer_config`, `enable_register`, `register_role`, `enable_article_review_notification`, `article_review_notification_roles`) VALUES
(1, 'WOW Blog', '/wow_blog_logo.svg', '/favicon.ico', 'zh-CN', 'system', 0, 'blog', NULL, NULL, 1, 'websocket', 30, '{\"logo_url\": \"/wow_blog_logo.svg\", \"site_description\": \"一个具有社交功能的团队Blog系统，并能创建专业的文档系统。\", \"social_media\": [{\"icon\": \"ant-design:zhihu-circle-filled\", \"url\": \"http://www.zhihu.com/user/123456\"}, {\"icon\": \"mage:tiktok-circle\", \"url\": \"http://www.douyin.com/user/231231231\"}, {\"icon\": \"simple-icons:xiaohongshu\", \"url\": \"http://www.xiaohongshu.com/user/12312312\"}, {\"icon\": \"ri:weibo-fill\", \"url\": \"http://weibo.com/\"}, {\"icon\": \"streamline-ultimate:bilibili-logo-bold\", \"url\": \"http://www.bilibili.com/\"}], \"nav_groups\": [{\"group_name\": \"产品\", \"links\": [{\"name\": \"Blog系统\", \"url\": \"\"}, {\"name\": \"文档系统\", \"url\": \"\"}]}, {\"group_name\": \"公司\", \"links\": [{\"name\": \"服务协议\", \"url\": \"\"}, {\"name\": \"隐私协议\", \"url\": \"\"}]}, {\"group_name\": \"联系我们\", \"links\": [{\"name\": \"contact@company.com\", \"url\": \"\"}]}], \"copyright\": \"WOW Blog\", \"icp_info\": [{\"text\": \"津ICP备 12345-5号\", \"url\": \"http://ww.mii.org.cn/\"}]}', 1, 'User', 1, '[\"Admin\",\"Editor\"]');

-- --------------------------------------------------------

--
-- 表的结构 `wb_doc`
--

CREATE TABLE `wb_doc` (
  `id` int(11) NOT NULL COMMENT '文档ID',
  `docbook_id` int(11) NOT NULL COMMENT '所属文档书ID',
  `title` varchar(255) NOT NULL COMMENT '文档标题',
  `slug` varchar(255) NOT NULL COMMENT 'URL标识',
  `content` longtext COMMENT '文档内容（Markdown）',
  `excerpt` text COMMENT '摘要',
  `parent_id` int(11) DEFAULT '0' COMMENT '父文档ID，0为顶级',
  `level` int(11) DEFAULT '1' COMMENT '层级深度',
  `path` varchar(500) DEFAULT NULL COMMENT '树路径：0/1/2',
  `sort_order` int(11) DEFAULT '0' COMMENT '同级排序',
  `status` enum('draft','published','hidden') DEFAULT 'draft' COMMENT '状态',
  `author_id` int(11) NOT NULL COMMENT '作者ID',
  `createtime` bigint(20) NOT NULL COMMENT '创建时间',
  `updatetime` bigint(20) NOT NULL COMMENT '更新时间',
  `pubtime` bigint(20) DEFAULT NULL COMMENT '发布时间',
  `view_count` int(11) DEFAULT '0' COMMENT '浏览次数',
  `comment_count` int(11) DEFAULT '0' COMMENT '评论数',
  `seo_title` varchar(255) DEFAULT NULL COMMENT 'SEO标题',
  `seo_keywords` varchar(500) DEFAULT NULL COMMENT 'SEO关键词',
  `seo_description` text COMMENT 'SEO描述'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文档表';


-- --------------------------------------------------------

--
-- 表的结构 `wb_docbook`
--

CREATE TABLE `wb_docbook` (
  `id` int(11) NOT NULL COMMENT '文档书ID',
  `name` varchar(100) NOT NULL COMMENT '文档书名称',
  `slug` varchar(100) NOT NULL COMMENT 'URL标识',
  `description` text COMMENT '文档书描述',
  `cover` varchar(500) DEFAULT NULL COMMENT '封面图URL',
  `icon` varchar(100) DEFAULT NULL COMMENT '图标',
  `is_public` tinyint(1) DEFAULT '1' COMMENT '是否公开',
  `show_sidebar` tinyint(1) DEFAULT '1' COMMENT '是否显示侧边栏',
  `allow_comment` tinyint(1) DEFAULT '1' COMMENT '是否允许评论',
  `allow_search` tinyint(1) DEFAULT '1' COMMENT '是否允许搜索',
  `theme` varchar(50) DEFAULT 'default' COMMENT '主题样式',
  `home_doc_id` int(11) DEFAULT NULL COMMENT '首页文档ID',
  `author_id` int(11) NOT NULL COMMENT '创建者ID',
  `sort_order` int(11) DEFAULT '0' COMMENT '排序',
  `createtime` bigint(20) NOT NULL COMMENT '创建时间',
  `updatetime` bigint(20) NOT NULL COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文档书表';


-- --------------------------------------------------------

--
-- 表的结构 `wb_email_settings`
--

CREATE TABLE `wb_email_settings` (
  `id` int(11) NOT NULL,
  `provider` varchar(50) NOT NULL COMMENT '邮件服务提供商',
  `smtp_host` varchar(255) NOT NULL COMMENT 'SMTP服务器',
  `smtp_port` int(11) DEFAULT '587',
  `smtp_user` varchar(255) DEFAULT NULL,
  `smtp_pass` varchar(255) DEFAULT NULL,
  `use_tls` tinyint(1) DEFAULT '1',
  `from_email` varchar(100) NOT NULL,
  `from_name` varchar(100) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` int(10) NOT NULL,
  `updated_at` int(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 转存表中的数据 `wb_email_settings`
--

INSERT INTO `wb_email_settings` (`id`, `provider`, `smtp_host`, `smtp_port`, `smtp_user`, `smtp_pass`, `use_tls`, `from_email`, `from_name`, `is_active`, `created_at`, `updated_at`) VALUES
(1, 'gmail', 'smtp.gmail.com', 587, NULL, NULL, 1, 'noreply@example.com', 'Blog Notification', 0, 1781683023, 1781683023),
(2, 'outlook', 'smtp.office365.com', 587, NULL, NULL, 1, 'noreply@example.com', 'Blog Notification', 0, 1781683023, 1781683023),
(3, 'qq', 'smtp.qq.com', 465, NULL, NULL, 1, 'noreply@example.com', 'Blog Notification', 0, 1781683023, 1782704831);

-- --------------------------------------------------------

--
-- 表的结构 `wb_member_invitations`
--

CREATE TABLE `wb_member_invitations` (
  `id` int(11) NOT NULL,
  `token` varchar(64) NOT NULL COMMENT '邀请令牌',
  `email` varchar(100) NOT NULL COMMENT '被邀请者邮箱',
  `role` varchar(20) NOT NULL COMMENT '邀请角色',
  `invited_by` int(11) NOT NULL COMMENT '邀请人ID',
  `blog_name` varchar(100) DEFAULT NULL COMMENT '博客名称',
  `admin_name` varchar(50) DEFAULT NULL COMMENT '管理员名称',
  `language` varchar(10) DEFAULT 'zh-CN' COMMENT '邮件语言',
  `status` enum('pending','accepted','cancelled','expired') DEFAULT 'pending',
  `expires_at` int(10) NOT NULL COMMENT '过期时间',
  `created_at` int(10) NOT NULL DEFAULT '0',
  `updated_at` int(10) NOT NULL DEFAULT '0',
  `accepted_at` int(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- --------------------------------------------------------

--
-- 表的结构 `wb_nav`
--

CREATE TABLE `wb_nav` (
  `id` int(11) NOT NULL,
  `label` varchar(100) NOT NULL COMMENT '显示文本',
  `nav_type` enum('sys','user') DEFAULT 'user',
  `type` enum('link','page','series','doc') NOT NULL COMMENT '类型',
  `value` varchar(100) NOT NULL COMMENT '值',
  `sort` int(10) NOT NULL DEFAULT '0' COMMENT '排序',
  `status` int(2) NOT NULL COMMENT '状态:1=显示,0=隐藏'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='导航';

--
-- 转存表中的数据 `wb_nav`
--

INSERT INTO `wb_nav` (`id`, `label`, `nav_type`, `type`, `value`, `sort`, `status`) VALUES
(1, '首页', 'sys', 'link', '/', 0, 1),
(2, '分类', 'sys', 'link', 'category', 1, 1),
(3, '系列', 'sys', 'link', 'series', 2, 1),
(4, '文档', 'sys', 'link', 'doc', 3, 1),
(5, '关于我们', 'user', 'page', '1', 5, 1);

-- --------------------------------------------------------

--
-- 表的结构 `wb_notifications`
--

CREATE TABLE `wb_notifications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL COMMENT '接收用户ID',
  `type` varchar(20) NOT NULL COMMENT '通知类型：comment/reply/article_mention/comment_mention/like/bookmark/system',
  `title` varchar(200) NOT NULL COMMENT '通知标题',
  `content` text COMMENT '通知内容摘要',
  `actor_id` int(11) DEFAULT NULL COMMENT '触发者用户ID',
  `actor_name` varchar(50) DEFAULT NULL COMMENT '触发者用户名（缓存）',
  `actor_avatar` text COMMENT '触发者头像（缓存）',
  `target_type` varchar(20) DEFAULT NULL COMMENT '关联对象类型：article/comment/doc',
  `target_id` int(11) DEFAULT NULL COMMENT '关联对象ID',
  `target_title` varchar(200) DEFAULT NULL COMMENT '关联对象标题（缓存）',
  `target_url` varchar(500) DEFAULT NULL COMMENT '关联对象URL',
  `is_read` tinyint(1) DEFAULT '0' COMMENT '是否已读',
  `created_at` int(11) DEFAULT '0' COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='消息通知表';


-- --------------------------------------------------------

--
-- 表的结构 `wb_pages`
--

CREATE TABLE `wb_pages` (
  `id` int(11) NOT NULL,
  `type` enum('system','custom') NOT NULL DEFAULT 'custom' COMMENT '类型',
  `title` varchar(20) NOT NULL COMMENT '标题',
  `content` mediumtext NOT NULL COMMENT '内容',
  `slug` varchar(20) NOT NULL COMMENT '页面Slug',
  `image` varchar(100) DEFAULT NULL COMMENT '转发图片',
  `seo_desc` varchar(300) DEFAULT NULL COMMENT 'SEO描述',
  `status` enum('normal','hidden') NOT NULL DEFAULT 'normal' COMMENT '状态',
  `createtime` int(10) NOT NULL COMMENT '创建时间',
  `updatetime` int(10) DEFAULT NULL COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='页面管理';

--
-- 转存表中的数据 `wb_pages`
--

INSERT INTO `wb_pages` (`id`, `type`, `title`, `content`, `slug`, `image`, `seo_desc`, `status`, `createtime`, `updatetime`) VALUES
(1, 'custom', 'About Us', '<h1>About Us</h1><p></p><p>This is a custom page.</p>', 'aboutus', NULL, NULL, 'hidden', 1757043426, 1757043497);

-- --------------------------------------------------------

--
-- 表的结构 `wb_series`
--

CREATE TABLE `wb_series` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL COMMENT '系列名称',
  `slug` varchar(20) NOT NULL COMMENT '系列Slug',
  `series_desc` varchar(300) DEFAULT NULL COMMENT '系列描述',
  `image` varchar(100) DEFAULT NULL COMMENT '封面图片',
  `articles_order` enum('desc','asc') NOT NULL DEFAULT 'desc' COMMENT '文章排序',
  `sort` int(11) NOT NULL DEFAULT '0',
  `createtime` int(10) NOT NULL COMMENT '创建时间',
  `updatetime` int(10) DEFAULT NULL COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系列管理';


-- --------------------------------------------------------

--
-- 表的结构 `wb_tags`
--

CREATE TABLE `wb_tags` (
  `id` int(11) NOT NULL,
  `type` enum('sys','user') NOT NULL DEFAULT 'user',
  `name` varchar(20) NOT NULL,
  `slug` varchar(20) NOT NULL,
  `tag_desc` varchar(200) DEFAULT NULL,
  `status` enum('normal','hidden') NOT NULL DEFAULT 'normal',
  `image` varchar(100) DEFAULT NULL,
  `counts` int(11) DEFAULT '0' COMMENT '下属文章数',
  `views` int(11) DEFAULT '0' COMMENT '点击查看数',
  `follows` int(11) DEFAULT '0' COMMENT '跟随关注数'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='标签管理';

--
-- 转存表中的数据 `wb_tags`
--

INSERT INTO `wb_tags` (`id`, `type`, `name`, `slug`, `tag_desc`, `status`, `image`, `counts`, `views`, `follows`) VALUES
(1, 'sys', 'Javascript', 'javascript', NULL, 'normal', NULL, 0, 0, 0),
(2, 'sys', 'Vue.js', 'vuejs', NULL, 'normal', NULL, 0, 0, 0),
(3, 'sys', 'React', 'react', NULL, 'normal', NULL, 0, 0, 0),
(4, 'sys', 'Angular', 'angular', NULL, 'normal', NULL, 0, 0, 0),
(5, 'sys', 'TypeScript', 'typescript', '', 'normal', '', 0, 0, 0),
(6, 'sys', 'Node.js', 'nodejs', 'Node.js is an open-source, cross-platform, back-end, JavaScript runtime environment that executes JavaScript code outside a web browser.', 'normal', NULL, 0, 0, 0),
(7, 'sys', 'HTML', 'html', '', 'normal', '', 0, 0, 0),
(8, 'sys', 'CSS', 'css', '', 'normal', '', 0, 0, 0),
(9, 'sys', 'Web Development', 'web-development', '', 'normal', '', 0, 0, 0),
(10, 'sys', 'Frontend', 'frontend', '', 'normal', '', 0, 0, 0),
(11, 'sys', 'Backend', 'backend', '', 'normal', '', 0, 0, 0),
(12, 'sys', 'Database', 'database', '', 'normal', '', 0, 0, 0),
(13, 'sys', 'API', 'api', '', 'normal', '', 0, 0, 0),
(14, 'sys', 'Mobile', 'mobile', '', 'normal', '', 0, 0, 0),
(15, 'sys', 'UI/UX', 'ui-ux', '', 'normal', '', 0, 0, 0);

-- --------------------------------------------------------

--
-- 表的结构 `wb_users`
--

CREATE TABLE `wb_users` (
  `id` int(11) NOT NULL,
  `username` varchar(20) NOT NULL COMMENT '用户名',
  `password` varchar(72) DEFAULT NULL,
  `salt` varchar(64) DEFAULT NULL,
  `full_name` varchar(20) DEFAULT NULL COMMENT '全名',
  `profile_image` varchar(1000) DEFAULT NULL COMMENT '头像',
  `profile_tagline` varchar(100) DEFAULT NULL COMMENT '简介标语',
  `location` varchar(100) DEFAULT NULL COMMENT '所在地',
  `gender` tinyint(2) DEFAULT '1' COMMENT '性别:0=女性,1=男性',
  `birthday` int(10) DEFAULT NULL COMMENT '生日',
  `school` varchar(50) DEFAULT NULL COMMENT '学校',
  `profile_bio` varchar(300) DEFAULT NULL COMMENT '个人简介',
  `tech_stack` varchar(300) DEFAULT NULL COMMENT '技术栈',
  `available_for` varchar(300) DEFAULT NULL COMMENT '适用于',
  `social_profiles` json DEFAULT NULL COMMENT '社交资料',
  `email` varchar(50) DEFAULT NULL COMMENT '邮件',
  `mobile` varchar(11) DEFAULT NULL COMMENT '手机',
  `role` enum('Admin','Editor','Contributor','User','Author') NOT NULL DEFAULT 'User' COMMENT '角色',
  `visibility` enum('Public','Private') NOT NULL DEFAULT 'Public' COMMENT '可见性',
  `status` enum('normal','block') NOT NULL DEFAULT 'normal' COMMENT '状态',
  `join_ip` varchar(15) DEFAULT NULL,
  `login_ip` varchar(15) DEFAULT NULL,
  `login_time` int(10) DEFAULT NULL,
  `createtime` int(10) NOT NULL COMMENT '创建时间',
  `updatetime` int(10) DEFAULT NULL COMMENT '更新时间',
  `notification_check_at` int(11) DEFAULT NULL COMMENT '最后检查通知时间',
  `privacy_show_bookmarks` int(11) DEFAULT '1' COMMENT '是否展示收藏',
  `privacy_show_likes` int(11) DEFAULT '1' COMMENT '是否展示点赞',
  `privacy_show_comments` int(11) DEFAULT '1' COMMENT '是否展示评论',
  `privacy_show_views` int(11) DEFAULT '1' COMMENT '是否展示浏览'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户管理';

--
-- 转存表中的数据 `wb_users`
--

INSERT INTO `wb_users` (`id`, `username`, `password`, `salt`, `full_name`, `profile_image`, `profile_tagline`, `location`, `gender`, `birthday`, `school`, `profile_bio`, `tech_stack`, `available_for`, `social_profiles`, `email`, `mobile`, `role`, `visibility`, `status`, `join_ip`, `login_ip`, `login_time`, `createtime`, `updatetime`, `notification_check_at`, `privacy_show_bookmarks`, `privacy_show_likes`, `privacy_show_comments`, `privacy_show_views`) VALUES
(1, 'admin', '$2b$12$Uaa..7BP7lfVPkU2iltMIulvLZfrmWx303qYAiSFfpjREik8WBl7.', NULL, 'Blog Admin', NULL, '', '', 1, NULL, '', '', NULL, '', NULL, 'yourname@example.com', '', 'Admin', 'Public', 'normal', '', '127.0.0.1', 1783993595, 1755399562, NULL, NULL, 1, 1, 1, 1);

-- --------------------------------------------------------

--
-- 表的结构 `wb_users_data`
--

CREATE TABLE `wb_users_data` (
  `id` int(11) NOT NULL,
  `type` enum('FOLLOW_TAG','FOLLOW_USER','BOOKMARK','LIKE','SHARE') NOT NULL,
  `user_id` int(11) NOT NULL,
  `target_id` int(11) NOT NULL COMMENT '目标id:文章标签用户',
  `status` tinyint(4) NOT NULL DEFAULT '1' COMMENT '状态:0=隐藏,1=显示',
  `createtime` int(10) NOT NULL,
  `updatetime` int(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


--
-- 转储表的索引
--

--
-- 表的索引 `alembic_version`
--
ALTER TABLE `alembic_version`
  ADD PRIMARY KEY (`version_num`);

--
-- 表的索引 `wb_articles`
--
ALTER TABLE `wb_articles`
  ADD PRIMARY KEY (`id`);

--
-- 表的索引 `wb_articles_data`
--
ALTER TABLE `wb_articles_data`
  ADD PRIMARY KEY (`id`),
  ADD KEY `article_id` (`article_id`);

--
-- 表的索引 `wb_article_views`
--
ALTER TABLE `wb_article_views`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_user_time` (`user_id`,`view_time`),
  ADD KEY `idx_article_time` (`article_id`,`view_time`),
  ADD KEY `idx_stats_time` (`view_time`);

--
-- 表的索引 `wb_categories`
--
ALTER TABLE `wb_categories`
  ADD PRIMARY KEY (`id`);

--
-- 表的索引 `wb_comments`
--
ALTER TABLE `wb_comments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `subject_id` (`subject_id`),
  ADD KEY `pid` (`pid`);

--
-- 表的索引 `wb_config`
--
ALTER TABLE `wb_config`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_docbook` (`default_docbook_id`);

--
-- 表的索引 `wb_doc`
--
ALTER TABLE `wb_doc`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uk_docbook_slug` (`docbook_id`,`slug`),
  ADD KEY `idx_docbook` (`docbook_id`),
  ADD KEY `idx_parent` (`parent_id`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_sort` (`docbook_id`,`parent_id`,`sort_order`),
  ADD KEY `idx_author` (`author_id`);

--
-- 表的索引 `wb_docbook`
--
ALTER TABLE `wb_docbook`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `slug` (`slug`),
  ADD KEY `idx_slug` (`slug`),
  ADD KEY `idx_author` (`author_id`),
  ADD KEY `idx_sort` (`sort_order`);

--
-- 表的索引 `wb_email_settings`
--
ALTER TABLE `wb_email_settings`
  ADD PRIMARY KEY (`id`);

--
-- 表的索引 `wb_member_invitations`
--
ALTER TABLE `wb_member_invitations`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `token` (`token`),
  ADD KEY `idx_token` (`token`),
  ADD KEY `idx_email` (`email`),
  ADD KEY `idx_status` (`status`);

--
-- 表的索引 `wb_nav`
--
ALTER TABLE `wb_nav`
  ADD PRIMARY KEY (`id`);

--
-- 表的索引 `wb_notifications`
--
ALTER TABLE `wb_notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_user_read` (`user_id`,`is_read`,`created_at`),
  ADD KEY `idx_created` (`created_at`);

--
-- 表的索引 `wb_pages`
--
ALTER TABLE `wb_pages`
  ADD PRIMARY KEY (`id`);

--
-- 表的索引 `wb_series`
--
ALTER TABLE `wb_series`
  ADD PRIMARY KEY (`id`);

--
-- 表的索引 `wb_tags`
--
ALTER TABLE `wb_tags`
  ADD PRIMARY KEY (`id`);

--
-- 表的索引 `wb_users`
--
ALTER TABLE `wb_users`
  ADD PRIMARY KEY (`id`);

--
-- 表的索引 `wb_users_data`
--
ALTER TABLE `wb_users_data`
  ADD PRIMARY KEY (`id`);


--
-- 限制导出的表
--

--
-- 限制表 `wb_doc`
--
ALTER TABLE `wb_doc`
  ADD CONSTRAINT `wb_doc_ibfk_1` FOREIGN KEY (`docbook_id`) REFERENCES `wb_docbook` (`id`) ON DELETE CASCADE;

--
-- 限制表 `wb_notifications`
--
ALTER TABLE `wb_notifications`
  ADD CONSTRAINT `wb_notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `wb_users` (`id`) ON DELETE CASCADE;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
