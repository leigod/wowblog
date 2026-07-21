import { Sort } from '@element-plus/icons-vue'

// 分类管理相关语言（英文）
export default {
  title: 'Category Management',
  title_info: 'Manage your blog categories here.',
  btn: {
    add: 'Add New Category',
    edit: 'Edit Category',
    delete: 'Delete Category'
  },
  table: {
    head: {
      name: 'Name',
      slug: 'Slug',
      description: 'Description',
      parent: 'Parent',
      cover: 'Cover',
      order: 'Article Order',
      order_new: 'Latest first',
      order_hot: 'Hotest first',
      order_pubtime: 'Oldest pubtime first',
      weight: 'Weight',
      sort: 'Sort',
      actions: 'Actions'
    },
    no_parent: 'No Parent',
    no_cover: 'None'
  },
  form: {
    name: 'Category Name',
    slug: 'Category Slug',
    description: 'Category Description',
    parent: 'Parent Category'
  },
  action: {
    delete: {
      title: 'Delete Category',
      confirmbtn: 'Delete',
      cancelbtn: 'Cancel',
      confirm: 'Are you sure you want to delete this category?',
      success: 'Category deleted successfully.',
      error: 'Failed to delete category.'
    },
    sort: {
      success: 'Category articles sorted successfully.',
      error: 'Failed to sort category articles.'
    }
  },
  page: {
    create: {
      title: 'Create Category',
      description: 'Create a new category for your blog.',
      success: 'Category created successfully!',
      error: 'Failed to create category.',
      btn: 'Create Category'
    },
    edit: {
      title: 'Edit Category',
      description: 'Edit the details of an existing category.',
      success: 'Category updated successfully!',
      error: 'Failed to update category.',
      btn: 'Update Category'
    },
    form: {
      name: 'Category Name',
      name_placeholder: 'Enter category name',
      slug: 'Category Slug',
      slug_placeholder: 'Enter category slug',
      slug_helptip:
        'E.g. javascript-basics. Only lowercase alphanumeric and "-","_" are allowed. Only include the path, not the domain name.',
      description: 'Category Description',
      description_placeholder: 'Enter category description',
      parent: 'Parent Category',
      parent_placeholder: 'Please select parent category',
      parent_default: 'No parent (top-level category)',
      cover: 'Category Cover',
      upload: 'Drop file here or <em>click to upload</em><br />',
      upload_helptip:
        'Recommended dimension: 1200 x 420 px, jpg/png files with a size less than 2M',
      validate: 'Please complete the category information before submitting.',
      uploaderror: {
        format: 'Please upload jpg/png format images.',
        size: 'Image size cannot exceed 2MB.',
        default: 'Failed to upload image. Please try again.'
      },
      uploadsuccess: 'Image uploaded successfully!',
      cover_helptip: 'Add a cover image for your category.',
      order: 'Sort article in the category',
      order_helptip: 'Sort your article in the category and show by'
    },
    validate: {
      name: 'Please enter the category name.',
      name_length: 'Category name length must be between 2 and 50 characters.',
      slug: 'Please enter the category slug.',
      slug_format: 'Slug can only contain letters, numbers, hyphens, and underscores.',
      slug_length: 'Slug length must be between 2 and 100 characters.',
      description: 'Please enter the category description.',
      article_sort: 'Please select the article sort order.'
    },
    load: {
      success: 'Category data loaded successfully.',
      error: 'Failed to load category data. Please try again later.'
    }
  }
}
