# JourneyHub Journey Module API Documentation

**Base URL:** `/api/v1/`
**Auth:** Bearer JWT token (except where noted)

---

## 1. Journey Endpoints

### 1.1 List Public Journeys

**Endpoint:** `GET /api/v1/journeys/`
**Auth:** Optional

**Query Parameters:**

| Param      | Type   | Description                                              |
| ---------- | ------ | -------------------------------------------------------- |
| page       | int    | Page number                                              |
| page_size  | int    | Items per page (max 50)                                  |
| status     | string | Filter by status (ACTIVE, COMPLETED, PAUSED, ABANDONED)  |
| category   | string | Filter by category                                       |
| visibility | string | Filter by visibility                                     |
| search     | string | Search in title and description                          |
| ordering   | string | Order by: created_at, updated_at, title, latest_progress |

**Response (200 OK):**

```json
{
  "status": "success",
  "message": "Journeys retrieved successfully",
  "data": {
    "count": 42,
    "next": "http://localhost:8000/api/v1/journeys/?page=2",
    "previous": null,
    "results": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Building a SaaS Product from Scratch",
        "category": "SOFTWARE",
        "cover_image_url": "https://res.cloudinary.com/demo/image/upload/v1234567890/journey-cover/saas.jpg",
        "status": "ACTIVE",
        "visibility": "PUBLIC",
        "update_count": 15,
        "latest_progress": 65,
        "created_at": "2026-07-20T10:30:00Z",
        "owner": {
          "id": "660e8400-e29b-41d4-a716-446655440001",
          "username": "john_doe",
          "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/john_doe.jpg"
        }
      }
    ]
  }
}
```

---

### 1.2 List My Journeys

**Endpoint:** `GET /api/v1/journeys/my/`
**Auth:** Required

**Query Parameters:** Same as 1.1

**Response (200 OK):** Same as 1.1 (only owner's journeys)

---

### 1.3 Get Journey Detail

**Endpoint:** `GET /api/v1/journeys/{id}/`
**Auth:** Optional (visibility filtered)

**Response (200 OK):**

```json
{
  "status": "success",
  "message": "Journey retrieved successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Building a SaaS Product from Scratch",
    "category": "SOFTWARE",
    "description": "A journey of building a SaaS product from idea to launch...",
    "cover_image_url": "https://res.cloudinary.com/demo/image/upload/v1234567890/journey-cover/saas.jpg",
    "cover_image_public_id": "journey-cover/saas",
    "status": "ACTIVE",
    "visibility": "PUBLIC",
    "update_count": 15,
    "latest_progress": 65,
    "created_at": "2026-07-20T10:30:00Z",
    "updated_at": "2026-07-25T15:45:00Z",
    "owner": {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "username": "john_doe",
      "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/john_doe.jpg"
    }
  }
}
```

**Error Responses:**

```json
// 404 Not Found
{
  "status": "error",
  "message": "Journey not found."
}

// 403 Forbidden - Private Journey
{
  "status": "error",
  "message": "You do not have permission to view this journey."
}
```

---

### 1.4 Create Journey

**Endpoint:** `POST /api/v1/journeys/create/`
**Auth:** Required

**Request:**

```json
{
  "title": "Building a SaaS Product from Scratch",
  "category": "SOFTWARE",
  "description": "A journey of building a SaaS product from idea to launch...",
  "cover_image_url": "https://res.cloudinary.com/demo/image/upload/v1234567890/journey-cover/saas.jpg",
  "cover_image_public_id": "journey-cover/saas",
  "visibility": "PUBLIC"
}
```

**Category Options:** `SOFTWARE, STARTUP, SKILL, RESEARCH, BOOK, ART, FITNESS, DIY, CONTENT, CHALLENGE, OTHER`

**Visibility Options:** `PUBLIC, FOLLOWERS, PRIVATE`

**Response (201 Created):**

```json
{
  "status": "success",
  "message": "Journey created successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Building a SaaS Product from Scratch",
    "category": "SOFTWARE",
    "description": "A journey of building a SaaS product from idea to launch...",
    "cover_image_url": "https://res.cloudinary.com/demo/image/upload/v1234567890/journey-cover/saas.jpg",
    "cover_image_public_id": "journey-cover/saas",
    "status": "ACTIVE",
    "visibility": "PUBLIC",
    "update_count": 0,
    "latest_progress": 0,
    "created_at": "2026-07-25T16:00:00Z",
    "updated_at": "2026-07-25T16:00:00Z",
    "owner": {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "username": "john_doe",
      "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/john_doe.jpg"
    }
  }
}
```

**Error Responses:**

```json
// 400 Bad Request - Validation Error
{
  "status": "error",
  "message": "Validation error",
  "data": {
    "errors": {
      "title": ["Title must contain at least 3 character(s)."]
    }
  }
}

// 429 Too Many Requests
{
  "status": "error",
  "message": "Rate limit exceeded. Please try again later."
}
```

---

### 1.5 Update Journey

**Endpoint:** `PATCH /api/v1/journeys/{id}/update/`
**Auth:** Required (Owner only)

**Request:**

```json
{
  "title": "Building a SaaS Product - Updated",
  "category": "STARTUP",
  "description": "Updated description...",
  "cover_image_url": "https://res.cloudinary.com/demo/image/upload/v1234567890/journey-cover/updated.jpg",
  "cover_image_public_id": "journey-cover/updated",
  "status": "PAUSED",
  "visibility": "FOLLOWERS"
}
```

**Status Options:** `ACTIVE, COMPLETED, PAUSED, ABANDONED`

**Response (200 OK):**

```json
{
  "status": "success",
  "message": "Journey updated successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Building a SaaS Product - Updated",
    "category": "STARTUP",
    "description": "Updated description...",
    "cover_image_url": "https://res.cloudinary.com/demo/image/upload/v1234567890/journey-cover/updated.jpg",
    "cover_image_public_id": "journey-cover/updated",
    "status": "PAUSED",
    "visibility": "FOLLOWERS",
    "update_count": 15,
    "latest_progress": 65,
    "created_at": "2026-07-20T10:30:00Z",
    "updated_at": "2026-07-25T16:30:00Z",
    "owner": {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "username": "john_doe",
      "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/john_doe.jpg"
    }
  }
}
```

---

### 1.6 Delete Journey (Soft Delete)

**Endpoint:** `DELETE /api/v1/journeys/{id}/delete/`
**Auth:** Required (Owner only)

**Response (204 No Content):**

```json
{
  "status": "success",
  "message": "Journey deleted successfully"
}
```

---

## 2. Journey Update Endpoints

### 2.1 List Journey Updates

**Endpoint:** `GET /api/v1/journeys/{journey_id}/updates/`
**Auth:** Optional (visibility filtered)

**Query Parameters:**

| Param            | Type    | Description                                           |
| ---------------- | ------- | ----------------------------------------------------- |
| page             | int     | Page number                                           |
| page_size        | int     | Items per page (max 50)                               |
| help_needed      | boolean | Filter by help_needed flag                            |
| milestone_status | string  | Filter by milestone status                            |
| search           | string  | Search in title and description                       |
| ordering         | string  | Order by: created_at, updated_at, progress_percentage |

**Response (200 OK):**

```json
{
  "status": "success",
  "message": "Journey updates retrieved successfully",
  "data": {
    "count": 15,
    "next": "http://localhost:8000/api/v1/journeys/550e8400/updates/?page=2",
    "previous": null,
    "results": [
      {
        "id": "770e8400-e29b-41d4-a716-446655440002",
        "title": "Week 1: Research & Planning",
        "milestone_status": "MILESTONE",
        "help_needed": false,
        "progress_percentage": 10,
        "like_count": 12,
        "comment_count": 5,
        "created_at": "2026-07-21T09:00:00Z",
        "image": {
          "id": "880e8400-e29b-41d4-a716-446655440003",
          "cloudinary_url": "https://res.cloudinary.com/demo/image/upload/v1234567890/updates/planning.jpg",
          "cloudinary_public_id": "updates/planning",
          "width": 1200,
          "height": 800,
          "order_index": 0
        }
      }
    ]
  }
}
```

---

### 2.2 Get Journey Update Detail

**Endpoint:** `GET /api/v1/journeys/{journey_id}/updates/{id}/`
**Auth:** Optional (visibility filtered)

**Response (200 OK):**

```json
{
  "status": "success",
  "message": "Journey update retrieved successfully",
  "data": {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "title": "Week 1: Research & Planning",
    "description": "<p>This week I focused on market research and planning...</p>",
    "progress_percentage": 10,
    "milestone_status": "MILESTONE",
    "help_needed": false,
    "visibility": null,
    "effective_visibility": "PUBLIC",
    "like_count": 12,
    "comment_count": 5,
    "created_at": "2026-07-21T09:00:00Z",
    "updated_at": "2026-07-21T17:30:00Z",
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
      },
      {
        "id": "aa0e8400-e29b-41d4-a716-446655440005",
        "name": "planning",
        "slug": "planning",
        "usage_count": 32
      }
    ],
    "comments": [
      {
        "id": "bb0e8400-e29b-41d4-a716-446655440006",
        "author": {
          "id": "cc0e8400-e29b-41d4-a716-446655440007",
          "username": "jane_doe",
          "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/jane_doe.jpg"
        },
        "content": "<p>Great progress! Keep it up!</p>",
        "like_count": 3,
        "created_at": "2026-07-21T10:00:00Z",
        "updated_at": "2026-07-21T10:00:00Z"
      }
    ],
    "accepted_solution": null
  }
}
```

---

### 2.3 Create Journey Update

**Endpoint:** `POST /api/v1/journeys/{journey_id}/updates/create/`
**Auth:** Required (Owner only)

**Request:**

```json
{
  "title": "Week 1: Research & Planning",
  "description": "<p>This week I focused on market research and planning...</p>",
  "progress_percentage": 10,
  "milestone_status": "MILESTONE",
  "help_needed": false,
  "visibility": "PUBLIC"
}
```

**Milestone Status Options:** `NONE, MILESTONE, COMPLETED`

**Response (201 Created):**

```json
{
  "status": "success",
  "message": "Journey update created successfully",
  "data": {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "title": "Week 1: Research & Planning",
    "description": "<p>This week I focused on market research and planning...</p>",
    "progress_percentage": 10,
    "milestone_status": "MILESTONE",
    "help_needed": false,
    "visibility": "PUBLIC",
    "created_at": "2026-07-25T17:00:00Z",
    "updated_at": "2026-07-25T17:00:00Z"
  }
}
```

**Error Responses:**

```json
// 400 Bad Request - Validation Error
{
  "status": "error",
  "message": "Validation error",
  "data": {
    "errors": {
      "description": ["Description must contain at least 10 character(s)."],
      "progress_percentage": ["Progress must be between 0 and 100."]
    }
  }
}

// 403 Forbidden - Not Owner
{
  "status": "error",
  "message": "You do not have permission to perform this action."
}
```

---

### 2.4 Update Journey Update

**Endpoint:** `PATCH /api/v1/journeys/{journey_id}/updates/{id}/update/`
**Auth:** Required (Owner only)

**Request:**

```json
{
  "title": "Week 1: Research & Planning - Updated",
  "description": "<p>Updated description with more details...</p>",
  "progress_percentage": 15,
  "milestone_status": "COMPLETED",
  "help_needed": true,
  "visibility": "FOLLOWERS"
}
```

**Response (200 OK):**

```json
{
  "status": "success",
  "message": "Journey update updated successfully",
  "data": {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "title": "Week 1: Research & Planning - Updated",
    "description": "<p>Updated description with more details...</p>",
    "progress_percentage": 15,
    "milestone_status": "COMPLETED",
    "help_needed": true,
    "visibility": "FOLLOWERS",
    "created_at": "2026-07-21T09:00:00Z",
    "updated_at": "2026-07-25T17:30:00Z"
  }
}
```

---

### 2.5 Delete Journey Update

**Endpoint:** `DELETE /api/v1/journeys/{journey_id}/updates/{id}/delete/`
**Auth:** Required (Owner only)

**Response (204 No Content):**

```json
{
  "status": "success",
  "message": "Journey update deleted successfully"
}
```

---

## 3. Tag Endpoints

### 3.1 Update Journey Update Tags

**Endpoint:** `PATCH /api/v1/journeys/{journey_id}/updates/{update_id}/tags/`
**Auth:** Required (Owner only)

**Request:**

```json
{
  "tags": ["research", "planning", "saas", "product", "development"]
}
```

**Response (200 OK):**

```json
{
  "status": "success",
  "message": "Tags updated successfully",
  "data": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440004",
      "name": "research",
      "slug": "research",
      "usage_count": 46
    },
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440005",
      "name": "planning",
      "slug": "planning",
      "usage_count": 33
    },
    {
      "id": "bb0e8400-e29b-41d4-a716-446655440006",
      "name": "saas",
      "slug": "saas",
      "usage_count": 18
    },
    {
      "id": "cc0e8400-e29b-41d4-a716-446655440007",
      "name": "product",
      "slug": "product",
      "usage_count": 27
    },
    {
      "id": "dd0e8400-e29b-41d4-a716-446655440008",
      "name": "development",
      "slug": "development",
      "usage_count": 41
    }
  ]
}
```

**Error Responses:**

```json
// 400 Bad Request - Too Many Tags
{
  "status": "error",
  "message": "Validation error",
  "data": {
    "errors": {
      "tags": ["You cannot assign more than 5 tags."]
    }
  }
}

// 400 Bad Request - Invalid Format
{
  "status": "error",
  "message": "tags must be a list",
  "status_code": 400
}
```

---

### 3.2 Get Trending Tags

**Endpoint:** `GET /api/v1/journeys/tags/trending/`
**Auth:** Optional

**Response (200 OK):**

```json
{
  "status": "success",
  "message": "Trending tags retrieved",
  "data": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440004",
      "name": "python",
      "slug": "python",
      "usage_count": 156
    },
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440005",
      "name": "react",
      "slug": "react",
      "usage_count": 142
    },
    {
      "id": "bb0e8400-e29b-41d4-a716-446655440006",
      "name": "ai",
      "slug": "ai",
      "usage_count": 98
    }
  ]
}
```

---

### 3.3 Get Tag Detail

**Endpoint:** `GET /api/v1/journeys/tags/{slug}/`
**Auth:** Optional

**Response (200 OK):**

```json
{
  "status": "success",
  "message": "Tag retrieved successfully",
  "data": {
    "id": "990e8400-e29b-41d4-a716-446655440004",
    "name": "python",
    "slug": "python",
    "usage_count": 156
  }
}
```

**Error Response (404):**

```json
{
  "status": "error",
  "message": "Tag not found."
}
```

---

## 4. Image Endpoints

### 4.1 Add Image to Update

**Endpoint:** `POST /api/v1/updates/{update_id}/images/create/`
**Auth:** Required (Journey Owner)

**Request:**

```json
{
  "cloudinary_url": "https://res.cloudinary.com/demo/image/upload/v1234567890/updates/planning.jpg",
  "cloudinary_public_id": "updates/planning",
  "width": 1200,
  "height": 800,
  "order_index": 0
}
```

**Response (201 Created):**

```json
{
  "status": "success",
  "message": "Image added successfully",
  "data": {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "cloudinary_url": "https://res.cloudinary.com/demo/image/upload/v1234567890/updates/planning.jpg",
    "cloudinary_public_id": "updates/planning",
    "width": 1200,
    "height": 800,
    "order_index": 0
  }
}
```

**Error Response (400):**

```json
{
  "status": "error",
  "message": "Validation error",
  "data": {
    "errors": {
      "cloudinary_url": ["Invalid Cloudinary URL format."]
    }
  }
}
```

---

### 4.2 Delete Image

**Endpoint:** `DELETE /api/v1/updates/{update_id}/images/{id}/delete/`
**Auth:** Required (Journey Owner)

**Response (204 No Content):**

```json
{
  "status": "success",
  "message": "Image deleted successfully"
}
```

---

### 4.3 Reorder Images

**Endpoint:** `PATCH /api/v1/updates/{update_id}/images/reorder/`
**Auth:** Required (Journey Owner)

**Request:**

```json
{
  "ordered_ids": ["880e8400-e29b-41d4-a716-446655440003", "aa0e8400-e29b-41d4-a716-446655440009"]
}
```

**Response (200 OK):**

```json
{
  "status": "success",
  "message": "Images reordered successfully"
}
```

**Error Response (400):**

```json
{
  "status": "error",
  "message": "Order list must contain all images.",
  "status_code": 400
}
```

---

## 5. Search Endpoint

### 5.1 Search Journeys

**Endpoint:** `GET /api/v1/journeys/search/?q=saas`
**Auth:** Optional

**Query Parameters:**

| Param     | Type   | Description                                       |
| --------- | ------ | ------------------------------------------------- |
| q         | string | Search query                                      |
| page      | int    | Page number                                       |
| page_size | int    | Items per page (max 50)                           |
| ordering  | string | Order by: created_at, updated_at, latest_progress |

**Response (200 OK):** Same as 1.1 (filtered results)

---

## 6. Permission Summary

| Endpoint                                   | Permission                   |
| ------------------------------------------ | ---------------------------- |
| GET /journeys/                             | Public (visibility filtered) |
| GET /journeys/my/                          | Authenticated (owner only)   |
| GET /journeys/{id}/                        | Public (visibility filtered) |
| POST /journeys/create/                     | Authenticated                |
| PATCH /journeys/{id}/update/               | Journey Owner                |
| DELETE /journeys/{id}/delete/              | Journey Owner                |
| GET /journeys/{id}/updates/                | Public (visibility filtered) |
| GET /journeys/{id}/updates/{id}/           | Public (visibility filtered) |
| POST /journeys/{id}/updates/create/        | Journey Owner                |
| PATCH /journeys/{id}/updates/{id}/update/  | Journey Owner                |
| DELETE /journeys/{id}/updates/{id}/delete/ | Journey Owner                |
| PATCH /journeys/{id}/updates/{id}/tags/    | Journey Owner                |
| GET /tags/trending/                        | Public                       |
| GET /tags/{slug}/                          | Public                       |
| POST /updates/{id}/images/create/          | Journey Owner                |
| DELETE /updates/{id}/images/{id}/delete/   | Journey Owner                |
| PATCH /updates/{id}/images/reorder/        | Journey Owner                |
| GET /search/                               | Public                       |

---

## 7. Rate Limits

| Endpoint                            | Limit       | Window   |
| ----------------------------------- | ----------- | -------- |
| GET /journeys/                      | 60 requests | 1 minute |
| POST /journeys/create/              | 10 requests | 1 hour   |
| POST /journeys/{id}/updates/create/ | 30 requests | 1 hour   |
| POST /updates/{id}/comments/create/ | 30 requests | 1 hour   |
| POST /comments/{id}/replies/create/ | 30 requests | 1 hour   |
| POST /updates/{id}/images/create/   | 20 requests | 1 hour   |

---

## 8. Error Response Formats

### Standard Error Structure

```json
{
  "status": "error",
  "message": "Human readable error message",
  "data": {
    "errors": {
      "field_name": ["Error message array"]
    }
  }
}
```

### Common HTTP Status Codes

| Status | Meaning           | Use Case                 |
| ------ | ----------------- | ------------------------ |
| 200    | Success           | Successful operation     |
| 201    | Created           | New resource created     |
| 204    | No Content        | Successful deletion      |
| 400    | Bad Request       | Validation error         |
| 401    | Unauthorized      | Missing/invalid token    |
| 403    | Forbidden         | Insufficient permissions |
| 404    | Not Found         | Resource not found       |
| 429    | Too Many Requests | Rate limit exceeded      |

---

## 9. HTML Sanitization

All `description` and `content` fields support HTML but are sanitized to prevent XSS attacks.

**Allowed Tags:**

```
p, br, strong, em, u, s, ul, ol, li, blockquote,
code, pre, h1, h2, h3, h4, h5, h6, a, img, span, div, hr
```

**Allowed Attributes:**

- `a`: href, target, rel, title
- `img`: src, alt, width, height, loading
- `span`, `div`: style
- `*`: class, id, title

**Allowed Styles:**

```
color, background-color, font-size, font-weight, text-align,
text-decoration, margin, padding, border, border-radius, width, height
```

---

## Summary of All Journey Endpoints

| Method | Endpoint                              | Auth     | Description          |
| ------ | ------------------------------------- | -------- | -------------------- |
| GET    | `/journeys/`                          | Optional | List public journeys |
| GET    | `/journeys/my/`                       | Required | List my journeys     |
| GET    | `/journeys/{id}/`                     | Optional | Get journey detail   |
| POST   | `/journeys/create/`                   | Required | Create journey       |
| PATCH  | `/journeys/{id}/update/`              | Required | Update journey       |
| DELETE | `/journeys/{id}/delete/`              | Required | Delete journey       |
| GET    | `/journeys/{id}/updates/`             | Optional | List journey updates |
| GET    | `/journeys/{id}/updates/{id}/`        | Optional | Get update detail    |
| POST   | `/journeys/{id}/updates/create/`      | Required | Create update        |
| PATCH  | `/journeys/{id}/updates/{id}/update/` | Required | Update update        |
| DELETE | `/journeys/{id}/updates/{id}/delete/` | Required | Delete update        |
| PATCH  | `/journeys/{id}/updates/{id}/tags/`   | Required | Update tags          |
| GET    | `/tags/trending/`                     | Optional | Get trending tags    |
| GET    | `/tags/{slug}/`                       | Optional | Get tag detail       |
| POST   | `/updates/{id}/images/create/`        | Required | Add image            |
| DELETE | `/updates/{id}/images/{id}/delete/`   | Required | Delete image         |
| PATCH  | `/updates/{id}/images/reorder/`       | Required | Reorder images       |
| GET    | `/search/`                            | Optional | Search journeys      |
