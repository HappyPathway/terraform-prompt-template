# FastAPI E-commerce API

Build a modern e-commerce backend API using Python FastAPI framework with PostgreSQL, Docker, and best security practices.
## Required Libraries
Pydantic
Pydantic-AI

## Tech Stack
- **Language & Framework**: Python 3.11+, FastAPI
- **Database**: PostgreSQL with SQLAlchemy
- **Authentication**: JWT with OAuth2
- **Deployment**: Docker, GitHub Actions
- **Testing**: pytest

## Core Features

### User Management
- User authentication (login/register)
- Role-based permissions
- Profile management

### Product Management
- Product CRUD operations
- Categories and tagging
- Search and filtering
- Inventory tracking

### Order Processing
- Order creation and tracking
- Payment integration (Stripe)
- Order history

### API Documentation
- Automatic Swagger/OpenAPI docs
- Comprehensive endpoint documentation

## Project Structure
```
app/
├── api/           # API endpoints
├── core/          # Config, security
├── db/            # Database models, schemas
├── services/      # Business logic
└── main.py        # App entry point
tests/             # Test suite
Dockerfile         # Container definition
docker-compose.yml # Local development
```

## Key Endpoints

### Auth
- POST /api/auth/login
- POST /api/auth/register

### Users
- GET /api/users/me
- PUT /api/users/{user_id}

### Products
- GET /api/products/
- POST /api/products/
- GET /api/products/search

### Orders
- POST /api/orders/
- GET /api/orders/{order_id}

## Required Features
- Async database operations
- Input validation
- Error handling
- Comprehensive testing
- CI/CD pipeline
- Security best practices
