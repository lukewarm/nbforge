# NBForge Administrator Guide

This guide explains how to perform administrative tasks in NBForge, including user management and service account management.

## Getting Started

### Creating the Initial Superuser

To create the first superuser in the system, you'll need to use the command-line script:

```bash
# From the project root
cd backend
python /app/scripts/create_superuser.py admin@example.com your_secure_password
```

This script can also be used to promote an existing user to superuser status:

```bash
# To elevate an existing user (no password needed)
cd backend
python /app/scripts/create_superuser.py existing_user@example.com
```

### Accessing the Admin Interface

Once you have superuser access, you can access the admin interface in the web UI. Look for the "Admin" section in the navigation menu.

## User Management

### Viewing Users

The Users admin page displays all registered users in the system. You can see:
- Basic user information (name, email)
- Account status (active/inactive)
- Superuser status

### Modifying User Privileges

As a superuser, you can:
1. **Activate/Deactivate Users**: Toggle the "Active" switch to enable or disable user accounts
2. **Grant/Revoke Superuser Status**: Toggle the "Superuser" switch to grant or revoke admin privileges

> **Important**: Be careful when granting admin access, as admins have complete administrative control over the system.
