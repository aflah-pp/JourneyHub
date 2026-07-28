# JourneyHub Audit Module API Documentation

**Base URL:** `/api/v1/`
**Auth:** Bearer JWT token (except where noted)

---

## 1. Report Endpoints

### 1.1 Create Report

**Endpoint:** `POST /api/v1/reports/create/`
**Auth:** Required

**Request:**
```json
{
  "content_type": "journey",
  "object_id": "550e8400-e29b-41d4-a716-446655440000",
  "reason": "SPAM",
  "description": "This content appears to be spam..."
}
```
> `content_type` accepts: `journey`, `journeyupdate`, `comment`, `commentreply`

**Content Types:**

| Type | Model |
|---|---|
| journey | Journey |
| journeyupdate | JourneyUpdate |
| comment | Comment |
| commentreply | CommentReply |

**Report Reasons:**

| Reason | Description |
|---|---|
| SPAM | Spam content |
| HARASSMENT | Harassment or bullying |
| INAPPROPRIATE | Inappropriate content |
| COPYRIGHT | Copyright infringement |
| PRIVACY | Privacy violation |
| OTHER | Other reason |

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Report submitted successfully.",
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "reporter": {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "username": "john_doe",
      "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/john_doe.jpg"
    },
    "target_type": "journey",
    "target_id": "550e8400-e29b-41d4-a716-446655440000",
    "reason": "SPAM",
    "reason_label": "Spam",
    "description": "This content appears to be spam...",
    "status": "PENDING",
    "status_label": "Pending",
    "moderator": null,
    "resolved_at": null,
    "resolution_note": "",
    "ip_address": "192.168.1.100",
    "created_at": "2026-07-25T10:00:00Z",
    "updated_at": "2026-07-25T10:00:00Z"
  }
}
```

**Error Responses:**
```json
// 400 Bad Request - Duplicate Report
{
  "status": "error",
  "message": "You have already reported this item."
}

// 400 Bad Request - Rate Limit
{
  "status": "error",
  "message": "Rate limit exceeded. You can only submit 10 reports per day."
}

// 400 Bad Request - Invalid Content Type
{
  "status": "error",
  "message": "Validation error",
  "data": {
    "errors": {
      "content_type": ["Invalid content_type. Allowed: ['journey', 'journeyupdate', 'comment', 'commentreply']"]
    }
  }
}

// 400 Bad Request - Target Not Found
{
  "status": "error",
  "message": "Validation error",
  "data": {
    "errors": {
      "object_id": ["Target object does not exist."]
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

### 1.2 List Reports

**Endpoint:** `GET /api/v1/reports/`
**Auth:** Required

**Query Parameters:**

| Param | Type | Description |
|---|---|---|
| page | int | Page number |
| page_size | int | Items per page (max 50) |
| status | string | Filter by status |
| reason | string | Filter by reason |
| search | string | Search in description/resolution_note |
| ordering | string | Order by: created_at, status, resolved_at |

**Response (200 OK) - Regular User:**
```json
{
  "status": "success",
  "message": "Reports retrieved successfully.",
  "data": {
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "reporter": {
          "id": "770e8400-e29b-41d4-a716-446655440002",
          "username": "john_doe",
          "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/john_doe.jpg"
        },
        "target_type": "journey",
        "target_id": "550e8400-e29b-41d4-a716-446655440000",
        "reason": "SPAM",
        "reason_label": "Spam",
        "description": "This content appears to be spam...",
        "status": "PENDING",
        "status_label": "Pending",
        "moderator": null,
        "resolved_at": null,
        "resolution_note": "",
        "ip_address": "192.168.1.100",
        "created_at": "2026-07-25T10:00:00Z",
        "updated_at": "2026-07-25T10:00:00Z"
      }
    ]
  }
}
```

**Response (200 OK) - Moderator/Staff:**
```json
{
  "status": "success",
  "message": "Reports retrieved successfully.",
  "data": {
    "count": 25,
    "next": "http://localhost:8000/api/v1/reports/?page=2",
    "previous": null,
    "results": [
      {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "reporter": {
          "id": "770e8400-e29b-41d4-a716-446655440002",
          "username": "john_doe",
          "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/john_doe.jpg"
        },
        "target_type": "journey",
        "target_id": "550e8400-e29b-41d4-a716-446655440000",
        "reason": "SPAM",
        "reason_label": "Spam",
        "description": "This content appears to be spam...",
        "status": "PENDING",
        "status_label": "Pending",
        "moderator": null,
        "resolved_at": null,
        "resolution_note": "",
        "ip_address": "192.168.1.100",
        "created_at": "2026-07-25T10:00:00Z",
        "updated_at": "2026-07-25T10:00:00Z"
      }
    ]
  }
}
```

**Error Responses:**
```json
// 401 Unauthorized
{
  "status": "error",
  "message": "Authentication credentials were not provided."
}
```

---

### 1.3 Get Report Detail

**Endpoint:** `GET /api/v1/reports/{id}/`
**Auth:** Required (Reporter or Moderator)

**URL Parameters:**

| Param | Type | Description |
|---|---|---|
| id | UUID | ID of the report |

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Report retrieved successfully.",
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "reporter": {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "username": "john_doe",
      "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/john_doe.jpg"
    },
    "target_type": "journey",
    "target_id": "550e8400-e29b-41d4-a716-446655440000",
    "reason": "SPAM",
    "reason_label": "Spam",
    "description": "This content appears to be spam...",
    "status": "PENDING",
    "status_label": "Pending",
    "moderator": null,
    "resolved_at": null,
    "resolution_note": "",
    "ip_address": "192.168.1.100",
    "created_at": "2026-07-25T10:00:00Z",
    "updated_at": "2026-07-25T10:00:00Z"
  }
}
```

**Error Responses:**
```json
// 403 Forbidden - Not Reporter or Moderator
{
  "status": "error",
  "message": "You do not have permission to view this report."
}

// 404 Not Found
{
  "status": "error",
  "message": "Report not found."
}
```

---

### 1.4 Resolve Report (Moderator Only)

**Endpoint:** `PATCH /api/v1/reports/{id}/`
**Auth:** Required (Moderator/Staff only)

**URL Parameters:**

| Param | Type | Description |
|---|---|---|
| id | UUID | ID of the report |

**Request (Resolve):**
```json
{
  "status": "RESOLVED",
  "note": "Content has been removed by moderators."
}
```

**Request (Dismiss):**
```json
{
  "status": "DISMISSED",
  "note": "No violation found after review."
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Report resolved successfully.",
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "reporter": {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "username": "john_doe",
      "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/john_doe.jpg"
    },
    "target_type": "journey",
    "target_id": "550e8400-e29b-41d4-a716-446655440000",
    "reason": "SPAM",
    "reason_label": "Spam",
    "description": "This content appears to be spam...",
    "status": "RESOLVED",
    "status_label": "Resolved",
    "moderator": {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "username": "moderator",
      "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/moderator.jpg"
    },
    "resolved_at": "2026-07-25T11:00:00Z",
    "resolution_note": "Content has been removed by moderators.",
    "ip_address": "192.168.1.100",
    "created_at": "2026-07-25T10:00:00Z",
    "updated_at": "2026-07-25T11:00:00Z"
  }
}
```

**Error Responses:**
```json
// 403 Forbidden - Not Moderator
{
  "status": "error",
  "message": "Only moderators can resolve reports."
}

// 400 Bad Request - Already Resolved
{
  "status": "error",
  "message": "This report is already resolved."
}

// 404 Not Found
{
  "status": "error",
  "message": "Report not found."
}
```

---

### 1.5 Update Report Status (Moderator Only)

**Endpoint:** `PATCH /api/v1/reports/{id}/`
**Auth:** Required (Moderator/Staff only)

**Request (Mark Under Review):**
```json
{
  "status": "UNDER_REVIEW",
  "note": "Investigating this report."
}
```

**Request (Request More Info):**
```json
{
  "status": "NEEDS_INFO",
  "note": "Please provide more details about this violation."
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Report status updated successfully.",
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "reporter": {"...": "..."},
    "target_type": "journey",
    "target_id": "550e8400-e29b-41d4-a716-446655440000",
    "reason": "SPAM",
    "reason_label": "Spam",
    "description": "This content appears to be spam...",
    "status": "UNDER_REVIEW",
    "status_label": "Under Review",
    "moderator": {"...": "..."},
    "resolved_at": null,
    "resolution_note": "Investigating this report.",
    "created_at": "2026-07-25T10:00:00Z",
    "updated_at": "2026-07-25T10:30:00Z"
  }
}
```

---

### 1.6 Get Report Statistics (Moderator Only)

**Endpoint:** `GET /api/v1/reports/stats/`
**Auth:** Required (Moderator/Staff only)

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Report statistics retrieved successfully.",
  "data": {
    "total": 25,
    "pending": 10,
    "under_review": 5,
    "resolved": 7,
    "dismissed": 3,
    "by_reason": {
      "SPAM": 12,
      "HARASSMENT": 5,
      "INAPPROPRIATE": 4,
      "COPYRIGHT": 2,
      "PRIVACY": 1,
      "OTHER": 1
    }
  }
}
```

---

## 2. Activity Log Endpoints

### 2.1 List Activity Logs

**Endpoint:** `GET /api/v1/activity-logs/`
**Auth:** Required

**Query Parameters:**

| Param | Type | Description |
|---|---|---|
| page | int | Page number |
| page_size | int | Items per page (max 50) |
| action_type | string | Filter by action type |
| user | string | Filter by user (staff only) |
| search | string | Search in metadata, user_agent, request_path |
| ordering | string | Order by: created_at, action_type |

**Action Types:**

| Action | Description |
|---|---|
| LOGIN | User login |
| LOGOUT | User logout |
| REGISTER | User registration |
| VERIFY_EMAIL | Email verification |
| PASSWORD_RESET | Password reset |
| PASSWORD_CHANGE | Password change |
| CREATE | Content created |
| UPDATE | Content updated |
| DELETE | Content deleted |
| VIEW | Content viewed |
| LIKE | Content liked |
| UNLIKE | Content unliked |
| COMMENT | Comment created |
| REPLY | Reply created |
| FOLLOW | User followed |
| UNFOLLOW | User unfollowed |
| SAVE | Content saved |
| UNSAVE | Content unsaved |
| REPORT | Report created |
| RESOLVE | Report resolved |
| SUSPEND | User suspended |
| UNSUSPEND | User unsuspended |
| BAN | User banned |
| UNBAN | User unbanned |
| ACCEPT | Solution accepted |
| REJECT | Solution rejected |

**Response (200 OK) - Regular User:**
```json
{
  "status": "success",
  "message": "Activity logs retrieved successfully.",
  "data": {
    "count": 150,
    "next": "http://localhost:8000/api/v1/activity-logs/?page=2",
    "previous": null,
    "results": [
      {
        "id": "990e8400-e29b-41d4-a716-446655440004",
        "user": {
          "id": "770e8400-e29b-41d4-a716-446655440002",
          "username": "john_doe",
          "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/john_doe.jpg"
        },
        "action_type": "LOGIN",
        "action_label": "Login",
        "target_type": null,
        "target_id": null,
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
        "request_path": "/api/v1/auth/login/",
        "request_method": "POST",
        "metadata": {},
        "created_at": "2026-07-25T09:00:00Z"
      },
      {
        "id": "aa0e8400-e29b-41d4-a716-446655440005",
        "user": {
          "id": "770e8400-e29b-41d4-a716-446655440002",
          "username": "john_doe",
          "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/john_doe.jpg"
        },
        "action_type": "CREATE",
        "action_label": "Create",
        "target_type": "journey",
        "target_id": "550e8400-e29b-41d4-a716-446655440000",
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
        "request_path": "/api/v1/journeys/create/",
        "request_method": "POST",
        "metadata": {
          "journey_title": "Building a SaaS Product"
        },
        "created_at": "2026-07-25T09:30:00Z"
      }
    ]
  }
}
```

**Response (200 OK) - Staff/Moderator:**
```json
{
  "status": "success",
  "message": "Activity logs retrieved successfully.",
  "data": {
    "count": 1250,
    "next": "http://localhost:8000/api/v1/activity-logs/?page=2",
    "previous": null,
    "results": [
      "// Same structure but shows all users' logs"
    ]
  }
}
```

---

### 2.2 Get Activity Log Detail

**Endpoint:** `GET /api/v1/activity-logs/{id}/`
**Auth:** Required (Owner or Staff)

**URL Parameters:**

| Param | Type | Description |
|---|---|---|
| id | UUID | ID of the activity log |

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Activity log retrieved successfully.",
  "data": {
    "id": "aa0e8400-e29b-41d4-a716-446655440005",
    "user": {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "username": "john_doe",
      "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/john_doe.jpg"
    },
    "action_type": "CREATE",
    "action_label": "Create",
    "target_type": "journey",
    "target_id": "550e8400-e29b-41d4-a716-446655440000",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "request_path": "/api/v1/journeys/create/",
    "request_method": "POST",
    "metadata": {
      "journey_title": "Building a SaaS Product"
    },
    "created_at": "2026-07-25T09:30:00Z"
  }
}
```

**Error Responses:**
```json
// 403 Forbidden - Not Owner or Staff
{
  "status": "error",
  "message": "You do not have permission to view this activity log."
}

// 404 Not Found
{
  "status": "error",
  "message": "Activity log not found."
}
```

---

### 2.3 Get Activity Statistics

**Endpoint:** `GET /api/v1/activity-logs/stats/`
**Auth:** Required

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Activity statistics retrieved successfully.",
  "data": {
    "total": 150,
    "by_action": {
      "LOGIN": 45,
      "LOGOUT": 30,
      "REGISTER": 1,
      "VERIFY_EMAIL": 1,
      "PASSWORD_RESET": 0,
      "PASSWORD_CHANGE": 2,
      "CREATE": 25,
      "UPDATE": 10,
      "DELETE": 3,
      "VIEW": 0,
      "LIKE": 50,
      "UNLIKE": 5,
      "COMMENT": 20,
      "REPLY": 8,
      "FOLLOW": 15,
      "UNFOLLOW": 3,
      "SAVE": 10,
      "UNSAVE": 2,
      "REPORT": 5,
      "RESOLVE": 0,
      "SUSPEND": 0,
      "UNSUSPEND": 0,
      "BAN": 0,
      "UNBAN": 0,
      "ACCEPT": 2,
      "REJECT": 0
    },
    "recent_actions": [
      {
        "id": "bb0e8400-e29b-41d4-a716-446655440006",
        "user": {"...": "..."},
        "action_type": "LIKE",
        "action_label": "Like",
        "target_type": "journeyupdate",
        "target_id": "cc0e8400-e29b-41d4-a716-446655440007",
        "created_at": "2026-07-25T10:00:00Z"
      }
    ]
  }
}
```

---

## 3. Report Status Flow

> **Note:** The original source document had a diagram placeholder here with no content. See the status table below for the full flow logic; a visual diagram should be added by whoever owns this doc.

**Status Descriptions:**

| Status | Description |
|---|---|
| PENDING | Report submitted, awaiting review |
| UNDER_REVIEW | Currently being investigated |
| NEEDS_INFO | Requires more information from reporter |
| RESOLVED | Issue resolved (content removed/action taken) |
| DISMISSED | No violation found |

---

## 4. Error Responses

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

| Status | Meaning | Use Case |
|---|---|---|
| 200 | Success | Successful operation |
| 201 | Created | Report created |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |

---

## 5. Rate Limits

| Endpoint | Limit | Window |
|---|---|---|
| POST /reports/create/ | 10 requests | 1 day |
| GET /reports/ | 60 requests | 1 minute |
| GET /reports/{id}/ | 60 requests | 1 minute |
| PATCH /reports/{id}/ | 30 requests | 1 minute |
| GET /reports/stats/ | 30 requests | 1 minute |
| GET /activity-logs/ | 60 requests | 1 minute |
| GET /activity-logs/{id}/ | 60 requests | 1 minute |
| GET /activity-logs/stats/ | 30 requests | 1 minute |

---

## 6. Permission Summary

| Endpoint | Permission | Description |
|---|---|---|
| POST /reports/create/ | IsAuthenticated | Create a report |
| GET /reports/ | IsReporterOrModerator | List reports (own or all) |
| GET /reports/{id}/ | IsReporterOrModerator | Get report detail |
| PATCH /reports/{id}/ | IsModerator | Resolve/update report |
| GET /reports/stats/ | IsModerator | Report statistics |
| GET /activity-logs/ | IsAuthenticated | List logs (own or all) |
| GET /activity-logs/{id}/ | IsAuthenticated | Get log detail |
| GET /activity-logs/stats/ | IsAuthenticated | Activity statistics |

---

## 7. Summary of All Audit Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/reports/create/` | Required | Create a report |
| GET | `/reports/` | Required | List reports |
| GET | `/reports/{id}/` | Required | Get report detail |
| PATCH | `/reports/{id}/` | Required | Resolve/update report |
| GET | `/reports/stats/` | Required | Report statistics |
| GET | `/activity-logs/` | Required | List activity logs |
| GET | `/activity-logs/{id}/` | Required | Get log detail |
| GET | `/activity-logs/stats/` | Required | Activity statistics |

---

## 8. Examples

### 8.1 Creating a Report
```bash
curl -X POST "http://localhost:8000/api/v1/reports/create/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "journey",
    "object_id": "550e8400-e29b-41d4-a716-446655440000",
    "reason": "SPAM",
    "description": "This journey contains spam content..."
  }'
```

### 8.2 Getting All Reports (User)
```bash
curl -X GET "http://localhost:8000/api/v1/reports/?status=PENDING&ordering=-created_at" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 8.3 Resolving a Report (Moderator)
```bash
curl -X PATCH "http://localhost:8000/api/v1/reports/660e8400-e29b-41d4-a716-446655440001/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "status": "RESOLVED",
    "note": "Content removed. User warned."
  }'
```

### 8.4 Getting Activity Logs
```bash
curl -X GET "http://localhost:8000/api/v1/activity-logs/?action_type=LIKE&ordering=-created_at" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 8.5 Getting Activity Statistics
```bash
curl -X GET "http://localhost:8000/api/v1/activity-logs/stats/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## 9. Data Retention

| Data Type | Retention Period | Notes |
|---|---|---|
| Reports | Permanent | Never deleted for audit purposes |
| Activity Logs | 90 days | Auto-archived after 90 days |
| Resolution Notes | Permanent | Required for audit trail |
| IP Addresses | 90 days | Logged for security, auto-removed |