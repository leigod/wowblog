// 文章管理相关语言（英文）
export default {
  list: {
    title: 'Articles and drafts',
    subtitle: 'Status overview of your articles and drafts',
    tab: {
      all: 'All',
      published: 'Published',
      draft: 'Draft',
      scheduled: 'Scheduled',
      deleted: 'Deleted'
    },
    search_placeholder: 'Search articles',
    author_search_placeholder: 'Search authors',
    tag_search_placeholder: 'Search tags',
    filter: 'Filter',
    filter_articles: 'Filter Articles',
    authors: 'Authors',
    tags: 'Tags',
    date: {
      tab_title: 'Date',
      previous_day: 'Previous day',
      past_3_day: 'Past 3 days',
      past_week: 'Past week',
      past_month: 'Past month',
      custome_date: 'Custom Date',
      custome_date_range: 'Custom Date Range',
      start_date: 'Start Date',
      end_date: 'End Date'
    },
    table: {
      head: {
        title: 'Title',
        slug: 'Slug',
        top: 'Top',
        featured: 'Featured',
        recommend: 'Recommend',
        actions: 'Actions'
      },
      menu: {
        pin_to_blog: 'Pin to blog',
        unpin: 'Unpin',
        delete: 'Delete',
        recommend_to_home: 'Recommend to home',
        un_recommend: 'Un-recommend',
        featured: 'Featured',
        un_featured: 'Un-featured',
        preview: 'Preview',
        cancel: 'Cancel',
        restore: 'Restore',
        permanently_delete: 'Permanently delete'
      }
    },
    empty: {
      published: {
        title: 'No published articles found',
        description: 'Publish your first article to get started.'
      },
      draft: {
        title: 'No draft articles found',
        description: 'Create a new draft to start writing.'
      },
      scheduled: {
        title: 'No scheduled articles found',
        description: 'Schedule a new article to publish at a later time.'
      },
      deleted: {
        title: 'No deleted articles found',
        description: 'Deleted articles are stored here. Restore them to make them visible again.'
      },
      default: {
        title: 'No articles found',
        description: 'Create a new article to get started.'
      }
    }
  },
  btn: {
    publish: 'Publish',
    preview: 'Preview',
    addcover: 'Add Cover',
    addsubtitle: 'Add Subtitle',
    update: 'Update'
  },
  text: {
    article_editor: 'Article Editor'
  },
  publishform: {
    category: 'Category',
    series: 'Series',
    status: 'Publish Status',
    status_published: 'Published',
    status_draft: 'Draft',
    status_scheduled: 'Scheduled',
    publish_time: 'Publish Time',
    author: 'Author',
    author_tooltip:
      'Author changes will take effect after the article is published.<br>Until then, your article will remain in draft. Once published,<br/>the new author will be able to edit it.',
    change_author: 'Change Author',
    co_author: 'Co-Author',
    co_author_addbtn: 'Add Co-Author',
    co_author_tooltip:
      'Select up to 4 co-authors from your team. <br>Co-authors will not be able to edit the article but are listed as collaborators in draft preview and article pages.',
    slug: 'Article Slug',
    slug_placeholder: 'Please enter the article slug',
    tags: 'Tags',
    tags_placeholder: 'Please enter the tags',
    seo_title: 'SEO Title',
    seo_title_placeholder: 'Please enter the SEO title',
    seo_description: 'SEO Description',
    seo_description_placeholder: 'Please enter the SEO description',
    og_image: 'Custom OG Image',
    og_image_helptip:
      'Upload an image to show when your article appears online or on social media. If there’s no image, the cover image will be used instead.',
    og_image_placeholder:
      'Recommended dimension: 1200 x 630 px, jpg/png files with a size less than 2M',
    table: 'Table of Contents',
    table_helptip: 'Generate a table of contents for your article.',
    disable_comments: 'Disable Comments',
    disable_comments_helptip: 'This will hide the comments section below your article.'
  },
  dialog: {
    delete: {
      title: 'Delete Article',
      description: 'Are you sure you want to delete this article? This action cannot be undone.',
      confirm: 'Delete',
      cancel: 'Cancel',
      success: 'Article deleted successfully.',
      error: 'Failed to delete article.'
    },
    update: {
      status: {
        success: 'Article status updated successfully.',
        error: 'Failed to update article status.'
      },
      success: 'Article updated successfully.',
      error: 'Failed to update article.'
    }
  }
}
