import { frontLogoutApi } from '@/api/services/auth'

export default {
  title: 'Appearance Management',

  // Tabs
  tabs: {
    general: 'General',
    footer: 'Footer'
  },

  // Form items
  default_language: 'Default Language',
  default_language_hint:
    'Website default language, users can switch languages on article pages. Settings are saved locally and will be applied on next visit',

  dark_mode: 'Dark Mode',
  dark_mode_system: 'Follow System',
  dark_mode_dark: 'Dark Mode',
  dark_mode_light: 'Light Mode',
  dark_mode_hint:
    'Website dark mode global setting, default setting for first-time visitors. Users can switch manually, and their preference is saved locally for future visits',

  default_homepage_type: 'Default Homepage Type',
  homepage_type_blog: 'Blog',
  homepage_type_doc: 'Docs',
  default_homepage_hint:
    'Set the default homepage type. Select "Blog" to display blog list on homepage, or "Docs" to display the specified docbook',

  default_docbook: 'Default DocBook',
  default_docbook_hint:
    'When default homepage type is set to "Docs", the homepage will display this docbook content',
  no_docbook_hint: 'No docbooks available, please create a docbook first',

  doc_subdomain: 'Docs Subdomain',
  doc_subdomain_placeholder: 'e.g., docs.example.com',
  doc_subdomain_hint:
    'Set the subdomain for the docs module. After configuration, the docs module can be accessed via an independent subdomain. Leave empty to use the main domain path',

  // Footer Settings
  footer: {
    logo: 'Site Logo',
    logo_url: 'Logo URL',
    logo_url_placeholder: 'Enter logo image URL',
    logo_url_hint: 'Logo image URL displayed in the website footer',

    site_description: 'Site Description',
    site_description_placeholder: 'Enter site description',
    site_description_hint: 'Brief description displayed in the footer to introduce the website',

    social_media: 'Social Media',
    select_icon: 'Select Icon',
    url_placeholder: 'Enter URL',
    social_media_hint: 'Add social media links, icons will be selected from Iconify icon library',
    add_social: 'Add Social Media',
    remove: 'Remove',

    nav_groups: 'Navigation Groups',
    group_name_placeholder: 'Group Name',
    nav_groups_hint: 'Create navigation link groups, each group can contain multiple links',
    add_nav_group: 'Add Group',
    add_link: 'Add Link',
    link_name_placeholder: 'Display Text',

    copyright: 'Copyright',
    copyright_placeholder: 'Enter copyright, e.g., © 2024 MySite',
    copyright_hint: 'Copyright notice displayed in the website footer',

    icp_info: 'ICP Information',
    icp_text_placeholder: 'e.g., 京ICP备12345678号',
    icp_info_hint: 'Add website ICP filing information, multiple filing numbers can be displayed',
    add_icp: 'Add ICP Info'
  },

  save_button: 'Save Settings',

  // Language options
  languages: {
    'zh-CN': '简体中文',
    'en-US': 'English'
  },

  // Messages
  message: {
    save_success: 'Settings saved successfully!',
    save_failed: 'Save failed',
    fetch_docbooks_failed: 'Failed to fetch docbook list',
    load_config_failed: 'Failed to load site configuration'
  }
}
