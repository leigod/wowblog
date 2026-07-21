export default {
  title: 'System Settings',

  // Tabs
  tabs: {
    basic: 'Basic Settings',
    message: 'Message Push',
    email: 'Email Configuration'
  },

  // Basic Settings
  basic: {
    site_title: 'Site Title',
    site_title_placeholder: 'Enter site title',
    site_logo: 'Site Logo',
    upload_logo_tip: 'Supports PNG, JPG, SVG, ICO formats, file size less than 2MB',
    favicon: 'Favicon',
    upload_favicon_tip: 'Supports ICO, PNG, SVG formats, file size less than 1MB',
    disable_comments: 'Disable Comments',
    disable_comments_hint:
      'Global setting, when enabled all articles will disable comments, overrides article settings',
    disable_doc_comments: 'Disable Doc Comments',
    disable_doc_comments_hint: 'Global setting, when enabled all documents will disable comments',
    save: 'Save Settings'
  },

  // Upload
  upload: {
    drop_text: 'Drop file here or <em>click to upload</em>',
    uploading: 'Uploading',
    remove_image: 'Remove Image'
  },

  // Message Push
  message: {
    push_method: 'Push Method',
    method_websocket: 'Real-time Push (WebSocket)',
    method_websocket_desc:
      'Receive new message notifications instantly, requires browser WebSocket support',
    method_polling: 'Polling',
    method_polling_desc:
      'Periodically check for new messages, better compatibility but with some delay',

    polling_interval: 'Polling Interval',
    polling_interval_unit: 'seconds',
    polling_interval_hint:
      'Smaller interval means more real-time messages but consumes more server resources',

    save_message: 'Save Message Settings',
    test_connection: 'Test Connection',
    send_test_message: 'Send Test Message',

    connection_status: 'Connection Status',
    connected: 'Connected',
    disconnected: 'Disconnected',
    connection_hint:
      'WebSocket connection status, real-time message push requires keeping connection',
    ws_url_label: 'WebSocket URL:'
  },

  // Email Configuration
  email: {
    section_title: 'SMTP Email Configuration',
    section_desc:
      'After configuring the mail server, the system can send invitation notifications, registration verification emails, etc. Click on the email provider below to configure.',

    table: {
      provider: 'Provider',
      smtp_host: 'SMTP Server',
      port: 'Port',
      from_email: 'From Email',
      from_name: 'From Name',
      status: 'Status',
      config_status: 'Config Status',
      actions: 'Actions',
      enabled: 'Enabled',
      disabled: 'Disabled',
      configured: 'Configured',
      not_configured: 'Not Configured',
      edit: 'Edit',
      configure: 'Configure'
    },

    empty: 'No email configuration',

    dialog: {
      add_title: 'Add Email Configuration',
      edit_title: 'Edit Email Configuration',
      provider: 'Provider',
      smtp_host: 'SMTP Server',
      smtp_host_placeholder: 'smtp.example.com',
      port: 'Port',
      smtp_user: 'SMTP Username',
      smtp_user_placeholder: 'your@email.com',
      smtp_pass: 'SMTP Password',
      smtp_pass_placeholder: 'App-specific password',
      smtp_pass_edit_placeholder: 'Leave empty to keep original password',
      smtp_pass_hint: 'Leave empty to not change password',
      from_email: 'From Email',
      from_email_placeholder: 'noreply@example.com',
      from_name: 'From Name',
      from_name_placeholder: 'Blog Notification',
      use_tls: 'Use TLS',
      is_active: 'Active',
      btn_cancel: 'Cancel',
      btn_confirm: 'Confirm'
    }
  },

  // Email Providers
  providers: {
    gmail: 'Gmail',
    outlook: 'Outlook',
    qq: 'QQ Mail',
    '163': '163 Mail',
    custom: 'Custom'
  },

  // Messages
  message_tip: {
    save_success: 'Settings saved successfully!',
    save_failed: 'Save failed',
    message_save_success: 'Message push settings saved successfully!',
    message_save_hint: 'Please click "Test Connection" button to verify WebSocket connection',
    message_save_failed: 'Save failed, please check network connection',
    ws_connect_success: 'WebSocket connected successfully',
    ws_connect_failed: 'WebSocket connection failed',
    ws_connect_timeout:
      'WebSocket connection timeout, please check if backend service is running at localhost:8000',
    ws_test_failed: 'WebSocket connection test failed',
    test_message_sent: 'Test message sent, please check console',
    test_message_failed: 'Failed to send test message',
    token_not_found: 'Authentication token not found, please login first',
    logo_upload_success: 'Site logo uploaded successfully',
    favicon_upload_success: 'Favicon uploaded successfully',
    upload_failed: 'Upload failed',
    logo_format_error: 'Only PNG, JPG, SVG, ICO format files are allowed',
    logo_size_error: 'File size cannot exceed 2MB',
    favicon_format_error: 'Favicon can only be ICO, PNG, SVG format files',
    favicon_size_error: 'Favicon file size cannot exceed 1MB',
    email_load_failed: 'Failed to load email configuration',
    email_update_success: 'Email configuration updated',
    email_update_failed: 'Update failed',
    invalid_operation: 'Invalid operation',
    operation_failed: 'Operation failed, please check network connection'
  }
}
