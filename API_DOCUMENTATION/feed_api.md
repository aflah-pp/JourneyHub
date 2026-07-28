# JourneyHub Feed API Documentation

**Base URL:** `/api/v1/`
**Auth:** Bearer JWT token (except where noted)

---

## 7. Feed Endpoints

### 7.1 Get Latest Feed

**Endpoint:** `GET /api/v1/feed/latest/`
**Auth:** Optional (public content only)

**Query Parameters:**

| Param | Type | Description |
|---|---|---|
| cursor | string | Base64 encoded cursor for pagination |
| page_size | int | Items per page (default: 30, max: 100) |

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Feed retrieved successfully.",
  "data": {
    "results": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Week 1: Research & Planning",
        "description": "<p>This week I focused on market research...</p>",
        "progress_percentage": 10,
        "milestone_status": "MILESTONE",
        "help_needed": false,
        "created_at": "2026-07-25T10:00:00Z",
        "updated_at": "2026-07-25T10:00:00Z",
        "author": {
          "id": "660e8400-e29b-41d4-a716-446655440001",
          "username": "john_doe",
          "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/john_doe.jpg"
        },
        "journey_id": "770e8400-e29b-41d4-a716-446655440002",
        "journey_title": "Building a SaaS Product",
        "journey_visibility": "PUBLIC",
        "images": [
          {
            "id": "880e8400-e29b-41d4-a716-446655440003",
            "cloudinary_url": "https://res.cloudinary.com/demo/image/upload/v1234567890/updates/planning.jpg",
            "cloudinary_public_id": "updates/planning",
            "width": 1200,
            "height": 800,
            "order_index": 0
          }
        ],
        "tags": [
          {
            "id": "990e8400-e29b-41d4-a716-446655440004",
            "name": "research",
            "slug": "research",
            "usage_count": 45
          }
        ],
        "milestone_badge": {
          "type": "milestone",
          "label": "Milestone",
          "color": "blue"
        },
        "help_needed_badge": null,
        "like_count": 12,
        "comment_count": 5,
        "is_liked_by_me": true,
        "is_saved_by_me": false
      }
    ],
    "next_cursor": "eyJjcmVhdGVkX2F0IjoiMjAyNi0wNy0yNVQxMDowMDowMFoiLCJpZCI6IjU1MGU4NDAwLWUyOWItNDFkNC1hNzE2LTQ0NjY1NTQ0MDAwMCJ9",
    "has_next": true,
    "page_size": 30
  }
}
```

---

### 7.2 Get Following Feed

**Endpoint:** `GET /api/v1/feed/following/`
**Auth:** Required

**Query Parameters:**

| Param | Type | Description |
|---|---|---|
| cursor | string | Base64 encoded cursor |
| page_size | int | Items per page (default: 30, max: 100) |

**Response:** Same as latest feed (filtered to followed users)

---

### 7.3 Get Trending Feed

**Endpoint:** `GET /api/v1/feed/trending/`
**Auth:** Optional

**Query Parameters:**

| Param | Type | Description |
|---|---|---|
| cursor | string | Base64 encoded cursor |
| page_size | int | Items per page (default: 30, max: 100) |

**Trending Score Formula (Per SRS):**
```
(likes*2 + comments*3 + saves*1.5) / hours_since_post^1.5
```

**Response:** Same as latest feed (sorted by trending score)

---

### 7.4 Get Help Needed Feed

**Endpoint:** `GET /api/v1/feed/help-needed/`
**Auth:** Optional

**Query Parameters:**

| Param | Type | Description |
|---|---|---|
| cursor | string | Base64 encoded cursor |
| page_size | int | Items per page (default: 30, max: 100) |

**Response:** Same as latest feed (only updates with `help_needed=true`)

---

### 7.5 Get Journey Timeline

**Endpoint:** `GET /api/v1/feed/journeys/{journey_id}/timeline/`
**Auth:** Optional (visibility filtered)

**Query Parameters:**

| Param | Type | Description |
|---|---|---|
| cursor | string | Base64 encoded cursor |
| page_size | int | Items per page (default: 30, max: 100) |

**Response:** Same as latest feed (scoped to specific journey)

---

### 7.6 Get User Timeline

**Endpoint:** `GET /api/v1/feed/users/{username}/timeline/`
**Auth:** Optional (visibility filtered)

**Query Parameters:**

| Param | Type | Description |
|---|---|---|
| cursor | string | Base64 encoded cursor |
| page_size | int | Items per page (default: 30, max: 100) |

**Response:** Same as latest feed (scoped to specific user)

---

## 8. Cursor Encoding Example

### Encoding a Cursor
```python
import base64
import json

def encode_cursor(created_at, obj_id):
    cursor_dict = {
        "created_at": created_at.isoformat(),
        "id": str(obj_id)
    }
    cursor_json = json.dumps(cursor_dict)
    return base64.b64encode(cursor_json.encode()).decode()

# Example: cursor = "eyJjcmVhdGVkX2F0IjoiMjAyNi0wNy0yNVQxMDowMDowMFoiLCJpZCI6IjU1MGU4NDAwLWUyOWItNDFkNC1hNzE2LTQ0NjY1NTQ0MDAwMCJ9"
```

### Decoding a Cursor
```python
def decode_cursor(cursor_string):
    try:
        cursor_json = base64.b64decode(cursor_string.encode()).decode()
        return json.loads(cursor_json)
    except:
        return None

# Returns: {"created_at": "2026-07-25T10:00:00Z", "id": "550e8400-e29b-41d4-a716-446655440000"}
```

---

## 9. Database Indexes Required

Ensure these indexes exist for optimal feed performance:

```sql
-- For Latest Feed
CREATE INDEX idx_feed_latest ON journey_updates (visibility, is_deleted, created_at DESC);

-- For Following Feed
CREATE INDEX idx_feed_following ON journey_updates (journey_id, visibility, is_deleted, created_at DESC);

-- For Help Needed Feed
CREATE INDEX idx_feed_help_needed ON journey_updates (help_needed, is_deleted, created_at DESC) WHERE help_needed = true AND is_deleted = false;

-- For Trending Feed
CREATE INDEX idx_feed_trending ON journey_updates (trending_score DESC, created_at DESC);

-- For Timeline
CREATE INDEX idx_timeline_journey ON journey_updates (journey_id, created_at DESC);
CREATE INDEX idx_timeline_user ON journey_updates (journey__owner_id, created_at DESC);
```

---

## 10. Feed Performance Optimization

### Query Optimization Checklist

| Technique | Applied |
|---|---|
| Cursor pagination | ✅ |
| Denormalized counters | ✅ |
| select_related | ✅ |
| prefetch_related | ✅ |
| Composite indexes | ✅ |
| Partial indexes | ✅ |
| Precomputed trending scores | ✅ |
| Query count < 5 per request | ✅ |

### Expected Response Times

| Feed Type | Query Count | Response Time |
|---|---|---|
| Latest | 3 queries | < 50ms |
| Following | 4 queries | < 80ms |
| Trending | 3 queries | < 60ms |
| Help Needed | 3 queries | < 40ms |
| Timeline | 3 queries | < 40ms |

---

## 11. Rate Limits

| Endpoint | Limit | Window |
|---|---|---|
| GET /feed/latest/ | 60 requests | 1 minute |
| GET /feed/following/ | 60 requests | 1 minute |
| GET /feed/trending/ | 60 requests | 1 minute |
| GET /feed/help-needed/ | 60 requests | 1 minute |
| GET /feed/journeys/{id}/timeline/ | 120 requests | 1 minute |
| GET /feed/users/{username}/timeline/ | 120 requests | 1 minute |

---

## Summary of Feed Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/feed/latest/` | Optional | Latest public updates |
| GET | `/feed/following/` | Required | Updates from followed users |
| GET | `/feed/trending/` | Optional | Trending updates |
| GET | `/feed/help-needed/` | Optional | Help needed updates |
| GET | `/feed/journeys/{id}/timeline/` | Optional | Journey timeline |
| GET | `/feed/users/{username}/timeline/` | Optional | User timeline |