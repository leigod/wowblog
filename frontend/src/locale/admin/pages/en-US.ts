export default {
  title: 'Pages',
  title_info: 'Create and manage your pages',
  btn: {
    add: 'Create a new page'
  },
  table: {
    name: 'Name',
    slug: 'Slug',
    description: 'Description',
    actions: 'Actions',
    visible: 'Visible',
    hidden: 'Hidden'
  },
  action: {
    update: {
      sort: {
        success: 'Sort updated successfully',
        error: 'Failed to update sort'
      }
    },
    delete: {
      confirm: 'Are you sure to delete this page?',
      success: 'Deleted page {pagename} successfully!',
      error: 'Failed to delete page {pagename}.'
    },
    empty: {
      title: 'No pages yet',
      description: 'Create your first page to get started'
    },
    show: 'Show page',
    hide: 'Hide page',
    toggle: {
      success: '{action} page "{pagename}" successfully!',
      error: 'Failed to {action} page "{pagename}"'
    }
  },
  page: {
    create: {
      title: 'Create new page',
      description: 'Create a new page for your blog.',
      success: 'Page created successfully!',
      error: 'Failed to create page.',
      btn: 'Create Page'
    },
    edit: {
      title: 'Edit page',
      description: 'Edit the details of an existing page.',
      success: 'Page updated successfully!',
      error: 'Failed to update page.',
      btn: 'Update Page'
    },
    form: {
      title: 'Page Name',
      title_placeholder: 'Enter page name',
      slug: 'Page Slug',
      slug_placeholder: 'page-path',
      slug_helptip:
        'E.g. javascript-basics. Only lowercase alphanumeric and "-","_" are allowed. Only include the path, not the domain name.',
      content: 'Page Content',
      content_placeholder: 'Click to open the editor and add content via WYSIWYG.',
      content_edit: 'Click to edit content',
      cover: 'Page Cover',
      cover_info: 'Image for social media sharing.',
      cover_helptip:
        'This image will appear when your page is shared on Twitter, Facebook and other social media websites.',
      upload: 'Drop file here or <em>click to upload</em><br />',
      upload_helptip:
        'Recommended dimension: 1200 x 420 px, jpg/png files with a size less than 2M',
      validate: 'Please complete the page information before submitting.',
      uploaderror: {
        format: 'Please upload jpg/png format images.',
        size: 'Image size cannot exceed 2MB.',
        default: 'Failed to upload image. Please try again.'
      },
      uploadsuccess: 'Image uploaded successfully!',
      seodesc: 'SEO Description',
      seodesc_placeholder: 'Enter a description for your page.',
      seodesc_helptip:
        'Best descriptions are under 160 chars. Search engines will show this description in search results. If not present, "Content" will be used.'
    },
    validate: {
      title: 'Please enter the page name.',
      title_length: 'Page name length must be between 2 and 100 characters.',
      slug: 'Please enter the page slug.',
      slug_format: 'Slug can only contain letters, numbers, hyphens, and underscores.',
      slug_length: 'Slug length must be between 2 and 100 characters.',
      content: 'Please enter the page content.',
      seodesc_length: 'SEO description length must be between 50 and 160 characters.'
    }
  }
}
