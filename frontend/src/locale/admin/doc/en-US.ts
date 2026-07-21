export default {
  title: 'Document Management',
  title_info: 'Manage documents in your docbook',

  // Back button
  back_to_list: 'Back to DocBooks',
  btn_create: 'New Document',

  // Status tabs
  status_tabs: {
    all: 'All',
    published: 'Published',
    draft: 'Draft',
    hidden: 'Hidden'
  },

  // Status values
  status: {
    published: 'Published',
    draft: 'Draft',
    hidden: 'Hidden'
  },

  // Search and filter
  search_placeholder: 'Search documents...',
  filter_parent_placeholder: 'Filter by parent',
  filter_parent_all: 'All',
  parent_select_placeholder: 'Select parent document (optional)',
  top_level_doc: '(Top Level)',

  // Table columns
  table: {
    title: 'Title',
    slug: 'URL Slug',
    level: 'Level',
    sort_order: 'Sort',
    view_count: 'Views',
    comment_count: 'Comments',
    update_time: 'Updated',
    actions: 'Actions'
  },

  // Action buttons
  actions: {
    view: 'View',
    edit: 'Edit',
    delete: 'Delete'
  },

  // Empty state
  empty: {
    title: 'No Documents',
    description: 'Click "New Document" to create your first document'
  },

  // Dialog
  dialog: {
    create_title: 'New Document',
    edit_title: 'Edit Document',

    form: {
      title: 'Title',
      title_placeholder: 'Enter document title',
      slug: 'URL Slug',
      slug_placeholder: 'Enter URL slug',
      slug_prefix: '/{slug}/',
      parent: 'Parent Document',
      sort_order: 'Sort Order',
      status: 'Status',
      excerpt: 'Excerpt',
      excerpt_placeholder: 'Document excerpt (optional)',
      content: 'Content',
      content_placeholder: 'Start writing your document content...'
    },

    btn_cancel: 'Cancel',
    btn_confirm: 'Confirm'
  },

  // Confirm delete
  confirm_delete: {
    title: 'Confirm Delete',
    message: 'Are you sure you want to delete the document "{title}"?{hasChildren}',
    has_children: ' Child documents will also be deleted.',
    confirm_btn: 'Confirm',
    cancel_btn: 'Cancel'
  },

  // Form validation
  validation: {
    title_required: 'Please enter document title',
    title_too_long: 'Title cannot exceed 255 characters',
    slug_required: 'Please enter URL slug',
    slug_too_long: 'URL slug cannot exceed 255 characters',
    slug_invalid: 'Can only contain lowercase letters, numbers and hyphens'
  },

  // Messages
  message: {
    load_failed: 'Failed to load',
    docbook_not_found: 'DocBook not found',
    load_docbook_failed: 'Failed to load DocBook',
    create_success: 'Created successfully',
    update_success: 'Updated successfully',
    delete_success: 'Deleted successfully',
    delete_failed: 'Failed to delete',
    operation_failed: 'Operation failed'
  },

  // Level label
  level_label: 'Lv'
}
