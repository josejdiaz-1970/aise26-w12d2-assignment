# Production-Ready Inventory Management API

A production-ready FastAPI application demonstrating authentication, authorization,
rate limiting, caching, observability, and containerized deployment.

## Features
- RESTful CRUD API for inventory items
- JWT authentication with role-based access control
- Redis-backed rate limiting and caching
- Structured logging with request IDs
- Health and detailed health endpoints
- Async external API integration
- Full Docker & docker-compose support
- Automated tests with ≥80% coverage

## Tech Stack
- FastAPI
- SQLAlchemy
- Redis
- JWT (PyJWT)
- Docker & docker-compose
- pytest

## Setup (Local)
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

Setup (Docker)
docker compose up --build

## 📮 5.5.2 — Postman Collection (what to include)

In Postman:

1. Create a **Collection**
2. Add requests in this order:
   - `POST /v1/auth/register`
   - `POST /v1/auth/login`
   - `GET /v1/items` (no token → 401)
   - `GET /v1/items` (with token → 200)
   - `POST /v1/items`
   - `GET /v1/health`
   - `GET /v1/health/detailed`

3. Set an **Environment variable**:
   - `base_url = http://localhost:8000`
   - `token` (saved from login response)

4. Use:
```http
Authorization: Bearer {{token}}