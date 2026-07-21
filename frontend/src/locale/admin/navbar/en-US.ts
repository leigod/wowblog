// 仪表盘相关语言（英文）
export default {
  title: 'Navbar',
  title_info: 'Add navigation menus and page links',
  btn: {
    add: 'Add Navbar Item'
  },
  table: {
    sort: 'Sort',
    label: 'Label',
    type: 'Type',
    value: 'Value',
    actions: 'Actions'
  },
  form: {
    add_title: 'Add Navbar Item',
    edit_title: 'Edit Navbar Item',
    label: 'Item Label',
    label_placeholder: 'Enter navbar item label',
    type: 'Type',
    type_placeholder: 'Select link type',
    type_link: 'Link',
    type_page: 'Page',
    type_series: 'Series',
    type_doc: 'Doc',
    value: 'Value',
    value_placeholder: 'Enter URL with http:// or https://',
    page: 'Page',
    page_placeholder: 'Select a page',
    series: 'Series',
    series_placeholder: 'Select a series',
    doc: 'Doc',
    doc_placeholder: 'Select a document'
  },
  validation: {
    general: 'Please enter value',
    label: 'Please enter item label',
    label_length: 'Label cannot exceed 50 characters',
    type: 'Please select link type',
    value: 'Value is required',
    link: 'Please enter a valid URL with http:// or https://'
  },
  action: {
    load: {
      page: 'Loading pages...',
      series: 'Loading series...'
    },
    update: {
      sort: {
        success: 'Sort updated successfully',
        error: 'Failed to update sort'
      },
      navbar: {
        success: 'Navbar item updated successfully',
        error: 'Failed to update navbar item'
      }
    },
    delete: {
      navbar: {
        success: 'Navbar item deleted successfully',
        error: 'Failed to delete navbar item'
      }
    },
    create: {
      navbar: {
        success: 'Navbar item created successfully',
        error: 'Failed to create navbar item'
      }
    }
  },
  empty: {
    title: 'No navbar items found',
    description: 'Add your first navbar item to get started'
  }
}
