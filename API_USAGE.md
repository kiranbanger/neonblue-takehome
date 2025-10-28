# API Usage Guide

This document provides examples of how to use the Experimentation Platform API endpoints.

## Base URL
```
http://localhost:5000
```

## Authentication
All endpoints require Bearer token authentication. Include the token in the `Authorization` header:
```
Authorization: Bearer test-token-123
```

Valid tokens:
- `test-token-123`
- `demo-token-456`

---

## Endpoints

### 1. Create Experiment
**POST** `/experiments/`

Creates a new experiment with variants.

**Request:**
```bash
curl -X POST http://localhost:5000/experiments/ \
  -H "Authorization: Bearer test-token-123" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Homepage Button Color Test",
    "description": "Testing blue vs red button colors",
    "variants": [
      {
        "name": "control",
        "traffic_allocation": 50
      },
      {
        "name": "treatment",
        "traffic_allocation": 50
      }
    ]
  }'
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Homepage Button Color Test",
  "description": "Testing blue vs red button colors",
  "status": "active",
  "variants": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "control",
      "traffic_allocation": 50
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "name": "treatment",
      "traffic_allocation": 50
    }
  ],
  "created_at": "2025-10-27T10:30:00.000000",
  "updated_at": "2025-10-27T10:30:00.000000"
}
```

---

### 2. Get User Assignment
**GET** `/experiments/{experiment_id}/assignment/{user_id}`

Gets or creates a user's variant assignment for an experiment.

**Request:**
```bash
curl -X GET http://localhost:5000/experiments/550e8400-e29b-41d4-a716-446655440000/assignment/user_12345 \
  -H "Authorization: Bearer test-token-123" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "experiment_id": "890e8400-e29b-41d4-a716-446655440000",
  "variant_id": "12",
  "variant_name": "control",
  "user_id": "user_12345",
  "created_at": "2025-10-27T10:31:00.000000",
  "updated_at": "2025-10-27T10:31:00.000000"
}
```

---

### 3. Record Event
**POST** `/events/`

Records an event for a user (e.g., click, purchase, signup).

**Request:**
```bash
curl -X POST http://localhost:5000/events/ \
  -H "Authorization: Bearer test-token-123" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_12345",
    "type": "click",
    "timestamp": "2025-10-27T10:32:00.000000Z",
    "properties": {
      "page": "homepage",
      "button_color": "blue",
      "duration": 45
    }
  }'
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "user_id": "user_12345",
  "client_id": 1,
  "event_type": "click",
  "timestamp": "2025-10-27T10:32:00.000000",
  "properties": {
    "page": "homepage",
    "button_color": "blue",
    "duration": 45
  },
  "created_at": "2025-10-27T10:32:00.000000",
  "updated_at": "2025-10-27T10:32:00.000000"
}
```

---

### 4. Get Experiment Results
**GET** `/experiments/{experiment_id}/results/`

Gets aggregated results for an experiment, including user counts and conversion rates per variant and event type.

**Query Parameters:**
- `event_type` (optional): Filter results by specific event type(s). Can be a single value or multiple values.

**Request (all event types):**
```bash
curl -X GET http://localhost:5000/experiments/550e8400-e29b-41d4-a716-446655440000/results/ \
  -H "Authorization: Bearer test-token-123" \
  -H "Content-Type: application/json"
```

**Request (filter by event type):**
```bash
curl -X GET "http://localhost:5000/experiments/550e8400-e29b-41d4-a716-446655440000/results/?event_type=purchase" \
  -H "Authorization: Bearer test-token-123" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
[
  {
    "variant_name": "control",
    "user_count": 50,
    "event_type": "click",
    "user_count_event_type": 45,
    "conversion_rate": 0.9
  },
  {
    "variant_name": "control",
    "user_count": 50,
    "event_type": "purchase",
    "user_count_event_type": 8,
    "conversion_rate": 0.16
  },
  {
    "variant_name": "treatment",
    "user_count": 50,
    "event_type": "click",
    "user_count_event_type": 48,
    "conversion_rate": 0.96
  },
  {
    "variant_name": "treatment",
    "user_count": 50,
    "event_type": "purchase",
    "user_count_event_type": 12,
    "conversion_rate": 0.24
  }
]
```

---

## Error Responses

### 400 Bad Request
Invalid request format or missing required fields.

```json
{
  "detail": "Invalid timestamp format. Use ISO format (e.g., 2025-10-24T04:31:32.819790)"
}
```

### 401 Unauthorized
Missing or invalid authentication token.

```json
{
  "detail": "Invalid authentication credentials"
}
```

### 404 Not Found
Experiment or resource not found.

```json
{
  "detail": "Experiment not found"
}
```

---

## Notes

- **Idempotent Assignment**: Calling the assignment endpoint multiple times with the same user_id will always return the same variant assignment
- **Timestamp Format**: Use ISO 8601 format with UTC timezone (e.g., `2025-10-27T10:32:00.000000Z`)
- **Traffic Allocation**: Must sum to 100 across all variants
- **User ID**: Can be any string up to 255 characters
- **Properties**: Optional JSON object for storing additional event metadata

