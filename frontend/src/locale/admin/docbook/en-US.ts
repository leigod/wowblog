export default {
  title: 'DocBook Management',
  title_info: 'Manage your document collections',
  search_placeholder: 'Search docbooks...',
  btn_create: 'New DocBook',

  table: {
    cover: 'Cover',
    name: 'Name',
    doc_count: 'Docs',
    visibility: 'Visibility',
    sort_order: 'Sort',
    update_time: 'Updated',
    actions: 'Actions'
  },

  actions: {
    manage_docs: 'Manage Docs',
    edit: 'Edit',
    delete: 'Delete'
  },

  visibility: {
    public: 'Public',
    private: 'Private'
  },

  theme: {
    default: 'Default',
    minimal: 'Minimal',
    dark: 'Dark'
  },

  empty: {
    title: 'No DocBooks',
    description: 'Click "New DocBook" to create your first document collection'
  },

  dialog: {
    create_title: 'New DocBook',
    edit_title: 'Edit DocBook',

    form: {
      name: 'Name',
      name_placeholder: 'Enter docbook name',
      slug: 'URL Slug',
      slug_placeholder: 'Enter URL slug, e.g.: my-docs',
      slug_prefix: '/docs/',
      description: 'Description',
      description_placeholder: 'Enter docbook description',
      cover: 'Cover Image',
      icon: 'Icon',
      icon_placeholder: 'Icon (emoji or icon name)',
      settings: 'Settings',
      visibility: 'Visibility',
      visibility_public: 'Public',
      visibility_private: 'Private',
      show_sidebar: 'Show Sidebar',
      allow_comment: 'Allow Comments',
      allow_search: 'Allow Search',
      theme: 'Theme',
      theme_placeholder: 'Select theme',
      sort_order: 'Sort Order'
    },

    cover_upload: {
      click_to_upload: 'Click to upload cover',
      upload_tip: 'Support JPG, PNG, WebP formats, max 2MB',
      uploading: 'Uploading...',
      remove_cover: 'Remove Cover'
    },

    btn_cancel: 'Cancel',
    btn_confirm: 'Confirm'
  },

  confirm_delete: {
    title: 'Confirm Delete',
    message: 'Are you sure you want to delete the docbook "{name}"? All documents will also be deleted. This action cannot be undone.',
    confirm_btn: 'Confirm',
    cancel_btn: 'Cancel'
  },

  validation: {
    name_required: 'Please enter docbook name',
    name_too_long: 'Name cannot exceed 100 characters',
    slug_required: 'Please enter URL slug',
    slug_too_long: 'URL slug cannot exceed 100 characters',
    slug_invalid: 'Can only contain lowercase letters, numbers and hyphens'
  },

  message: {
    load_failed: 'Failed to load',
    create_success: 'Created successfully',
    update_success: 'Updated successfully',
    delete_success: 'Deleted successfully',
    delete_failed: 'Failed to delete',
    upload_success: 'Cover uploaded successfully',
    upload_failed: 'Upload failed',
    operation_failed: 'Operation failed',
    image_format_error: 'Only JPG/PNG/WebP format images are allowed!',
    image_size_error: 'Image size cannot exceed 2MB!'
  }
}
