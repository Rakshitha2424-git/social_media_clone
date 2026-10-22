# Social Media Clone — Full-Stack Web Application

A full-stack social media application built with React, FastAPI, and PostgreSQL. The application allows users to register, authenticate, create and manage posts, search content, and vote on posts.

**GitHub Repository:** https://github.com/Rakshitha2424-git/social_media_clone

## Features

- User registration and login
- JWT-based authentication
- Password hashing using bcrypt
- Create, retrieve, update, and delete posts
- Post ownership checks for update and delete operations
- Search posts by title
- Pagination using `limit` and `skip`
- Voting on posts, with duplicate-vote prevention
- SQLAlchemy ORM for database operations
- Alembic database migrations
- Docker Compose configuration
- Automated test directory and GitHub Actions workflow configuration

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Data validation | Pydantic |
| Authentication | JWT, OAuth2 password flow |
| Password hashing | bcrypt via Passlib |
| Database migrations | Alembic |
| Containers | Docker, Docker Compose |
| CI/CD configuration | GitHub Actions |

## Architecture

The application uses a client-server architecture.

1. The React frontend sends HTTP requests to the FastAPI backend.
2. FastAPI validates incoming data and executes application logic.
3. SQLAlchemy interacts with PostgreSQL.
4. The backend returns structured responses to the frontend.

Request flow:

`React → FastAPI → SQLAlchemy → PostgreSQL`

## API Reference

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/users/` | Register a user |
| POST | `/login` | Authenticate and receive an access token |

### Posts

| Method | Endpoint | Description |
|---|---|---|
| GET | `/posts/` | Retrieve posts |
| POST | `/posts/` | Create a post |
| GET | `/posts/latest` | Retrieve the latest post |
| GET | `/posts/{id}` | Retrieve a specific post |
| PUT | `/posts/{id}` | Update a post you own |
| DELETE | `/posts/{id}` | Delete a post you own |

### Users

| Method | Endpoint | Description |
|---|---|---|
| GET | `/users/{id}` | Retrieve a user by ID |

### Voting

| Method | Endpoint | Description |
|---|---|---|
| GET | `/vote/` | Retrieve the authenticated user's voted post IDs |
| POST | `/vote/` | Add or remove a vote |

Protected endpoints require a valid bearer access token. Refer to the running API documentation for exact request and response schemas.

## Pagination and Search

The posts endpoint supports pagination and title search.

Example requests:

- `/posts/?limit=10&skip=0`
- `/posts/?limit=10&skip=10`
- `/posts/?limit=10&skip=0&search=python`

`limit` controls the maximum number of returned posts, while `skip` specifies how many results to skip. The `search` parameter filters posts by title.

The current implementation uses SQLAlchemy's `limit()` and `offset()` methods.

## Authentication and Authorization

Registration stores a hashed password rather than the original password. During login, the submitted password is verified against the stored hash.

After successful authentication, the API returns a JWT access token. Protected endpoints validate the token to identify the current user.

Post update and delete operations also verify that the authenticated user owns the requested post.

## Running the Application

### Prerequisites

- Python
- Node.js and npm
- PostgreSQL, or the configured PostgreSQL Docker service
- Docker and Docker Compose

### Clone the repository

```bash
git clone https://github.com/Rakshitha2424-git/social_media_clone.git
cd social_media_clone
```

### Configure environment variables

Create a local `.env` file using the variable names expected by the backend configuration:

```dotenv
DATABASE_HOSTNAME=localhost
DATABASE_PORT=5432
DATABASE_USERNAME=your_database_user
DATABASE_PASSWORD=your_database_password
DATABASE_NAME=your_database_name

SECRET_KEY=your_new_random_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Use your actual local database settings. For Docker Compose, the database hostname should match the PostgreSQL service name, and the API must use the database's configured internal port.

Never commit `.env` or real credentials to GitHub.

### Start the backend

Install the dependencies listed in `requirements.txt` in a virtual environment, ensure the database is running and configured, and apply the project's Alembic migrations as required.

Start FastAPI:

```bash
uvicorn main:app --reload
```

### Start the frontend

Navigate to the frontend directory and follow its package configuration:

```bash
npm install
npm run dev
```

### Run with Docker Compose

After reviewing and securing the Compose configuration, start the services with:

```bash
docker compose up --build
```

## API Documentation

FastAPI generates interactive API documentation automatically.

When the backend is running locally, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing and Continuous Integration

The repository contains a `tests` directory and GitHub Actions workflow configuration. Use these to document and verify automated test execution, including authentication, post operations, voting, validation errors, and authorization checks.

Only describe CI checks as passing after confirming their results in GitHub Actions.

## Future Improvements

- Validate pagination parameters and cap the maximum page size.
- Add tests for invalid tokens and unauthorized post modifications.
- Improve error handling for duplicate registrations.
- Use secure environment-based secrets and production database credentials.
- Add screenshots, a live demo, and deployment instructions.
- Document test coverage and CI/CD results.

## Learning Outcomes

This project demonstrates practical experience with REST API development, relational database integration, authentication, authorization, pagination, database migrations, containerization, and automated development workflows.
