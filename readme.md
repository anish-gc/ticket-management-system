# Ticket Management System


This project provides a secure Django REST API with custom token-based jwt authentication for tickt.

## 🌟 Features

- Custom token authentication with jwt
- Account, Roles, mapping, and Role Menu Mapping

## 🔧 Technology Stack

- **Backend**: Django 5.2+
- **Database**: PostgreSQL 16+
- **API**: Django REST Framework

## 📋 Prerequisites

Before setting up the project, ensure you have the following installed:

- Python 3.12+ 
- PostgreSQL 16+
- Git
- pip
- virtualenv (optional for development)

## 🚀 Getting Started

Follow these steps to set up and run the project locally:

### 1. Clone the Repository

```bash
git clone git@github.com:anish-gc/ticket-management-system.git
cd ticket-management-system
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r development.txt
```

### 4. Configure PostgreSQL

Make sure PostgreSQL is installed and running. Create a database for the project:

```bash
# Access PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE ticket_management_system;

# Exit PostgreSQL
\q
```

### 5. Environment Variables

Create a `.env` file in the project root (You can take sample from .env-sample. Just copy all the contents to .env):

```
DEBUG=True
MODE=development
SECRET_KEY=your_secret_key_here
DB_NAME=urdb
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```
### 6. Restore the backup from the file ticket_management_system.backup using command.After restore, you dont need to run makemigrations and migrate. It contains superuser, role, menu.    Skip step 7, 8, 9  if you follow this step. Replace ticket_management_system with ur db_name

```bash
pg_restore -h localhost -U postgres -W -d ticket_management_system ticket_management_system.backup

```
### 7. Run Migrations(only if u didnot follow step 6)

```bash
python manage.py makemigrations
python manage.py migrate
```

### 8. Create a Superuser(only if u didnot follow step 6)

```bash
python manage.py createsuperuser
```

### 9. Run this base commands sequentially (only if u didnot follow step 6)

```bash
python manage.py seed_predefined_roles
python manage.py load_menu_structure
python manage.py grant_admin_menu_permissions
```

### 10. Run the development Server

```bash
python manage.py runserver
```

The application should now be accessible at http://localhost:8000.

mission for role by visiting
```
## 🗂️ Project Structure

```
├── accounts
│   ├── account_manager.py
│   ├── admin.py
│   ├── apps.py
│   ├── build_menu.py
│   ├── __init__.py
│   ├── management
│   ├── migrations
│   ├── models
│   ├── serializers
│   ├── tests.py
│   ├── urls.py
│   ├── validation
│   └── views
├── authentication
│   ├── validation.py
│   └── views.py
├── core
│   ├── asgi.py
│   ├── __init__.py
│   ├── jwt_behaviour.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── debug.log
├── development.txt
├── manage.py
├── readme.md
├── templates
│   └── emails
├── ticket_management_system.backup
├── tickets
│   ├── admin.py
│   ├── apps.py
│   ├── __init__.py
│   ├── migrations
│   ├── models
│   ├── serializers
│   ├── signals.py
│   ├── tests.py
│   ├── ticket_manager.py
│   ├── urls.py
│   ├── utils
│   └── views
├── utilities
│   ├── api_views.py
│   ├── custom_pagination_class.py
│   ├── custom_response.py
│   ├── exception.py
│   ├── global_functions.py
│   ├── global_parameters.py
│   ├── jwt_authentication.py
│   ├── models.py
│   ├── permission_old.py
│   ├── permission.py
│   └── serializer_errors.py
└── venv


```

## Authentication

### Login

**Endpoint:**  
`POST /api/auth/login/`

**Request:**
```json
{
    "username": "your_username",
    "password": "your_password"
}
```

**Successful Response (200 OK):**
```json
{
    "ResponseCode": "0",
    "response": "Ok",
    "data": {
        "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU1NTMzMTU3LCJpYXQiOjE3NTU1MzI4NTcsImp0aSI6ImY0MjVjYzc5YzI0YzQ3ODRiMWJlNzQwNDc4MzQyYjU1IiwidXNlcl9pZCI6IjEifQ.mhW8SFyCkOZXAThJz4Whc_oti9KVjBd0aWHniZcG-3E",
        "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc1NjEzNzY1NywiaWF0IjoxNzU1NTMyODU3LCJqdGkiOiJhNWY4NWY0YTBiMWE0MzU4ODU1YzE3MmJmYTY5ZTExOSIsInVzZXJfaWQiOiIxIn0.ILVLtAdSNi7Dr1TPBhRkewIzhLoQEMvfFbpDmW5MC1M",
        "username": "anishchengre",
        "designation": "superadmin",
        "sessionTimeInMinutes": 5.0,
        "menu": [
            {
                "id": "c6df6120f59c46a1bc09eaae6286fc34",
                "name": "Account Management",
                "url": "#",
                "icon": "",
                "createUrl": "#",
                "listUrl": "#",
                "isView": true,
                "isCreate": true,
                "isUpdate": true,
                "isDelete": true,
                "subMenus": [
                    {
                        "id": "ba5e5ebc6887410e8352039d02acf744",
                        "name": "Accounts",
                        "url": "/accounts/",
                        "icon": "",
                        "createUrl": "/accounts/create/",
                        "listUrl": "/accounts/list/",
                        "isView": true,
                        "isCreate": true,
                        "isUpdate": true,
                        "isDelete": true,
                        "subMenus": null
                    },
                    {
                        "id": "485dee4c021149168ce274f7d23c8695",
                        "name": "Roles",
                        "url": "/roles/",
                        "icon": "",
                        "createUrl": "/roles/create/",
                        "listUrl": "/roles/list/",
                        "isView": true,
                        "isCreate": true,
                        "isUpdate": true,
                        "isDelete": true,
                        "subMenus": null
                    }
                ]
            }
        ]
    }
}
```

**Error Responses:**

- Invalid credentials (401 Unauthorized):
```json
{
    "ResponseCode": "1",
    "response": "Oops! We couldn't find any users."
}```

```
## Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/login/` | POST | User login |
| `/api/auth/logout/` | POST | User logout |
| `/api/auth/refresh/` | POST | Refresh JWT token |
| `/api/auth/verify/` | POST | Verify JWT token |

## Accounts

### Account Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/accounts/` | GET, POST | List all accounts or create new account |
| `/api/account/<pk>/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete specific account |
| `/api/account/toggle/<pk>/` | POST | Toggle account active status |

### Role Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/roles/` | GET, POST | List all roles or create new role |
| `/api/role/<pk>/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete specific role |

### Menu Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/menus/` | GET, POST | List all menus or create new menu |
| `/api/menu/<pk>/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete specific menu |

### Mapping Management

#### Account Role Mapping
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/account/role/mapping/` | GET, POST | List all account-role mappings or create new mapping |
| `/api/account/role/mapping/<pk>/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete specific mapping |

#### Role Menu Permission Mapping
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/role/menu/permission/mapping/` | GET, POST | List all role-menu-permission mappings or create new mapping |
| `/api/role/menu/permission/mapping/<pk>/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete specific mapping |

#### Account Menu Mapping
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/account/menu/mapping/` | GET, POST | List all account-menu mappings or create new mapping |
| `/api/account/menu/mapping/<pk>/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete specific mapping |

## Tickets

### Ticket Management
```
Ticked can be filtered by params like menu_id, status(?status=OPEN&status=IN_PROGRESS),priority(?priority=critical), 
sla_breached, escalated, order_by(?order_by=importance,deadline, sla, created_by, priority)
```
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tickets/` | GET, POST | List all tickets or create new ticket |
| `/api/ticket/<pk>/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete specific ticket |

### Ticket Priority

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ticket-priority/` | GET, POST | List all ticket priorities or create new priority |
| `/api/ticket-priority/<pk>/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete specific priority |

### Ticket Status

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ticket-status/` | GET, POST | List all ticket statuses or create new status |
| `/api/ticket-status/<pk>/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete specific status |

### Notification Logs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tickets/notification-logs/` | GET | List all notification logs |
| `/api/tickets/notification-log/<pk>/` | GET | Retrieve specific notification log |

## Usage Notes
1. All API endpoints are prefixed with `/api/`
2. Authentication is required for most endpoints using JWT tokens
3. Replace `<pk>` in URLs with the actual ReferenceID of the resource
4. POST endpoints typically require a JSON payload in the request body

```

