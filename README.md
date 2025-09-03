# ATLAS - Authentication & Authorization Service

ATLAS is a robust, multi-tenant authentication and authorization service built with FastAPI. It provides a complete solution for managing users, applications, roles, and permissions in a scalable, tenant-based architecture.

## Key Features

- **JWT-based Authentication**: Secure login/logout functionality using JSON Web Tokens (JWT) with support for access and refresh tokens.
- **Multi-Tenant Architecture**: Supports multiple tenants with schema separation, allowing for isolated data for different clients using the `X-Tenant-Schema` header.
- **User Management**: Complete CRUD operations for managing users within each tenant.
- **Application Management**: Allows registration and management of different applications that will use the authentication service.
- **Role-Based Access Control (RBAC)**: Define granular roles and permissions for each application, and assign them to users.
- **Email Notifications**: Built-in support for sending transactional emails for actions like password resets and email verifications using customizable HTML templates.
- **Database Seeding**: Includes scripts to initialize default tenants and create sample data for quick setup.
- **Dockerized**: Fully containerized with Docker for easy setup, development, and deployment.

## Technology Stack

- **Backend**: Python, FastAPI
- **Database**: PostgreSQL (with SQLAlchemy ORM)
- **Caching**: Redis (Optional, for caching and other purposes)
- **Containerization**: Docker, Docker Compose
  \-- **Mailing**: `fastapi-mail`

## Project Structure

```
/app
|-- api/                # API endpoints and dependencies
|   |-- deps.py         # Dependencies for endpoints (e.g., auth, DB session)
|   |-- v1/             # API version 1
|       |-- api.py      # Main API router
|       |-- endpoints/  # Routers for each resource (users, roles, etc.)
|-- core/               # Core components (config, security, mailing)
|-- db/                 # Database session management and base models
|-- models/             # SQLAlchemy ORM models
|-- repositories/       # Data access layer (interacts with the DB)
|-- schemas/            # Pydantic schemas for data validation
|-- services/           # Business logic layer
|-- templates/          # Email templates
|-- utils/              # Utility scripts (e.g., database initialization)
|-- main.py             # Main FastAPI application entrypoint
```

## Getting Started

Follow these instructions to get the project up and running on your local machine.

### Prerequisites

- Docker
- Docker Compose

### 1\. Clone the Repository

```sh
git clone https://github.com/GratiaManullang03/atlas.git
cd atlas
```

### 2\. Configure Environment Variables

The application uses a `.env` file for configuration. Copy the provided example and fill in your details.

```sh
cp .env.example .env
```

Now, edit the `.env` file with your specific configuration:

```env
# -------------------------------------
# APPLICATION SETTINGS
# -------------------------------------
APP_NAME=ATLAS
APP_VERSION=1.0.0
DEBUG=True

# -------------------------------------
# DATABASE CONNECTION
# -------------------------------------
DATABASE_URL=postgresql://atlas_user:atlas_password@db:5432/atlas_db

# -------------------------------------
# REDIS CONNECTION (OPTIONAL)
# -------------------------------------
REDIS_URL=redis://redis:6379/0

# -------------------------------------
# JWT & SECURITY
# -------------------------------------
SECRET_KEY=your_super_secret_and_long_random_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30
FRONTEND_URL=http://localhost:3000

# -------------------------------------
# MULTI-TENANCY
# -------------------------------------
DEFAULT_SCHEMA=public

# -------------------------------------
# SMTP EMAIL CONFIGURATION
# -------------------------------------
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_email_password
MAIL_FROM=your_email@example.com
MAIL_FROM_NAME="ATLAS Service (No Reply)"
MAIL_SERVER=smtp.example.com
MAIL_PORT=465
MAIL_SSL_TLS=True
MAIL_STARTTLS=False
```

⚠️ **Important:**
You must replace the `SECRET_KEY` with a secure, random value.
The easiest way is to generate one using OpenSSL:

```sh
openssl rand -hex 64
```

Copy the output and paste it into the `.env` file as your `SECRET_KEY`.

### 3\. Build and Run with Docker

Use Docker Compose to build and run the application and its services (Redis). Note that for a complete setup, you should also add a database service (like PostgreSQL) to your `docker-compose.yml`.

```sh
docker-compose up --build -d
```

For development with hot-reloading, you can use the override file:

```sh
docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build -d
```

### 4\. Access the API

The API will be available at `http://localhost:8000`. You can access the interactive API documentation at `http://localhost:8000/docs`.

## API Usage

When interacting with the API, you may need to provide the following headers:

- `Authorization`: `Bearer <your_jwt_token>` for accessing protected endpoints.
- `X-Tenant-Schema`: The name of the tenant schema you want to operate on (e.g., `default_tenant`). If not provided, it will use the `DEFAULT_SCHEMA` from your configuration.
