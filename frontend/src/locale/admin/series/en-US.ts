export default {
  title: 'Series',
  title_info: 'Create and manage your series',
  btn: {
    add: 'Create new series',
    view: 'View series'
  },
  action: {
    update: {
      sort: {
        success: 'Sort updated successfully',
        error: 'Failed to update sort'
      }
    },
    delete: {
      confirm: 'Are you sure to delete this series?',
      success: 'Series deleted successfully',
      error: 'Failed to delete series'
    },
    empty: {
      title: 'No series yet',
      description: 'Create your first series to organize your articles'
    }
  },
  page: {
    create: {
      title: 'Create new series',
      description: 'Create a new series for your blog.',
      success: 'Series created successfully!',
      error: 'Failed to create series.',
      btn: 'Create Series'
    },
    edit: {
      title: 'Edit series',
      description: 'Edit the details of an existing series.',
      success: 'Series updated successfully!',
      error: 'Failed to update series.',
      btn: 'Update Series'
    },
    form: {
      name: 'Series Name',
      name_placeholder: 'Enter series name',
      slug: 'Series Slug',
      slug_placeholder: 'series-path',
      slug_helptip:
        'E.g. javascript-basics. Only lowercase alphanumeric and "-","_" are allowed. Only include the path, not the domain name.',
      description: 'Series Description',
      description_placeholder: 'Enter series description',
      cover: 'Series Cover',
      upload: 'Drop file here or <em>click to upload</em><br />',
      upload_helptip: 'Recommended dimension: 800 x 800 px, jpg/png files with a size less than 2M',
      validate: 'Please complete the series information before submitting.',
      uploaderror: {
        format: 'Please upload jpg/png format images.',
        size: 'Image size cannot exceed 2MB.',
        default: 'Failed to upload image. Please try again.'
      },
      uploadsuccess: 'Image uploaded successfully!',
      cover_helptip: 'Add a cover image for your series.',
      order: 'Sort article in the series',
      order_helptip: 'Sort your article in the series and show by',
      order_oldest: 'Oldest first',
      order_newest: 'Newest first'
    },
    validate: {
      name: 'Please enter the series name.',
      name_length: 'Series name length must be between 2 and 50 characters.',
      slug: 'Please enter the series slug.',
      slug_format: 'Slug can only contain letters, numbers, hyphens, and underscores.',
      slug_length: 'Slug length must be between 2 and 100 characters.',
      description: 'Please enter the series description.',
      article_sort: 'Please select the article sort order.'
    },
    load: {
      success: 'Series data loaded successfully.',
      error: 'Failed to load series data. Please try again later.'
    }
  }
}
