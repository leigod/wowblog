-- WowBlog 全量数据库结构（全新空库初始化用）
-- 由 mysqldump --no-data 从当前开发库导出，仅含表结构，不含任何真实业务数据。
-- 下方 INSERT 均为占位模板（示例管理员 / 示例配置）。
-- 初始管理员：admin / yourname@example.com，初始密码 admin123456，首次登录后请立即修改。
-- alembic_version 已写入当前 head（f7a3c1e9d4b2），保持与 alembic/versions/ 一致。
--
-- MySQL dump 10.13  Distrib 8.4.4, for macos15 (arm64)
--
-- Host: 127.0.0.1    Database: wowblog
-- ------------------------------------------------------
-- Server version	5.7.39

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wb_admin_logs`
--

DROP TABLE IF EXISTS `wb_admin_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wb_admin_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL COMMENT '操作人用户ID',
  `username` varchar(50) DEFAULT NULL COMMENT '操作人用户名（冗余）',
  `role` varchar(20) DEFAULT NULL COMMENT '操作人角色',
  `action` varchar(100) DEFAULT NULL COMMENT '动作: login/logout 或 METHOD:path',
  `method` varchar(10) DEFAULT NULL COMMENT 'HTTP 方法',
  `path` varchar(200) DEFAULT NULL COMMENT '请求路径',
  `detail` text COMMENT '请求体 JSON（已脱敏）',
  `status_code` int(11) DEFAULT NULL COMMENT '响应状态码',
  `ip` varchar(45) DEFAULT NULL COMMENT '客户端IP',
  `user_agent` varchar(500) DEFAULT NULL COMMENT 'User-Agent',
  `createtime` int(11) DEFAULT NULL COMMENT '创建时间戳',
  PRIMARY KEY (`id`),
  KEY `idx_al_user_id` (`user_id`),
  KEY `idx_al_action` (`action`),
  KEY `idx_al_createtime` (`createtime`)
) ENGINE=InnoDB AUTO_INCREMENT=159 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wb_article_views`
--

DROP TABLE IF EXISTS `wb_article_views`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wb_article_views` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
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
  `is_logged_in` int(11) DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `idx_user_time` (`user_id`,`view_time`),
  KEY `idx_article_time` (`article_id`,`view_time`),
  KEY `idx_stats_time` (`view_time`)
) ENGINE=InnoDB AUTO_INCREMENT=472 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wb_articles`
--

DROP TABLE IF EXISTS `wb_articles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wb_articles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL COMMENT '文章标题',
  `subtitle` varchar(200) DEFAULT NULL COMMENT '文章副标题',
  `cover` varchar(100) DEFAULT NULL COMMENT '封面图片',
  `content` mediumtext NOT NULL COMMENT '内容',
  `author` int(10) NOT NULL COMMENT '作者',
  `co_authors` varchar(100) DEFAULT NULL COMMENT '共同作者',
  `category_id` int(11) DEFAULT NULL COMMENT '平台分类（审核发布时由 Admin/Editor 选择，Author 提交时可为空）',
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
  `deletetime` int(10) DEFAULT NULL COMMENT '删除时间',
  `blog_category_id` int(11) DEFAULT NULL COMMENT '文章在作者自己blog中的分类（wb_user_categories.id，可空）',
  `blog_series_id` int(11) DEFAULT NULL COMMENT '文章在作者自己blog中的系列（wb_user_series.id，可空）',
  `blog_top` int(11) NOT NULL DEFAULT '0' COMMENT '个人blog内置顶：1=置顶（焦点区优先），0=普通',
  `blog_sort` int(11) NOT NULL DEFAULT '0' COMMENT '个人blog内排序权重（大者靠前），与置顶组合生效',
  PRIMARY KEY (`id`),
  KEY `ix_articles_blog_category_id` (`blog_category_id`),
  KEY `ix_articles_blog_series_id` (`blog_series_id`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COMMENT='文章管理';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wb_articles_data`
--

DROP TABLE IF EXISTS `wb_articles_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wb_articles_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `article_id` int(11) NOT NULL,
  `likes` int(11) DEFAULT '0',
  `comments` int(11) DEFAULT '0',
  `bookmarks` int(11) DEFAULT '0',
  `shares` int(11) DEFAULT '0',
  `views` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `article_id` (`article_id`)
) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wb_blacklist`
--

DROP TABLE IF EXISTS `wb_blacklist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wb_blacklist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL COMMENT '用户ID',
  `type` varchar(20) DEFAULT NULL COMMENT '限制类型: comment/post/login',
  `reason` varchar(200) DEFAULT NULL COMMENT '拉黑原因',
  `admin_id` int(11) DEFAULT NULL COMMENT '操作管理员ID',
  `note` text COMMENT '备注',
  `expire_at` int(11) DEFAULT NULL COMMENT '过期时间，NULL表示永久',
  `status` varchar(20) DEFAULT NULL COMMENT '状态: active/inactive',
  `created_at` int(11) DEFAULT NULL COMMENT '创建时间',
  `updated_at` int(11) DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_type` (`type`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wb_categories`
--

DROP TABLE IF EXISTS `wb_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wb_categories` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL COMMENT '分类名称',
  `pid` int(10) NOT NULL COMMENT '所属分类',
  `cat_desc` varchar(300) NOT NULL COMMENT '分类描述',
  `slug` varchar(20) NOT NULL COMMENT '分类Slug',
  `image` varchar(100) DEFAULT NULL COMMENT '分类封面',
  `articles_order` enum('id desc','views desc','pubtime asc') NOT NULL DEFAULT 'id desc' COMMENT '文章排序',
  `sort` int(10) NOT NULL DEFAULT '0' COMMENT '排序',
  `createtime` int(10) NOT NULL COMMENT '创建时间',
  `updatetime` int(10) DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COMMENT='分类管理';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wb_comments`
--

DROP TABLE IF EXISTS `wb_comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wb_comments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
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
  `deletetime` int(10) DEFAULT NULL,
  `audit_status` varchar(20) NOT NULL DEFAULT 'approved' COMMENT '审核状态: pending/approved/rejected',
  `updatetime` int(11) DEFAULT NULL COMMENT '更新时间',
  `reviewed_by` int(11) DEFAULT NULL COMMENT '审核人ID',
  `reviewed_at` int(11) DEFAULT NULL COMMENT '审核时间',
  PRIMARY KEY (`id`),
  KEY `subject_id` (`subject_id`),
  KEY `pid` (`pid`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wb_config`
--

DROP TABLE IF EXISTS `wb_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wb_config` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
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
  `article_review_notification_roles` text NOT NULL COMMENT '文章审核提醒接收者角色',
  `oauth_enabled` int(11) DEFAULT NULL COMMENT '是否启用社交登录，0=禁用，1=启用',
  `enabled_oauth_providers` json DEFAULT NULL COMMENT '启用的 OAuth provider 列表',
  `sensitive_words_enabled` int(11) DEFAULT NULL COMMENT '是否启用敏感词过滤，0=关闭，1=启用',
  `article_review_enabled` int(11) NOT NULL DEFAULT '1' COMMENT '文章审核开关：1=开启（作者发布固定草稿待审核），0=关闭（作者可选发布状态）',
  PRIMARY KEY (`id`),
  KEY `idx_docbook` (`default_docbook_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wb_doc`
--

DROP TABLE IF EXISTS `wb_doc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wb_doc` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '文档ID',
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
  `seo_description` text COMMENT 'SEO描述',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_docbook_slug` (`docbook_id`,`slug`),
  KEY `idx_docbook` (`docbook_id`),
  KEY `idx_parent` (`parent_id`),
  KEY `idx_status` (`status`),
  KEY `idx_sort` (`docbook_id`,`parent_id`,`sort_order`),
  KEY `idx_author` (`author_id`),
  CONSTRAINT `wb_doc_ibfk_1` FOREIGN KEY (`docbook_id`) REFERENCES `wb_docbook` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COMMENT='文档表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wb_docbook`
--

DROP TABLE IF EXISTS `wb_docbook`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wb_docbook` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '文档书ID',
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
  `updatetime` bigint(20) NOT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `idx_slug` (`slug`),
  KEY `idx_author` (`author_id`),
  KEY `idx_sort` (`sort_order`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COMMENT='文档书表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wb_email_settings`
--

DROP TABLE IF EXISTS `wb_email_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wb_email_settings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
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
  `updated_at` int(10) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wb_member_invitations`
--

DROP TABLE IF EXISTS `wb_member_invitations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wb_member_invitations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
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
  `accepted_at` int(10) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token` (`token`),
  KEY `idx_token` (`token`),
  KEY `idx_email` (`email`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wb_nav`
--

DROP TABLE IF EXISTS `wb_nav`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wb_nav` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `label` varchar(100) NOT NULL COMMENT '显示文本',
  `nav_type` enum('sys','user') DEFAULT 'user',
  `type` enum('link','page','series','doc') NOT NULL COMMENT '类型',
  `value` varchar(100) NOT NULL COMMENT '值',
  `sort` int(10) NOT NULL DEFAULT '0' COMMENT '排序',
  `status` int(2) NOT NULL COMMENT '状态:1=显示,0=隐藏',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COMMENT='导航';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wb_notifications`
--

DROP TABLE IF EXISTS `wb_notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wb_notifications` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
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
  `created_at` int(11) DEFAULT '0' COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_read` (`user_id`,`is_read`,`created_at`),
  KEY `idx_created` (`created_at`),
  CONSTRAINT `wb_notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `wb_users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COMMENT='消息通知表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wb_pages`
--

DROP TABLE IF EXISTS `wb_pages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wb_pages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` enum('system','custom') NOT NULL DEFAULT 'custom' COMMENT '类型',
  `title` varchar(20) NOT NULL COMMENT '标题',
  `content` mediumtext NOT NULL COMMENT '内容',
  `slug` varchar(20) NOT NULL COMMENT '页面Slug',
  `image` varchar(100) DEFAULT NULL COMMENT '转发图片',
  `seo_desc` varchar(300) DEFAULT NULL COMMENT 'SEO描述',
  `status` enum('normal','hidden') NOT NULL DEFAULT 'normal' COMMENT '状态',
  `createtime` int(10) NOT NULL COMMENT '创建时间',
  `updatetime` int(10) DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COMMENT='页面管理';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wb_sensitive_words`
--

DROP TABLE IF EXISTS `wb_sensitive_words`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wb_sensitive_words` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `word` varchar(100) NOT NULL COMMENT '敏感词',
  `type` varchar(20) DEFAULT NULL COMMENT '类型: banned(禁止)/review(需审核)/replace(替换)',
  `replacement` varchar(100) DEFAULT NULL COMMENT '替换内容',
  `category` varchar(50) DEFAULT NULL COMMENT '分类: politics/porn/adult/spam/other',
  `status` varchar(20) DEFAULT NULL COMMENT '状态: active/inactive',
  `created_at` int(11) DEFAULT NULL COMMENT '创建时间',
  `created_by` int(11) DEFAULT NULL COMMENT '创建人ID',
  PRIMARY KEY (`id`),
  KEY `idx_word` (`word`),
  KEY `idx_type` (`type`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wb_series`
--

DROP TABLE IF EXISTS `wb_series`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wb_series` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL COMMENT '系列名称',
  `slug` varchar(20) NOT NULL COMMENT '系列Slug',
  `series_desc` varchar(300) DEFAULT NULL COMMENT '系列描述',
  `image` varchar(100) DEFAULT NULL COMMENT '封面图片',
  `articles_order` enum('desc','asc') NOT NULL DEFAULT 'desc' COMMENT '文章排序',
  `sort` int(11) NOT NULL DEFAULT '0',
  `createtime` int(10) NOT NULL COMMENT '创建时间',
  `updatetime` int(10) DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COMMENT='系列管理';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wb_tags`
--

DROP TABLE IF EXISTS `wb_tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wb_tags` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` enum('sys','user') NOT NULL DEFAULT 'user',
  `name` varchar(20) NOT NULL,
  `slug` varchar(20) NOT NULL,
  `tag_desc` varchar(200) DEFAULT NULL,
  `status` enum('normal','hidden') NOT NULL DEFAULT 'normal',
  `image` varchar(100) DEFAULT NULL,
  `counts` int(11) DEFAULT '0' COMMENT '下属文章数',
  `views` int(11) DEFAULT '0' COMMENT '点击查看数',
  `follows` int(11) DEFAULT '0' COMMENT '跟随关注数',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=utf8mb4 COMMENT='标签管理';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wb_user_blogs`
--

DROP TABLE IF EXISTS `wb_user_blogs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wb_user_blogs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL COMMENT '博主用户ID（一人一行）',
  `blog_name` varchar(100) DEFAULT NULL COMMENT 'blog名称（空则前台回退显示用户名）',
  `blog_description` varchar(300) DEFAULT NULL COMMENT 'blog说明',
  `impressum` text COMMENT '法律声明（blog页脚展示，部分司法辖区强制）',
  `logo` varchar(255) DEFAULT NULL COMMENT 'blog logo（建议 500x125 4:1 透明 PNG）',
  `favicon` varchar(255) DEFAULT NULL COMMENT 'blog favicon（建议 32x32/64x64 方形 PNG）',
  `social_links` json DEFAULT NULL COMMENT '社媒账号列表 JSON：[{"platform":"github","url":"..."}]',
  `homepage_layout` enum('magazine','stacked','grid') NOT NULL DEFAULT 'magazine' COMMENT '首页布局风格',
  `createtime` int(11) DEFAULT NULL COMMENT '开通时间戳（版权年份起点）',
  `updatetime` int(11) DEFAULT NULL COMMENT '更新时间戳',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_user_blogs_user_id` (`user_id`),
  KEY `ix_user_blogs_user_id` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wb_user_categories`
--

DROP TABLE IF EXISTS `wb_user_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wb_user_categories` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL COMMENT '归属博主用户ID',
  `name` varchar(100) NOT NULL COMMENT '分类名',
  `slug` varchar(50) NOT NULL COMMENT 'URL slug（同用户内唯一）',
  `sort` int(11) DEFAULT NULL COMMENT '排序权重',
  `createtime` int(11) DEFAULT NULL COMMENT '创建时间戳',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_user_categories_user_slug` (`user_id`,`slug`),
  KEY `ix_user_categories_user_id` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wb_user_navs`
--

DROP TABLE IF EXISTS `wb_user_navs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wb_user_navs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL COMMENT '归属博主用户ID',
  `label` varchar(50) NOT NULL COMMENT '导航标签',
  `type` enum('link','category','series') NOT NULL COMMENT '类型（无平台导航的系统项与页面类型）',
  `value` varchar(100) NOT NULL COMMENT 'link=URL；category/series=对应表ID',
  `sort` int(11) DEFAULT NULL COMMENT '排序权重',
  `status` int(11) DEFAULT NULL COMMENT '1=显示 0=隐藏',
  `createtime` int(11) DEFAULT NULL COMMENT '创建时间戳',
  PRIMARY KEY (`id`),
  KEY `ix_user_navs_user_id` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wb_user_oauth`
--

DROP TABLE IF EXISTS `wb_user_oauth`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wb_user_oauth` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `provider` varchar(50) NOT NULL,
  `provider_user_id` varchar(255) NOT NULL,
  `access_token` text,
  `refresh_token` text,
  `email` varchar(255) DEFAULT NULL,
  `avatar_url` varchar(500) DEFAULT NULL,
  `raw_data` json DEFAULT NULL,
  `createtime` int(11) DEFAULT NULL,
  `updatetime` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_wb_user_oauth_id` (`id`),
  KEY `ix_wb_user_oauth_user_id` (`user_id`),
  CONSTRAINT `wb_user_oauth_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `wb_users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wb_user_series`
--

DROP TABLE IF EXISTS `wb_user_series`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wb_user_series` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL COMMENT '归属博主用户ID',
  `name` varchar(100) NOT NULL COMMENT '系列名',
  `description` varchar(300) DEFAULT NULL COMMENT '系列说明',
  `slug` varchar(50) DEFAULT NULL COMMENT 'URL slug（同用户内唯一）',
  `sort` int(11) DEFAULT NULL COMMENT '排序权重',
  `createtime` int(11) DEFAULT NULL COMMENT '创建时间戳',
  PRIMARY KEY (`id`),
  KEY `ix_user_series_user_id` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wb_users`
--

DROP TABLE IF EXISTS `wb_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wb_users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL COMMENT '用户名',
  `password` varchar(72) DEFAULT NULL,
  `salt` varchar(64) DEFAULT NULL,
  `full_name` varchar(20) DEFAULT NULL COMMENT '全名',
  `profile_image` varchar(1000) DEFAULT NULL COMMENT '头像',
  `profile_tagline` varchar(100) DEFAULT NULL COMMENT '简介标语',
  `location` varchar(100) DEFAULT NULL COMMENT '所在地',
  `gender` tinyint(2) DEFAULT '1' COMMENT '性别:0=女性,1=男性',
  `birthday` int(10) DEFAULT NULL COMMENT '生日',
  `school` varchar(100) DEFAULT NULL,
  `profile_bio` text,
  `tech_stack` varchar(300) DEFAULT NULL COMMENT '技术栈',
  `available_for` varchar(300) DEFAULT NULL COMMENT '适用于',
  `social_profiles` json DEFAULT NULL COMMENT '社交资料',
  `email` varchar(50) DEFAULT NULL COMMENT '邮件',
  `mobile` varchar(11) DEFAULT NULL COMMENT '手机',
  `role` enum('Admin','Editor','Contributor','User','Author') NOT NULL DEFAULT 'User' COMMENT '角色',
  `visibility` enum('Public','Private') NOT NULL DEFAULT 'Public' COMMENT '可见性',
  `status` enum('normal','block') NOT NULL DEFAULT 'normal' COMMENT '状态',
  `join_ip` varchar(45) DEFAULT NULL,
  `login_ip` varchar(45) DEFAULT NULL,
  `login_time` int(10) DEFAULT NULL,
  `createtime` int(10) NOT NULL COMMENT '创建时间',
  `updatetime` int(10) DEFAULT NULL COMMENT '更新时间',
  `notification_check_at` int(11) DEFAULT NULL COMMENT '最后检查通知时间',
  `privacy_show_bookmarks` int(11) DEFAULT '1' COMMENT '是否展示收藏',
  `privacy_show_likes` int(11) DEFAULT '1' COMMENT '是否展示点赞',
  `privacy_show_comments` int(11) DEFAULT '1' COMMENT '是否展示评论',
  `privacy_show_views` int(11) DEFAULT '1' COMMENT '是否展示浏览',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COMMENT='用户管理';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wb_users_data`
--

DROP TABLE IF EXISTS `wb_users_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wb_users_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` enum('FOLLOW_TAG','FOLLOW_USER','BOOKMARK','LIKE','SHARE') NOT NULL,
  `user_id` int(11) NOT NULL,
  `target_id` int(11) NOT NULL COMMENT '目标id:文章标签用户',
  `status` tinyint(4) NOT NULL DEFAULT '1' COMMENT '状态:0=隐藏,1=显示',
  `createtime` int(10) NOT NULL,
  `updatetime` int(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-18 15:36:10

-- 初始模板数据（无真实用户数据）
INSERT INTO `alembic_version` (`version_num`) VALUES ('f7a3c1e9d4b2');

INSERT INTO `wb_config` (`id`, `site_title`, `site_logo`, `site_favicon`, `language`, `dark_mode`, `disable_comment`, `default_homepage`, `default_docbook_id`, `doc_subdomain`, `doc_comment`, `message_push_method`, `polling_interval`, `footer_config`, `enable_register`, `register_role`, `enable_article_review_notification`, `article_review_notification_roles`) VALUES
(1, 'WOW Blog', '/wow_blog_logo.svg', '/favicon.ico', 'zh-CN', 'system', 0, 'blog', NULL, NULL, 1, 'websocket', 30, '{\"logo_url\": \"/wow_blog_logo.svg\", \"site_description\": \"一个具有社交功能的团队Blog系统，并能创建专业的文档系统。\", \"social_media\": [{\"icon\": \"ant-design:zhihu-circle-filled\", \"url\": \"http://www.zhihu.com/user/123456\"}, {\"icon\": \"mage:tiktok-circle\", \"url\": \"http://www.douyin.com/user/231231231\"}, {\"icon\": \"simple-icons:xiaohongshu\", \"url\": \"http://www.xiaohongshu.com/user/12312312\"}, {\"icon\": \"ri:weibo-fill\", \"url\": \"http://weibo.com/\"}, {\"icon\": \"streamline-ultimate:bilibili-logo-bold\", \"url\": \"http://www.bilibili.com/\"}], \"nav_groups\": [{\"group_name\": \"产品\", \"links\": [{\"name\": \"Blog系统\", \"url\": \"\"}, {\"name\": \"文档系统\", \"url\": \"\"}]}, {\"group_name\": \"公司\", \"links\": [{\"name\": \"服务协议\", \"url\": \"\"}, {\"name\": \"隐私协议\", \"url\": \"\"}]}, {\"group_name\": \"联系我们\", \"links\": [{\"name\": \"contact@company.com\", \"url\": \"\"}]}], \"copyright\": \"WOW Blog\", \"icp_info\": [{\"text\": \"津ICP备 12345-5号\", \"url\": \"http://ww.mii.org.cn/\"}]}', 1, 'User', 1, '[\"Admin\",\"Editor\"]');

INSERT INTO `wb_email_settings` (`id`, `provider`, `smtp_host`, `smtp_port`, `smtp_user`, `smtp_pass`, `use_tls`, `from_email`, `from_name`, `is_active`, `created_at`, `updated_at`) VALUES
(1, 'gmail', 'smtp.gmail.com', 587, NULL, NULL, 1, 'noreply@example.com', 'Blog Notification', 0, 1781683023, 1781683023),
(2, 'outlook', 'smtp.office365.com', 587, NULL, NULL, 1, 'noreply@example.com', 'Blog Notification', 0, 1781683023, 1781683023),
(3, 'qq', 'smtp.qq.com', 465, NULL, NULL, 1, 'noreply@example.com', 'Blog Notification', 0, 1781683023, 1782704831);

INSERT INTO `wb_nav` (`id`, `label`, `nav_type`, `type`, `value`, `sort`, `status`) VALUES
(1, '首页', 'sys', 'link', '/', 0, 1),
(2, '分类', 'sys', 'link', 'category', 1, 1),
(3, '系列', 'sys', 'link', 'series', 2, 1),
(4, '文档', 'sys', 'link', 'doc', 3, 1),
(5, '关于我们', 'user', 'page', '1', 5, 1);

INSERT INTO `wb_pages` (`id`, `type`, `title`, `content`, `slug`, `image`, `seo_desc`, `status`, `createtime`, `updatetime`) VALUES
(1, 'custom', 'About Us', '<h1>About Us</h1><p></p><p>This is a custom page.</p>', 'aboutus', NULL, NULL, 'hidden', 1757043426, 1757043497);

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

INSERT INTO `wb_users` (`id`, `username`, `password`, `salt`, `full_name`, `profile_image`, `profile_tagline`, `location`, `gender`, `birthday`, `school`, `profile_bio`, `tech_stack`, `available_for`, `social_profiles`, `email`, `mobile`, `role`, `visibility`, `status`, `join_ip`, `login_ip`, `login_time`, `createtime`, `updatetime`, `notification_check_at`, `privacy_show_bookmarks`, `privacy_show_likes`, `privacy_show_comments`, `privacy_show_views`) VALUES
(1, 'admin', '$2b$12$nkM0TZz3RCFQWzTGcBMKduXXIeyugRsJpnAqjWmXABbx6F7aeNId6', NULL, 'Blog Admin', NULL, '', '', 1, NULL, '', '', NULL, '', NULL, 'yourname@example.com', '', 'Admin', 'Public', 'normal', '', '127.0.0.1', 1783993595, 1755399562, NULL, NULL, 1, 1, 1, 1);
