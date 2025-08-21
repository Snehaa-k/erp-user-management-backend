# ERP Backend - Multi-Tenant User & Role Management System

A comprehensive Django REST API backend for multi-tenant ERP user and role management with real-time updates, audit logging, and granular permissions.

## Features

- **Multi-Tenant Architecture**: Complete data isolation between companies
- **JWT Authentication**: Secure token-based authentication with auto-refresh
- **Granular Permissions**: Flexible role-based permission system
- **Real-time Updates**: WebSocket integration for live permission changes
- **Audit Logging**: Comprehensive tracking of all user actions
- **Security Features**: Account lockout, strong password policies
- **RESTful APIs**: Complete CRUD operations for all entities

## Tech Stack

- **Django 5.2.5** with Django REST Framework
- **JWT Authentication** with SimpleJWT
- **WebSocket Support** with Django Channels
- **PostgreSQL/SQLite** database support
- **CORS** enabled for frontend integration

## Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create Initial Permissions**
   ```bash
   python manage.py create_permissions
   ```

4. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run Server**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/me/` - Get current user info

### Companies (Multi-tenant)
- `GET /api/companies/` - List companies
- `POST /api/companies/` - Create company
- `PUT /api/companies/{id}/` - Update company
- `DELETE /api/companies/{id}/` - Delete company

### Users
- `GET /api/users/` - List users (company-scoped)
- `POST /api/users/` - Create user
- `PUT /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Delete user
- `POST /api/users/{id}/assign_role/` - Assign role to user

### Roles & Permissions
- `GET /api/roles/` - List roles (company-scoped)
- `POST /api/roles/` - Create role
- `PUT /api/roles/{id}/` - Update role
- `DELETE /api/roles/{id}/` - Delete role
- `POST /api/roles/{id}/assign_permissions/` - Assign permissions to role
- `GET /api/permissions/` - List all permissions

### Audit Logs
- `GET /api/audit-logs/` - List audit logs (company-scoped, filterable)

## WebSocket Connection

Connect to `ws://localhost:8000/ws/notifications/` for real-time updates.

## Permission System

The system uses granular permissions:
- `VIEW_COMPANIES`, `CREATE_COMPANY`, `UPDATE_COMPANY`, `DELETE_COMPANY`
- `VIEW_USERS`, `CREATE_USER`, `UPDATE_USER`, `DELETE_USER`
- `VIEW_ROLES`, `CREATE_ROLE`, `UPDATE_ROLE`, `DELETE_ROLE`
- `VIEW_PERMISSIONS`, `ASSIGN_PERMISSIONS`, `ASSIGN_ROLES`
- `VIEW_AUDIT_LOGS`

## Multi-Tenant Data Isolation

- All data is automatically scoped to the user's company
- Users can only access data within their own company
- Strict permission checks at API level
- Company-based role and permission management

## Security Features

- **Account Lockout**: 5 failed attempts locks account for 5 minutes
- **Strong Password Policy**: Minimum 8 characters with complexity requirements
- **JWT Security**: Access tokens expire in 60 minutes, refresh tokens in 7 days
- **Audit Trail**: All actions logged with IP address and user agent

## Real-time Updates

When roles or permissions are modified:
1. Changes are saved to database
2. WebSocket notifications sent to affected users
3. Frontend receives updates and refreshes UI permissions
4. No page refresh required

## Database Schema

### Core Models
- **Company**: Multi-tenant container
- **User**: Extended Django user with company association
- **Role**: Company-scoped roles
- **Permission**: Global permission definitions
- **UserRole**: Many-to-many relationship between users and roles
- **AuditLog**: Comprehensive action logging

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
```

### Admin Interface
Access Django admin at `http://localhost:8000/admin/`

## Production Deployment

1. Set `DEBUG = False` in settings
2. Configure PostgreSQL database
3. Set up Redis for Channels
4. Configure proper CORS origins
5. Use environment variables for secrets