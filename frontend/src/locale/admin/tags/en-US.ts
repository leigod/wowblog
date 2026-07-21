export default {
  title: 'Tags',
  title_info: 'Create and manage content tags',
  btn: {
    add: 'Create a new tag'
  },
  table: {
    name: 'Name',
    slug: 'Slug',
    description: 'Description',
    cover: 'Cover',
    visibility: 'Visibility',
    actions: 'Actions',
    no_cover: 'None'
  },
  action: {
    update: {
      sort: {
        success: 'Sort updated successfully',
        error: 'Failed to update sort'
      }
    },
    delete: {
      confirm: 'Are you sure to delete tag "{tagname}"?',
      title: 'Delete tag',
      btn: {
        confirm: 'Delete',
        cancel: 'Cancel'
      },
      success: 'Deleted tag {tagname} successfully!',
      error: 'Failed to delete tag {tagname}.'
    },
    empty: {
      title: 'No tags yet',
      description: 'Create your first tag to get started'
    },
    search: {
      placeholder: 'Search tags by name'
    },
    show: 'Show tag',
    hide: 'Hide tag',
    toggle: {
      success: '{action} "{tagname}" successfully!',
      error: 'Failed to {action} "{tagname}"'
    }
  },
  drawer: {
    create: {
      title: 'Create new tag',
      description: 'Create a new tag for your blog.',
      success: 'Tag created successfully!',
      error: 'Failed to create tag.',
      btn: 'Create Tag'
    },
    edit: {
      title: 'Edit tag',
      description: 'Edit the details of an existing tag.',
      success: 'Tag updated successfully!',
      error: 'Failed to update tag.',
      btn: 'Update Tag'
    },
    form: {
      name: 'Tag Name',
      name_placeholder: 'Enter Tag name',
      slug: 'Tag Slug',
      slug_placeholder: 'tag-path',
      slug_helptip:
        'E.g. javascript-basics. Only lowercase alphanumeric and "-","_" are allowed. Only include the path, not the domain name.',
      type: 'Tag type',
      type_placeholder: 'Select tag type',
      type_sys: 'System tag',
      type_user: 'User tag',
      description: 'Tag Description',
      description_placeholder: 'Enter Tag description',
      status: 'Visibility',
      status_visible: 'Visible',
      status_hidden: 'Hidden',
      cover: 'Tag Cover',
      cover_info: 'Upload a cover image for the tag.',
      cover_helptip:
        'This image will appear when your page is shared on Twitter, Facebook and other social media websites.',
      upload: 'Drop file here or <em>click to upload</em><br />',
      upload_helptip: 'Recommended dimension: 640 x 640 px, jpg/png files with a size less than 2M',
      validate: 'Please complete the page information before submitting.',
      uploaderror: {
        format: 'Please upload jpg/png format images.',
        size: 'Image size cannot exceed 2MB.',
        default: 'Failed to upload image. Please try again.'
      },
      uploadsuccess: 'Image uploaded successfully!'
    },
    validate: {
      name: 'Please enter the tag name.',
      name_length: 'Tag name length must be between 2 and 30 characters.',
      slug: 'Please enter the tag slug.',
      slug_format: 'Slug can only contain letters, numbers, hyphens, and underscores.',
      slug_length: 'Slug length must be between 2 and 30 characters.',
      type: 'Please select the tag type.'
    }
  }
}
