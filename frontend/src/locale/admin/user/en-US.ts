export default {
  title: 'User Management',
  title_info: 'Manage all registered users in the system',
  section_title: 'User List',
  search_placeholder: 'Search username or email',
  status_filter: {
    all: 'All',
    normal: 'Normal',
    disabled: 'Disabled'
  },
  table: {
    user: 'User',
    email: 'Email',
    role: 'Role',
    status: 'Status',
    articles_count: 'Articles',
    comments_count: 'Comments',
    actions: 'Actions'
  },
  roles: {
    Admin: 'Admin',
    Editor: 'Editor',
    Author: 'Author',
    Contributor: 'Contributor',
    User: 'User'
  },
  actions: {
    view: 'View',
    send_message: 'Message',
    more: 'More',
    edit_role: 'Edit Role',
    reset_password: 'Reset Password',
    delete_user: 'Delete User',
    view_profile: 'View Profile'
  },
  drawer: {
    title: 'User Details',
    view_profile: 'View Profile'
  },
  detail_section: {
    basic_info: 'Basic Information',
    email: 'Email',
    mobile: 'Mobile',
    gender: 'Gender',
    register_time: 'Register Time',
    status: 'Status',
    statistics: 'Statistics',
    articles_count: 'Articles',
    comments_count: 'Comments',
    bio: 'Bio',
    gender_male: 'Male',
    gender_female: 'Female',
    gender_unknown: '-'
  },
  message_dialog: {
    title: 'Send Message',
    recipient: 'Recipient',
    message_type: 'Message Type',
    type_system: 'System Notification',
    type_reminder: 'Reminder',
    message_title: 'Title',
    title_placeholder: 'Please enter message title',
    content: 'Content',
    content_placeholder: 'Please enter message content',
    send: 'Send',
    cancel: 'Cancel',
    warning: 'Please fill in message title and content'
  },
  role_dialog: {
    title: 'Edit User Role',
    user: 'User',
    role: 'Role',
    confirm: 'Confirm',
    cancel: 'Cancel'
  },
  reset_password_confirm: {
    title: 'Reset Password Confirmation',
    message: 'Are you sure you want to reset password for user {name}? The new password will be sent to the user email.',
    confirm: 'Confirm',
    cancel: 'Cancel'
  },
  delete_user_confirm: {
    title: 'Delete User Confirmation',
    message: 'Are you sure you want to delete user {name}? This action cannot be undone, all user data will be deleted.',
    confirm: 'Confirm',
    cancel: 'Cancel'
  },
  message: {
    send_success: 'Message sent successfully',
    send_failed: 'Failed to send message',
    status_update_success: 'User {username} status updated to {status}',
    status_update_failed: 'Failed to update status',
    role_update_success: 'User role updated successfully',
    role_update_failed: 'Failed to update role',
    password_reset_success: 'Password reset successfully, new password has been sent to user email',
    password_reset_failed: 'Failed to reset password',
    delete_success: 'User deleted successfully',
    delete_failed: 'Failed to delete user',
    load_failed: 'Failed to load user list',
    user_not_found: 'User not found'
  },
  status: {
    normal: 'Normal',
    disabled: 'Disabled'
  }
}
