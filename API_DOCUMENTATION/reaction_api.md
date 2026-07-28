# JourneyHub Reaction Module API Documentation

**Base URL:** `/api/v1/`
**Auth:** Bearer JWT token (except where noted)

---

## 1. Like Endpoints

### 1.1 Create Like

**Endpoint:** `POST /api/v1/updates/{update_id}/like/`
**Auth:** Required

**URL Parameters:**

| Param | Type | Description |
|---|---|---|
| update_id | UUID | ID of the journey update to like |

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "You liked this update.",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user": {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "username": "john_doe",
      "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/john_doe.jpg"
    },
    "created_at": "2026-07-25T10:00:00Z"
  }
}
```

**Error Responses:**
```json
// 400 Bad Request - Already Liked
{
  "status": "error",
  "message": "You have already liked this update."
}

// 403 Forbidden - Not Visible
{
  "status": "error",
  "message": "You do not have permission to like this update."
}

// 404 Not Found
{
  "status": "error",
  "message": "Journey update not found."
}

// 429 Too Many Requests
{
  "status": "error",
  "message": "Rate limit exceeded. Please try again later."
}
```

---

### 1.2 Remove Like

**Endpoint:** `DELETE /api/v1/updates/{update_id}/unlike/`
**Auth:** Required

**URL Parameters:**

| Param | Type | Description |
|---|---|---|
| update_id | UUID | ID of the journey update to unlike |

**Response (204 No Content):**
```json
{
  "status": "success",
  "message": "Like removed successfully"
}
```

**Error Responses:**
```json
// 404 Not Found - Not Liked
{
  "status": "error",
  "message": "You have not liked this update."
}

// 404 Not Found - Update Not Found
{
  "status": "error",
  "message": "Journey update not found."
}
```

---

## 2. Comment Endpoints

### 2.1 List Comments

**Endpoint:** `GET /api/v1/updates/{update_id}/comments/`
**Auth:** Optional (visibility filtered)

**URL Parameters:**

| Param | Type | Description |
|---|---|---|
| update_id | UUID | ID of the journey update |

**Query Parameters:**

| Param | Type | Description |
|---|---|---|
| page | int | Page number |
| page_size | int | Items per page (max 50) |

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Comments retrieved successfully.",
  "data": {
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "770e8400-e29b-41d4-a716-446655440002",
        "user": {
          "id": "880e8400-e29b-41d4-a716-446655440003",
          "username": "jane_doe",
          "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/jane_doe.jpg"
        },
        "content": "<p>This is a great update! Keep going!</p>",
        "reply_count": 2,
        "created_at": "2026-07-25T09:00:00Z",
        "updated_at": "2026-07-25T09:00:00Z",
        "replies": [
          {
            "id": "990e8400-e29b-41d4-a716-446655440004",
            "user": {
              "id": "aa0e8400-e29b-41d4-a716-446655440005",
              "username": "bob_smith",
              "avatar_url": null
            },
            "content": "<p>I completely agree with you!</p>",
            "created_at": "2026-07-25T09:30:00Z",
            "updated_at": "2026-07-25T09:30:00Z"
          }
        ]
      }
    ]
  }
}
```

**Error Responses:**
```json
// 403 Forbidden - Not Visible
{
  "status": "error",
  "message": "You do not have permission to view comments on this update."
}

// 404 Not Found
{
  "status": "error",
  "message": "Journey update not found."
}
```

---

### 2.2 Create Comment

**Endpoint:** `POST /api/v1/updates/{update_id}/comments/create/`
**Auth:** Required

**URL Parameters:**

| Param | Type | Description |
|---|---|---|
| update_id | UUID | ID of the journey update |

**Request:**
```json
{
  "content": "<p>This is a great update! Keep going!</p>"
}
```

**Validation Rules:**

| Field | Rules |
|---|---|
| content | Min 1 character, HTML sanitized (no scripts/events) |

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Comment added successfully.",
  "data": {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "user": {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "username": "jane_doe",
      "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/jane_doe.jpg"
    },
    "content": "<p>This is a great update! Keep going!</p>",
    "reply_count": 0,
    "created_at": "2026-07-25T10:00:00Z",
    "updated_at": "2026-07-25T10:00:00Z",
    "replies": []
  }
}
```

**Error Responses:**
```json
// 400 Bad Request - Empty Content
{
  "status": "error",
  "message": "Validation error",
  "data": {
    "errors": {
      "content": ["Comment must contain at least 1 character(s)."]
    }
  }
}

// 403 Forbidden - Not Visible
{
  "status": "error",
  "message": "You do not have permission to comment on this update."
}

// 429 Too Many Requests
{
  "status": "error",
  "message": "Rate limit exceeded. Please try again later."
}
```

---

### 2.3 Get Comment Detail

**Endpoint:** `GET /api/v1/comments/{id}/`
**Auth:** Optional (visibility filtered)

**URL Parameters:**

| Param | Type | Description |
|---|---|---|
| id | UUID | ID of the comment |

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Comment retrieved successfully.",
  "data": {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "user": {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "username": "jane_doe",
      "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/jane_doe.jpg"
    },
    "content": "<p>This is a great update! Keep going!</p>",
    "reply_count": 2,
    "created_at": "2026-07-25T09:00:00Z",
    "updated_at": "2026-07-25T09:00:00Z",
    "replies": [
      {
        "id": "990e8400-e29b-41d4-a716-446655440004",
        "user": {
          "id": "aa0e8400-e29b-41d4-a716-446655440005",
          "username": "bob_smith",
          "avatar_url": null
        },
        "content": "<p>I completely agree with you!</p>",
        "created_at": "2026-07-25T09:30:00Z",
        "updated_at": "2026-07-25T09:30:00Z"
      }
    ]
  }
}
```

**Error Responses:**
```json
// 403 Forbidden
{
  "status": "error",
  "message": "You do not have permission to view this comment."
}

// 404 Not Found
{
  "status": "error",
  "message": "Comment not found."
}
```

---

### 2.4 Update Comment

**Endpoint:** `PATCH /api/v1/comments/{id}/`
**Auth:** Required (Comment Author)

**URL Parameters:**

| Param | Type | Description |
|---|---|---|
| id | UUID | ID of the comment to update |

**Request:**
```json
{
  "content": "<p>Updated comment with more details...</p>"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Comment updated successfully.",
  "data": {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "user": {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "username": "jane_doe",
      "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/jane_doe.jpg"
    },
    "content": "<p>Updated comment with more details...</p>",
    "reply_count": 2,
    "created_at": "2026-07-25T09:00:00Z",
    "updated_at": "2026-07-25T10:30:00Z",
    "replies": ["..."]
  }
}
```

**Error Responses:**
```json
// 403 Forbidden - Not Owner
{
  "status": "error",
  "message": "You do not have permission to update this comment."
}

// 404 Not Found
{
  "status": "error",
  "message": "Comment not found."
}
```

---

### 2.5 Delete Comment (Soft Delete)

**Endpoint:** `DELETE /api/v1/comments/{id}/`
**Auth:** Required (Comment Author)

**URL Parameters:**

| Param | Type | Description |
|---|---|---|
| id | UUID | ID of the comment to delete |

**Response (204 No Content):**
```json
{
  "status": "success",
  "message": "Comment deleted successfully."
}
```

**Error Responses:**
```json
// 403 Forbidden - Not Owner
{
  "status": "error",
  "message": "You do not have permission to delete this comment."
}

// 404 Not Found
{
  "status": "error",
  "message": "Comment not found."
}
```

---

## 3. Comment Reply Endpoints

### 3.1 List Replies

**Endpoint:** `GET /api/v1/comments/{comment_id}/replies/`
**Auth:** Optional (visibility filtered)

**URL Parameters:**

| Param | Type | Description |
|---|---|---|
| comment_id | UUID | ID of the parent comment |

**Query Parameters:**

| Param | Type | Description |
|---|---|---|
| page | int | Page number |
| page_size | int | Items per page (max 50) |

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Replies retrieved successfully.",
  "data": {
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "990e8400-e29b-41d4-a716-446655440004",
        "user": {
          "id": "aa0e8400-e29b-41d4-a716-446655440005",
          "username": "bob_smith",
          "avatar_url": null
        },
        "content": "<p>I completely agree with you!</p>",
        "created_at": "2026-07-25T09:30:00Z",
        "updated_at": "2026-07-25T09:30:00Z"
      }
    ]
  }
}
```

**Error Responses:**
```json
// 403 Forbidden
{
  "status": "error",
  "message": "You do not have permission to view this comment."
}

// 404 Not Found
{
  "status": "error",
  "message": "Comment not found."
}
```

---

### 3.2 Create Reply

**Endpoint:** `POST /api/v1/comments/{comment_id}/replies/create/`
**Auth:** Required

**URL Parameters:**

| Param | Type | Description |
|---|---|---|
| comment_id | UUID | ID of the parent comment |

**Request:**
```json
{
  "content": "<p>I completely agree with your point!</p>"
}
```

**Validation Rules:**

| Field | Rules |
|---|---|
| content | Min 1 character, HTML sanitized (no scripts/events) |

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Reply added successfully.",
  "data": {
    "id": "990e8400-e29b-41d4-a716-446655440004",
    "user": {
      "id": "aa0e8400-e29b-41d4-a716-446655440005",
      "username": "bob_smith",
      "avatar_url": null
    },
    "content": "<p>I completely agree with your point!</p>",
    "created_at": "2026-07-25T10:30:00Z",
    "updated_at": "2026-07-25T10:30:00Z"
  }
}
```

**Error Responses:**
```json
// 400 Bad Request - Empty Content
{
  "status": "error",
  "message": "Validation error",
  "data": {
    "errors": {
      "content": ["Reply must contain at least 1 character(s)."]
    }
  }
}

// 403 Forbidden
{
  "status": "error",
  "message": "You do not have permission to reply to this comment."
}

// 404 Not Found
{
  "status": "error",
  "message": "Comment not found."
}

// 429 Too Many Requests
{
  "status": "error",
  "message": "Rate limit exceeded. Please try again later."
}
```

---

### 3.3 Get Reply Detail

**Endpoint:** `GET /api/v1/replies/{id}/`
**Auth:** Optional (visibility filtered)

**URL Parameters:**

| Param | Type | Description |
|---|---|---|
| id | UUID | ID of the reply |

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Reply retrieved successfully.",
  "data": {
    "id": "990e8400-e29b-41d4-a716-446655440004",
    "user": {
      "id": "aa0e8400-e29b-41d4-a716-446655440005",
      "username": "bob_smith",
      "avatar_url": null
    },
    "content": "<p>I completely agree with your point!</p>",
    "created_at": "2026-07-25T09:30:00Z",
    "updated_at": "2026-07-25T09:30:00Z"
  }
}
```

**Error Responses:**
```json
// 403 Forbidden
{
  "status": "error",
  "message": "You do not have permission to view this reply."
}

// 404 Not Found
{
  "status": "error",
  "message": "Reply not found."
}
```

---

### 3.4 Update Reply

**Endpoint:** `PATCH /api/v1/replies/{id}/`
**Auth:** Required (Reply Author)

**URL Parameters:**

| Param | Type | Description |
|---|---|---|
| id | UUID | ID of the reply to update |

**Request:**
```json
{
  "content": "<p>Updated reply with more details...</p>"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Reply updated successfully.",
  "data": {
    "id": "990e8400-e29b-41d4-a716-446655440004",
    "user": {
      "id": "aa0e8400-e29b-41d4-a716-446655440005",
      "username": "bob_smith",
      "avatar_url": null
    },
    "content": "<p>Updated reply with more details...</p>",
    "created_at": "2026-07-25T09:30:00Z",
    "updated_at": "2026-07-25T10:30:00Z"
  }
}
```

**Error Responses:**
```json
// 403 Forbidden - Not Owner
{
  "status": "error",
  "message": "You do not have permission to update this reply."
}

// 404 Not Found
{
  "status": "error",
  "message": "Reply not found."
}
```

---

### 3.5 Delete Reply (Soft Delete)

**Endpoint:** `DELETE /api/v1/replies/{id}/`
**Auth:** Required (Reply Author)

**URL Parameters:**

| Param | Type | Description |
|---|---|---|
| id | UUID | ID of the reply to delete |

**Response (204 No Content):**
```json
{
  "status": "success",
  "message": "Reply deleted successfully."
}
```

**Error Responses:**
```json
// 403 Forbidden - Not Owner
{
  "status": "error",
  "message": "You do not have permission to delete this reply."
}

// 404 Not Found
{
  "status": "error",
  "message": "Reply not found."
}
```

---

## 4. Accepted Solution Endpoints

### 4.1 Get Accepted Solution

**Endpoint:** `GET /api/v1/updates/{update_id}/accepted-solution/`
**Auth:** Optional (visibility filtered)

**URL Parameters:**

| Param | Type | Description |
|---|---|---|
| update_id | UUID | ID of the journey update |

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Accepted solution retrieved successfully.",
  "data": {
    "id": "bb0e8400-e29b-41d4-a716-446655440006",
    "journey_update_id": "cc0e8400-e29b-41d4-a716-446655440007",
    "comment": {
      "id": "dd0e8400-e29b-41d4-a716-446655440008",
      "user": {
        "id": "ee0e8400-e29b-41d4-a716-446655440009",
        "username": "jane_doe",
        "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/jane_doe.jpg"
      },
      "content": "<p>This is the solution you're looking for...</p>",
      "reply_count": 1,
      "created_at": "2026-07-24T08:00:00Z",
      "updated_at": "2026-07-24T08:00:00Z",
      "replies": ["..."]
    },
    "accepted_at": "2026-07-25T10:00:00Z",
    "accepted_by": {
      "id": "ff0e8400-e29b-41d4-a716-446655440010",
      "username": "john_doe",
      "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/john_doe.jpg"
    }
  }
}
```

**Error Responses:**
```json
// 404 Not Found - No Accepted Solution
{
  "status": "error",
  "message": "No accepted solution found for this update."
}

// 403 Forbidden
{
  "status": "error",
  "message": "You do not have permission to view this accepted solution."
}

// 404 Not Found
{
  "status": "error",
  "message": "Journey update not found."
}
```

---

### 4.2 Accept Solution

**Endpoint:** `POST /api/v1/updates/{update_id}/accept-solution/`
**Auth:** Required (Journey Owner only)

**URL Parameters:**

| Param | Type | Description |
|---|---|---|
| update_id | UUID | ID of the journey update |

**Request:**
```json
{
  "comment_id": "dd0e8400-e29b-41d4-a716-446655440008"
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Solution accepted successfully.",
  "data": {
    "id": "bb0e8400-e29b-41d4-a716-446655440006",
    "journey_update_id": "cc0e8400-e29b-41d4-a716-446655440007",
    "comment": {
      "id": "dd0e8400-e29b-41d4-a716-446655440008",
      "user": {
        "id": "ee0e8400-e29b-41d4-a716-446655440009",
        "username": "jane_doe",
        "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/jane_doe.jpg"
      },
      "content": "<p>This is the solution you're looking for...</p>",
      "reply_count": 1,
      "created_at": "2026-07-24T08:00:00Z",
      "updated_at": "2026-07-24T08:00:00Z",
      "replies": ["..."]
    },
    "accepted_at": "2026-07-25T10:00:00Z",
    "accepted_by": {
      "id": "ff0e8400-e29b-41d4-a716-446655440010",
      "username": "john_doe",
      "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/john_doe.jpg"
    }
  }
}
```

**Error Responses:**
```json
// 400 Bad Request - Already Accepted
{
  "status": "error",
  "message": "Validation error",
  "data": {
    "errors": {
      "comment_id": ["A solution has already been accepted for this update."]
    }
  }
}

// 400 Bad Request - Comment Not Found
{
  "status": "error",
  "message": "Validation error",
  "data": {
    "errors": {
      "comment_id": ["Comment not found or does not belong to this update."]
    }
  }
}

// 403 Forbidden - Not Journey Owner
{
  "status": "error",
  "message": "You do not have permission to perform this action."
}

// 404 Not Found
{
  "status": "error",
  "message": "Journey update not found."
}

// 429 Too Many Requests
{
  "status": "error",
  "message": "Rate limit exceeded. Please try again later."
}
```

---

### 4.3 Remove Accepted Solution

**Endpoint:** `DELETE /api/v1/updates/{update_id}/remove-accepted/`
**Auth:** Required (Journey Owner only)

**URL Parameters:**

| Param | Type | Description |
|---|---|---|
| update_id | UUID | ID of the journey update |

**Response (204 No Content):**
```json
{
  "status": "success",
  "message": "Accepted solution removed successfully."
}
```

**Error Responses:**
```json
// 403 Forbidden - Not Journey Owner
{
  "status": "error",
  "message": "You do not have permission to perform this action."
}

// 404 Not Found - No Accepted Solution
{
  "status": "error",
  "message": "No accepted solution found for this update."
}

// 404 Not Found
{
  "status": "error",
  "message": "Journey update not found."
}
```

---

## 5. Saved Journey Endpoints

### 5.1 List Saved Journeys

**Endpoint:** `GET /api/v1/journeys/saved/`
**Auth:** Required

**Query Parameters:**

| Param | Type | Description |
|---|---|---|
| page | int | Page number |
| page_size | int | Items per page (max 50) |

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Saved journeys retrieved successfully.",
  "data": {
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "110e8400-e29b-41d4-a716-446655440011",
        "user": {
          "id": "120e8400-e29b-41d4-a716-446655440012",
          "username": "john_doe",
          "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/john_doe.jpg"
        },
        "journey": "130e8400-e29b-41d4-a716-446655440013",
        "journey_title": "Building a SaaS Product",
        "journey_owner": {
          "id": "140e8400-e29b-41d4-a716-446655440014",
          "username": "jane_doe",
          "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/jane_doe.jpg"
        },
        "created_at": "2026-07-25T08:00:00Z"
      }
    ]
  }
}
```

---

### 5.2 Save Journey

**Endpoint:** `POST /api/v1/journeys/{journey_id}/save/`
**Auth:** Required

**URL Parameters:**

| Param | Type | Description |
|---|---|---|
| journey_id | UUID | ID of the journey to save |

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Journey saved successfully.",
  "data": {
    "id": "110e8400-e29b-41d4-a716-446655440011",
    "user": {
      "id": "120e8400-e29b-41d4-a716-446655440012",
      "username": "john_doe",
      "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/john_doe.jpg"
    },
    "journey": "130e8400-e29b-41d4-a716-446655440013",
    "journey_title": "Building a SaaS Product",
    "journey_owner": {
      "id": "140e8400-e29b-41d4-a716-446655440014",
      "username": "jane_doe",
      "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/jane_doe.jpg"
    },
    "created_at": "2026-07-25T10:00:00Z"
  }
}
```

**Error Responses:**
```json
// 400 Bad Request - Already Saved
{
  "status": "error",
  "message": "You have already saved this journey."
}

// 403 Forbidden - Not Visible
{
  "status": "error",
  "message": "You cannot save this journey."
}

// 404 Not Found
{
  "status": "error",
  "message": "Journey not found."
}

// 429 Too Many Requests
{
  "status": "error",
  "message": "Rate limit exceeded. Please try again later."
}
```

---

### 5.3 Unsave Journey

**Endpoint:** `DELETE /api/v1/journeys/{journey_id}/unsave/`
**Auth:** Required

**URL Parameters:**

| Param | Type | Description |
|---|---|---|
| journey_id | UUID | ID of the journey to unsave |

**Response (204 No Content):**
```json
{
  "status": "success",
  "message": "Journey unsaved successfully."
}
```

**Error Responses:**
```json
// 404 Not Found - Not Saved
{
  "status": "error",
  "message": "You haven't saved this journey."
}

// 404 Not Found
{
  "status": "error",
  "message": "Journey not found."
}
```

---

## 6. Notification Endpoints

### 6.1 List Notifications

**Endpoint:** `GET /api/v1/notifications/`
**Auth:** Required

**Query Parameters:**

| Param | Type | Description |
|---|---|---|
| page | int | Page number |
| page_size | int | Items per page (max 50) |

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Notifications retrieved successfully.",
  "data": {
    "count": 15,
    "next": "http://localhost:8000/api/v1/notifications/?page=2",
    "previous": null,
    "results": [
      {
        "id": "150e8400-e29b-41d4-a716-446655440015",
        "notification_type": "LIKE",
        "title": "jane_doe liked your update",
        "body": "jane_doe liked 'Week 1: Research & Planning'",
        "is_read": false,
        "read_at": null,
        "created_at": "2026-07-25T10:00:00Z",
        "actor": {
          "id": "160e8400-e29b-41d4-a716-446655440016",
          "username": "jane_doe",
          "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/jane_doe.jpg"
        },
        "target_type": "journeyupdate",
        "target_id": "170e8400-e29b-41d4-a716-446655440017",
        "target_detail": {
          "title": "Week 1: Research & Planning",
          "id": "170e8400-e29b-41d4-a716-446655440017"
        }
      }
    ]
  }
}
```

**Notification Types:**

| Type | Description |
|---|---|
| LIKE | Someone liked your update |
| COMMENT | Someone commented on your update |
| COMMENT_REPLY | Someone replied to your comment |
| FOLLOW | Someone followed you |
| ACCEPTED_SOLUTION | Someone accepted your solution |
| MILESTONE | Someone reached a milestone |

---

### 6.2 Get Notification Detail

**Endpoint:** `GET /api/v1/notifications/{id}/`
**Auth:** Required (Recipient only)

**URL Parameters:**

| Param | Type | Description |
|---|---|---|
| id | UUID | ID of the notification |

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Notification retrieved successfully.",
  "data": {
    "id": "150e8400-e29b-41d4-a716-446655440015",
    "notification_type": "LIKE",
    "title": "jane_doe liked your update",
    "body": "jane_doe liked 'Week 1: Research & Planning'",
    "is_read": false,
    "read_at": null,
    "created_at": "2026-07-25T10:00:00Z",
    "actor": {
      "id": "160e8400-e29b-41d4-a716-446655440016",
      "username": "jane_doe",
      "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/jane_doe.jpg"
    },
    "target_type": "journeyupdate",
    "target_id": "170e8400-e29b-41d4-a716-446655440017",
    "target_detail": {
      "title": "Week 1: Research & Planning",
      "id": "170e8400-e29b-41d4-a716-446655440017"
    }
  }
}
```

**Error Responses:**
```json
// 403 Forbidden - Not Recipient
{
  "status": "error",
  "message": "You do not have permission to view this notification."
}

// 404 Not Found
{
  "status": "error",
  "message": "Notification not found."
}
```

---

### 6.3 Update Notification (Mark Read/Unread)

**Endpoint:** `PATCH /api/v1/notifications/{id}/`
**Auth:** Required (Recipient only)

**URL Parameters:**

| Param | Type | Description |
|---|---|---|
| id | UUID | ID of the notification |

**Request:**
```json
{
  "is_read": true
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Notification updated successfully.",
  "data": {
    "id": "150e8400-e29b-41d4-a716-446655440015",
    "notification_type": "LIKE",
    "title": "jane_doe liked your update",
    "body": "jane_doe liked 'Week 1: Research & Planning'",
    "is_read": true,
    "read_at": "2026-07-25T10:05:00Z",
    "created_at": "2026-07-25T10:00:00Z",
    "actor": {"...": "..."},
    "target_type": "journeyupdate",
    "target_id": "170e8400-e29b-41d4-a716-446655440017",
    "target_detail": {"...": "..."}
  }
}
```

---

### 6.4 Mark All Notifications Read

**Endpoint:** `POST /api/v1/notifications/mark-all-read/`
**Auth:** Required

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "5 notifications marked as read.",
  "data": {
    "updated_count": 5
  }
}
```

---

### 6.5 Get Unread Count

**Endpoint:** `GET /api/v1/notifications/unread-count/`
**Auth:** Required

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Unread count retrieved successfully.",
  "data": {
    "unread_count": 5
  }
}
```

---

## 7. HTML Sanitization Rules

All content fields in comments, replies, and accepted solutions are sanitized to prevent XSS.

**Allowed HTML Tags:**
```
p, br, strong, em, u, s, ul, ol, li,
blockquote, code, pre, h1, h2, h3, h4, h5, h6,
a, img, span, div, hr
```

**Allowed Attributes:**
- `a`: href, target, rel, title
- `img`: src, alt, width, height, loading
- `span`, `div`: style
- `*`: class, id, title

**Allowed CSS Properties:**
```
color, background-color, font-size, font-weight,
text-align, text-decoration, margin, padding,
border, border-radius, width, height
```

**Blocked (Automatically Removed):**
- `<script>` tags and any JavaScript
- `onclick`, `onerror`, `onload` and other event handlers
- `javascript:` URLs
- `data:` URLs (except images)
- Inline event handlers

---

## 8. Rate Limits

| Endpoint | Limit | Window |
|---|---|---|
| POST /updates/{id}/like/ | 60 requests | 1 hour |
| DELETE /updates/{id}/unlike/ | 60 requests | 1 hour |
| POST /updates/{id}/comments/create/ | 30 requests | 1 hour |
| PATCH /comments/{id}/ | 30 requests | 1 hour |
| DELETE /comments/{id}/ | 30 requests | 1 hour |
| POST /comments/{id}/replies/create/ | 30 requests | 1 hour |
| PATCH /replies/{id}/ | 30 requests | 1 hour |
| DELETE /replies/{id}/ | 30 requests | 1 hour |
| POST /updates/{id}/accept-solution/ | 10 requests | 1 hour |
| POST /journeys/{id}/save/ | 30 requests | 1 hour |
| DELETE /journeys/{id}/unsave/ | 30 requests | 1 hour |

---

## 9. Permission Summary

| Endpoint | Permission |
|---|---|
| POST /updates/{id}/like/ | IsAuthenticated |
| DELETE /updates/{id}/unlike/ | IsAuthenticated |
| GET /updates/{id}/comments/ | IsAuthenticatedOrReadOnly |
| POST /updates/{id}/comments/create/ | IsAuthenticated |
| GET /comments/{id}/ | IsAuthenticatedOrReadOnly |
| PATCH /comments/{id}/ | IsCommentAuthor |
| DELETE /comments/{id}/ | IsCommentAuthor |
| GET /comments/{id}/replies/ | IsAuthenticatedOrReadOnly |
| POST /comments/{id}/replies/create/ | IsAuthenticated |
| GET /replies/{id}/ | IsAuthenticatedOrReadOnly |
| PATCH /replies/{id}/ | IsReplyAuthor |
| DELETE /replies/{id}/ | IsReplyAuthor |
| GET /updates/{id}/accepted-solution/ | IsAuthenticatedOrReadOnly |
| POST /updates/{id}/accept-solution/ | CanAcceptSolution (Journey Owner) |
| DELETE /updates/{id}/remove-accepted/ | CanRemoveAcceptedSolution (Journey Owner) |
| GET /journeys/saved/ | IsAuthenticated |
| POST /journeys/{id}/save/ | IsAuthenticated |
| DELETE /journeys/{id}/unsave/ | IsAuthenticated |
| GET /notifications/ | IsAuthenticated |
| GET /notifications/{id}/ | IsNotificationRecipient |
| PATCH /notifications/{id}/ | IsNotificationRecipient |
| POST /notifications/mark-all-read/ | IsAuthenticated |
| GET /notifications/unread-count/ | IsAuthenticated |

---

## 10. Summary of All Reaction Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/updates/{id}/like/` | Required | Like an update |
| DELETE | `/updates/{id}/unlike/` | Required | Remove like |
| GET | `/updates/{id}/comments/` | Optional | List comments |
| POST | `/updates/{id}/comments/create/` | Required | Create comment |
| GET | `/comments/{id}/` | Optional | Get comment |
| PATCH | `/comments/{id}/` | Required | Update comment |
| DELETE | `/comments/{id}/` | Required | Delete comment |
| GET | `/comments/{id}/replies/` | Optional | List replies |
| POST | `/comments/{id}/replies/create/` | Required | Create reply |
| GET | `/replies/{id}/` | Optional | Get reply |
| PATCH | `/replies/{id}/` | Required | Update reply |
| DELETE | `/replies/{id}/` | Required | Delete reply |
| GET | `/updates/{id}/accepted-solution/` | Optional | Get accepted solution |
| POST | `/updates/{id}/accept-solution/` | Required | Accept solution |
| DELETE | `/updates/{id}/remove-accepted/` | Required | Remove accepted |
| GET | `/journeys/saved/` | Required | List saved journeys |
| POST | `/journeys/{id}/save/` | Required | Save journey |
| DELETE | `/journeys/{id}/unsave/` | Required | Unsave journey |
| GET | `/notifications/` | Required | List notifications |
| GET | `/notifications/{id}/` | Required | Get notification |
| PATCH | `/notifications/{id}/` | Required | Update notification |
| POST | `/notifications/mark-all-read/` | Required | Mark all read |
| GET | `/notifications/unread-count/` | Required | Get unread count |