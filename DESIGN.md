# Experimentation Platform - Design Document

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Data Models](#data-models)
4. [Authentication & Authorization](#authentication--authorization)
5. [Technology Stack](#technology-stack)
6. [Deployment](#deployment)

---

## Overview

### Purpose
The Experimentation Platform is a simplified A/B testing API service that enables clients to:
- Create and manage experiments with multiple variants
- Assign users to variants using deterministic hashing
- Track user events and behaviors
- Analyze experiment results with conversion metrics

### Key Features
- **Multi-tenant support**: Isolated data per client using client_id
- **Idempotent user assignment**: Consistent variant assignment using deterministic hashing
- **Flexible event tracking**: Support for arbitrary event types and properties
- **Real-time analytics**: Aggregated conversion metrics per variant and event type
- **RESTful API**: Standard HTTP methods and status codes
- **Bearer token authentication**: Simple but secure API access control

---

## System Architecture

### High-Level Architecture

```
┌─────────────┐
│   Client    │
│ Application │
└──────┬──────┘
       │ HTTPS/HTTP
       │ Bearer Token
       ▼
┌─────────────────────────────────────┐
│         FastAPI Application         │
│  ┌───────────────────────────────┐  │
│  │    Authentication Layer       │  │
│  │    (HTTPBearer)               │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │    API Routers                │  │
│  │  - Experiments Router         │  │
│  │  - Events Router              │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │    Business Logic             │  │
│  │  - Variant Assignment         │  │
│  │  - Results Aggregation        │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │    Data Access Layer          │  │
│  │    (SQLAlchemy ORM)           │  │
│  └───────────────────────────────┘  │
└──────────────┬──────────────────────┘
               │
               ▼
       ┌───────────────┐
       │  MySQL 8.0    │
       │   Database    │
       └───────────────┘
```

### Component Breakdown

#### 1. **API Layer** (`app/routers/`)
- **Experiments Router**: Handles experiment creation, user assignment, and results retrieval
- **Events Router**: Handles event recording and tracking

#### 2. **Authentication Layer** (`app/auth.py`)
- Bearer token validation
- Client ID extraction from token
- Token-to-client mapping

#### 3. **Data Models** (`app/models.py`)
- SQLAlchemy ORM models
- Database schema definitions
- Relationships and constraints

#### 4. **Database Layer** (`app/database.py`)
- Database connection management
- Session handling
- Connection pooling

---

## Data Models

### Entity Relationship Diagram

```
┌─────────────────┐
│   Experiment    │
│─────────────────│
│ id (UUID)       │◄─────┐
│ name            │      │
│ description     │      │
│ client_id       │      │
│ status          │      │
│ created_at      │      │
│ updated_at      │      │
└─────────────────┘      │
         │               │
         │ 1:N           │
         ▼               │
┌─────────────────┐      │
│    Variant      │      │
│─────────────────│      │
│ id (INT)        │      │
│ experiment_id   │──────┘
│ name            │
│ traffic_alloc   │
│ created_at      │
│ updated_at      │
└─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐      ┌─────────────────┐
│ UserAssignment  │      │     Event       │
│─────────────────│      │─────────────────│
│ id (UUID)       │      │ id (UUID)       │
│ experiment_id   │      │ user_id         │
│ variant_id      │      │ client_id       │
│ user_id         │◄────►│ event_type      │
│ created_at      │      │ timestamp       │
│ updated_at      │      │ properties      │
└─────────────────┘      │ created_at      │
                         │ updated_at      │
                         └─────────────────┘
```

### Model Descriptions

#### **Experiment**
Represents an A/B test experiment.
- **id**: UUID primary key
- **name**: Human-readable experiment name
- **description**: Optional experiment description
- **client_id**: Multi-tenant system (indexed)
- **status**: Experiment state (active, paused, completed)

#### **Variant**
Represents a variant within an experiment (e.g., control, treatment).
- **id**: Auto-incrementing integer primary key
- **experiment_id**: Foreign key to Experiment
- **name**: Variant name (control, treatment, etc.)
- **traffic_allocation**: Percentage of traffic (0-100)
- **Constraint**: Traffic allocations must sum to 100 per experiment

#### **UserAssignment**
Tracks which variant a user is assigned to for an experiment.
- **id**: UUID primary key
- **experiment_id**: Foreign key to Experiment (indexed)
- **variant_id**: Foreign key to Variant
- **user_id**: User identifier string (indexed)
- **Unique Constraint**: (experiment_id, user_id) - ensures one assignment per user per experiment

#### **Event**
Records user actions and behaviors.
- **id**: UUID primary key
- **user_id**: User identifier (indexed)
- **client_id**: Multi-tenant system (indexed)
- **event_type**: Type of event (click, purchase, signup, etc.)
- **timestamp**: When the event occurred (indexed)
- **properties**: JSON object for additional event data

### Indexing Strategy
- **client_id**: Fast multi-tenant filtering
- **user_id**: Quick user lookup for assignments and events
- **experiment_id**: Efficient experiment-based queries
- **timestamp**: Time-range queries for analytics

---

## Authentication & Authorization

### Authentication Mechanism
- **Type**: Bearer Token Authentication
- **Implementation**: FastAPI HTTPBearer security scheme
- **Token Storage**: Environment variables (.env file)

### Token Structure
```
VALID_TOKENS=token1,token2,token3
TOKEN_CLIENT_ID_MAP=token1:1,token2:2,token3:3
```

### Authorization Flow
1. Client sends request with `Authorization: Bearer <token>` header
2. HTTPBearer extracts token from header
3. `verify_token()` validates token against VALID_TOKENS
4. Returns associated client_id for multi-tenant isolation
5. All queries filtered by client_id

### Multi-Tenancy
- Each client has a unique client_id
- All experiments and events are scoped to client_id
- Prevents cross-client data access
- Enforced at database query level


## Technology Stack

### Backend Framework
- **FastAPI 0.109.0+**: Modern, fast web framework with automatic API documentation

### Database
- **MySQL 8.0**: Relational database for data persistence
- **SQLAlchemy 2.0.38+**: ORM for database interactions
- **PyMySQL**: MySQL driver for Python

### Data Processing
- **Pandas**: Data aggregation and analysis for results endpoint

### Authentication
- **FastAPI Security**: HTTPBearer for token authentication
- **python-dotenv**: Environment variable management

### Deployment
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

---


## Deployment

### Docker Architecture

```
┌─────────────────────────────────┐
│   Docker Compose Network        │
│                                 │
│  ┌──────────────────────────┐  │
│  │  FastAPI Container       │  │
│  │  - Port: 5000            │  │
│  │  - Python 3.13           │  │
│  │  - Hot reload enabled    │  │
│  └──────────┬───────────────┘  │
│             │                   │
│             │ DATABASE_URL      │
│             ▼                   │
│  ┌──────────────────────────┐  │
│  │  MySQL Container         │  │
│  │  - Port: 3306            │  │
│  │  - Persistent volume     │  │
│  │  - Health checks         │  │
│  └──────────────────────────┘  │
└─────────────────────────────────┘
```
---
