export default {
  title: 'Members and roles',
  title_info: 'Manage the members of your blog and define their roles.',
  btn: {
    role_definition: 'Role definition',
    invite_member: 'Invite member',
    add_member: 'Add member',
    update: 'Update Member',
    add: 'Add Member'
  },
  section: {
    manage_members: 'Manage members'
  },
  tabs: {
    team_members: 'Team members ({count})',
    pending_invites: 'Pending invites ({count})'
  },
  table: {
    name: 'Name',
    role: 'Role',
    visibility: 'Visibility',
    status: 'Status',
    actions: 'Actions',
    email: 'Email',
    invited_by: 'Invited by',
    expires_at: 'Expires at',
    created_at: 'Invited at'
  },
  visibility: {
    public: 'Public',
    private: 'Private'
  },
  status: {
    normal: 'Normal',
    block: 'Block',
    pending: 'Pending',
    accepted: 'Accepted',
    cancelled: 'Cancelled',
    expired: 'Expired'
  },
  gender: {
    male: 'Male',
    female: 'Female'
  },
  drawer: {
    member_details: 'Member details',
    role_definition: 'Role definition',
    create_title: 'Add New Member',
    edit_title: 'Edit Member',
    invite_title: 'Invite New Member'
  },
  form: {
    username: 'Username',
    username_placeholder: 'Enter username',
    full_name: 'Full Name',
    full_name_placeholder: 'Enter full name',
    profile_image: 'Profile Image',
    gender: 'Gender',
    email: 'Email',
    email_placeholder: 'Enter email',
    mobile: 'Mobile',
    mobile_placeholder: 'Enter mobile number',
    role: 'Role',
    role_placeholder: 'Select role',
    select_role: 'Select role',
    placeholder_email: 'Enter email',
    placeholder_mobile: 'Enter mobile number',
    language: 'Email language',
    language_placeholder: 'Select email language'
  },
  detail_section: {
    role: 'Role',
    visibility: 'Visibility',
    permissions: 'Permissions'
  },
  message: {
    get_members_error: 'Failed to get member list',
    delete_confirm: 'Are you sure to delete this member?',
    delete_success: 'Member deleted successfully',
    delete_error: 'Failed to delete member',
    update_success: 'Member updated successfully',
    add_success: 'Member added successfully',
    add_error: 'Failed to add member',
    validation_error: 'Username and full name are required',
    update_visibility_success: 'Updating member visibility: {name}',
    update_visibility_error: 'Updating member visibility failed: {name}',
    update_status_success: 'Updating member status: {name}',
    update_status_error: 'Updating member status failed: {name}',
    submit_failed: 'Submission failed',
    update_failed: 'Update failed',
    invite_success: 'Invitation created and email sent',
    invite_error: 'Failed to create invitation',
    invite_duplicate: 'This user has already been invited to this role',
    resend_success: 'Email resent successfully',
    resend_error: 'Failed to resend email',
    cancel_success: 'Invitation cancelled',
    cancel_error: 'Failed to cancel invitation',
    cancel_invite_confirm: 'Are you sure to cancel this invitation?',
    get_invitations_error: 'Failed to get invitation list',
    owner_delete_error: 'Cannot delete system owner'
  },
  validations: {
    username_required: 'Username is required',
    username_length: 'Length should be 3 to 20 characters',
    full_name_required: 'Full name is required',
    full_name_length: 'Length should be 3 to 20 characters',
    email_required: 'Email is required',
    invalid_email: 'Invalid email format',
    mobile_length: 'Mobile number must be 11 digits',
    invalid_mobile: 'Invalid mobile number',
    username_and_full_name_required: 'Username and full name are required',
    email_duplicate: 'This user has already been invited to the same role'
  },
  roles: {
    administrator: 'Administrator',
    admin: {
      name: 'Admin',
      description: 'Super user with all permissions',
      permissions1: 'Creater of publication',
      permissions2: 'Has full control',
      permissions3: 'Can delete publication',
      permissions4: 'Manage publication'
    },
    editor: {
      name: 'Editor',
      description: 'Can manage and publish all articles',
      permissions1: 'Publish and manage articles',
      permissions2: 'Manage categories and tags',
      permissions3: 'Manage comments',
      permissions4: 'Manage media files'
    },
    author: {
      name: 'Author',
      description: 'Can independently create, publish and manage their own articles',
      permissions1: 'Create and publish articles',
      permissions2: 'Edit own articles',
      permissions3: 'Manage media files',
      permissions4: 'Can only manage own content'
    },
    contributor: {
      name: 'Contributor',
      description: 'Can create draft articles (requires approval to publish)',
      permissions1: 'Create draft articles',
      permissions2: 'Edit own drafts',
      permissions3: 'Requires approval to publish',
      permissions4: 'For guest author submissions'
    },
    subscriber: {
      name: 'Subscriber',
      description: 'Can only manage their own profile',
      permissions: 'profile:*'
    },
    admin_permissions: 'manage system settings, publish articles, and manage members and comments',
    editor_permissions: 'publish and manage articles, manage categories and tags',
    author_permissions: 'create and publish own articles',
    contributor_permissions: 'create draft articles (requires approval)'
  },
  search: {
    placeholder: 'Search team members'
  },
  invite: {
    title: 'Invite Member',
    description: 'Invite a new member to join your team',
    email_label: 'Email address',
    email_placeholder: 'Enter invitee email',
    role_label: 'Select role',
    role_placeholder: 'Choose a role to assign',
    language_label: 'Email language',
    language_placeholder: 'Select email language',
    submit: 'Send Invitation',
    cancel: 'Cancel',
    resend: 'Resend',
    success: 'Invitation sent successfully!',
    error: 'Failed to send invitation, please try again',
    status: {
      pending: 'Pending',
      accepted: 'Accepted',
      cancelled: 'Cancelled',
      expired: 'Expired'
    },
    created_at: 'Invited at',
    expires_at: 'Expires at'
  }
}
