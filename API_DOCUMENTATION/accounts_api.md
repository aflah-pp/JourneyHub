# JourneyHub Accounts API Documentation

**Base URL:** `/api/v1/`
**Auth:** Bearer JWT token (except where noted)

---

## 1. Authentication Endpoints

### 1.1 User Registration

**Endpoint:** `POST /auth/register/`

**Request:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!",
  "terms_accepted": true
}
```

**Validation Rules:**

| Field | Rules |
|---|---|
| username | 3-30 chars, alphanumeric + underscore, unique |
| email | Valid email format, unique, no disposable domains |
| password | 10+ chars, uppercase, lowercase, digit, special char |
| first_name | Max 50 chars |
| last_name | Max 50 chars |
| terms_accepted | Must be true |

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Registration successful. Please check your email to verify your account.",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john@example.com",
    "requires_verification": true
  }
}
```

**Error Responses:**
```json
// 400 Bad Request - Duplicate Username
{
  "status": "error",
  "message": "Validation error",
  "data": {
    "errors": {
      "username": ["A user with this username already exists."]
    }
  }
}

// 400 Bad Request - Invalid Password
{
  "status": "error",
  "message": "Validation error",
  "data": {
    "errors": {
      "password": [
        "Password must contain at least 10 characters.",
        "Password must contain at least one uppercase letter."
      ]
    }
  }
}

// 400 Bad Request - Password Mismatch
{
  "status": "error",
  "message": "Validation error",
  "data": {
    "errors": {
      "confirm_password": ["Passwords do not match."]
    }
  }
}
```

---

### 1.2 Email Verification

**Endpoint:** `POST /auth/verify-email/`

**Request:**
```json
{
  "token": "NTUwZTg0MDAtZTI5Yi00MWQ0LWE3MTYtNDQ2NjU1NDQwMDAw-abc123def456"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Email verified successfully."
}
```

**Error Responses:**
```json
// 400 Bad Request - Invalid Token
{
  "status": "error",
  "message": "Invalid verification token."
}

// 400 Bad Request - Expired Token
{
  "status": "error",
  "message": "Invalid or expired verification token."
}

// 200 OK - Already Verified
{
  "status": "success",
  "message": "Email already verified."
}
```

---

### 1.3 User Login

**Endpoint:** `POST /auth/login/`

**Request:**
```json
{
  "login": "john_doe",
  "password": "SecurePass123!"
}
```
*(`login` field accepts either username or email, e.g. `john@example.com`)*

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Login successful.",
  "data": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "john_doe",
      "email": "john@example.com",
      "is_verified": true
    }
  }
}
```
> **Note:** Refresh token is set as HTTP-only cookie.

**Error Responses:**
```json
// 401 Unauthorized - Invalid Credentials
{
  "status": "error",
  "message": "Invalid credentials.",
  "data": {
    "errors": {
      "login": ["Invalid credentials."]
    }
  }
}

// 401 Unauthorized - Account Locked
{
  "status": "error",
  "message": "Account locked. Try again in 15 minutes.",
  "data": {
    "errors": {
      "login": ["Account locked. Try again in 15 minutes."]
    }
  }
}

// 401 Unauthorized - Suspended Account
{
  "status": "error",
  "message": "Account suspended. Reason: Violation of community guidelines.",
  "data": {
    "errors": {
      "login": ["Account suspended. Reason: Violation of community guidelines."]
    }
  }
}
```

---

### 1.4 Refresh Token

**Endpoint:** `POST /auth/refresh/`

**Request:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Response (401):**
```json
{
  "detail": "Token is invalid or expired"
}
```

---

### 1.5 User Logout

**Endpoint:** `POST /auth/logout/`
**Auth:** Required

**Request:** None (refresh token from cookie)

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Logout successful."
}
```

---

## 2. Password Management

### 2.1 Forgot Password

**Endpoint:** `POST /auth/password/forgot/`

**Request:**
```json
{
  "email": "john@example.com"
}
```

**Response (200 OK - Always):**
```json
{
  "status": "success",
  "message": "If an account exists with this email, a password reset link has been sent."
}
```
> **Note:** Always returns success to prevent email enumeration.

---

### 2.2 Reset Password (with token)

**Endpoint:** `POST /auth/password/reset/{uidb64}/{token}/`

**URL Parameters:**

| Param | Description |
|---|---|
| uidb64 | Base64 encoded user ID |
| token | Reset token from email |

**Request:**
```json
{
  "password": "NewSecurePass123!",
  "confirm_password": "NewSecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Password reset successfully."
}
```

**Error Response (400):**
```json
{
  "status": "error",
  "message": "Invalid or expired reset link."
}
```

---

### 2.3 Change Password (Authenticated)

**Endpoint:** `POST /auth/password/change/`
**Auth:** Required

**Request:**
```json
{
  "old_password": "CurrentPass123!",
  "new_password": "NewSecurePass123!",
  "confirm_password": "NewSecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Password changed successfully."
}
```

**Error Responses:**
```json
// 400 Bad Request - Wrong Current Password
{
  "status": "error",
  "message": "Validation error",
  "data": {
    "errors": {
      "old_password": ["Incorrect current password."]
    }
  }
}

// 400 Bad Request - Invalid New Password
{
  "status": "error",
  "message": "Validation error",
  "data": {
    "errors": {
      "new_password": ["Password must contain at least 10 characters."]
    }
  }
}
```

---

## 3. User Profile Endpoints

### 3.1 Get My Profile

**Endpoint:** `GET /auth/me/`
**Auth:** Required

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Profile retrieved successfully.",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_verified": true,
    "is_following": false,
    "profile": {
      "bio": "Software engineer passionate about building things.",
      "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/john_doe.jpg",
      "location": "San Francisco, CA",
      "website": "https://john.dev",
      "what_i_do": "Building full-stack applications",
      "following_count": 45,
      "follower_count": 120,
      "journey_count": 8
    }
  }
}
```

---

### 3.2 Update My Profile

**Endpoint:** `PATCH /auth/me/`
**Auth:** Required

**Request:**
```json
{
  "first_name": "Johnathan",
  "last_name": "Smith",
  "email": "johnathan@example.com",
  "bio": "Senior software engineer | Open source contributor",
  "avatar_url": "https://res.cloudinary.com/demo/image/upload/v1234567890/profile_pics/new_avatar.jpg",
  "avatar_public_id": "profile_pics/new_avatar",
  "location": "Austin, TX",
  "website": "https://johnathan.dev",
  "what_i_do": "Building scalable distributed systems"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Profile updated successfully.",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "johnathan@example.com",
    "first_name": "Johnathan",
    "last_name": "Smith",
    "is_verified": true,
    "is_following": false,
    "profile": {
      "bio": "Senior software engineer | Open source contributor",
      "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/new_avatar.jpg",
      "location": "Austin, TX",
      "website": "https://johnathan.dev",
      "what_i_do": "Building scalable distributed systems",
      "following_count": 45,
      "follower_count": 120,
      "journey_count": 8
    }
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
      "email": ["A user with this email already exists."]
    }
  }
}
```

---

### 3.3 Get Public User Profile

**Endpoint:** `GET /auth/users/{username}/`
**Auth:** Optional

**URL Parameters:**

| Param | Description |
|---|---|
| username | Username of the user to view |

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "User profile retrieved successfully.",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "jane_doe",
    "email": null,
    "first_name": "Jane",
    "last_name": "Doe",
    "is_verified": true,
    "is_following": true,
    "profile": {
      "bio": "UX Designer | Creating delightful experiences",
      "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/jane_doe.jpg",
      "location": "New York, NY",
      "website": "https://jane.design",
      "what_i_do": "Designing products that matter",
      "following_count": 78,
      "follower_count": 234,
      "journey_count": 12
    }
  }
}
```
> `email` is only shown if the user allows it. `is_following` is only meaningful if authenticated and following.

**Error Response (404):**
```json
{
  "status": "error",
  "message": "User not found."
}
```

---

### 3.4 Search Users

**Endpoint:** `GET /auth/users/search/?q={query}`
**Auth:** Optional

**Query Parameters:**

| Param | Description |
|---|---|
| q | Search query (username partial match) |

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Search results.",
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "john_doe",
      "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/john_doe.jpg"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "username": "john_smith",
      "avatar_url": null
    },
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "username": "johndoe_tech",
      "avatar_url": "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_200,h_200,c_fill/profile_pics/johndoe_tech.jpg"
    }
  ]
}
```

**Error Response (400):**
```json
{
  "status": "error",
  "message": "Search query required.",
  "data": []
}
```

---

## 4. Follow System

### 4.1 Follow a User

**Endpoint:** `POST /auth/users/{user_id}/follow/`
**Auth:** Required

**URL Parameters:**

| Param | Description |
|---|---|
| user_id | UUID of user to follow |

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "User followed successfully."
}
```

**Error Responses:**
```json
// 400 Bad Request - Self Follow
{
  "status": "error",
  "message": "Validation error",
  "data": {
    "errors": {
      "detail": ["You cannot follow yourself."]
    }
  }
}

// 400 Bad Request - Already Following
{
  "status": "error",
  "message": "Validation error",
  "data": {
    "errors": {
      "detail": ["You are already following this user."]
    }
  }
}

// 404 Not Found
{
  "status": "error",
  "message": "User not found."
}
```

---

### 4.2 Unfollow a User

**Endpoint:** `DELETE /auth/users/{user_id}/unfollow/`
**Auth:** Required

**URL Parameters:**

| Param | Description |
|---|---|
| user_id | UUID of user to unfollow |

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "User unfollowed successfully."
}
```

**Error Responses:**
```json
// 400 Bad Request - Not Following
{
  "status": "error",
  "message": "Validation error",
  "data": {
    "errors": {
      "detail": ["You are not following this user."]
    }
  }
}

// 404 Not Found
{
  "status": "error",
  "message": "User not found."
}
```

---

## 5. User Preferences

### 5.1 Get User Preferences

**Endpoint:** `GET /auth/preferences/`
**Auth:** Required

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Preferences retrieved successfully.",
  "data": {
    "show_email": false,
    "show_full_name": true,
    "email_notifications": true,
    "show_activity_status": true,
    "allow_direct_messages": true
  }
}
```

---

### 5.2 Update User Preferences

**Endpoint:** `PATCH /auth/preferences/`
**Auth:** Required

**Request:**
```json
{
  "show_email": true,
  "show_full_name": false,
  "email_notifications": false,
  "show_activity_status": false,
  "allow_direct_messages": false
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Preferences updated successfully.",
  "data": {
    "show_email": true,
    "show_full_name": false,
    "email_notifications": false,
    "show_activity_status": false,
    "allow_direct_messages": false
  }
}
```

---

## 6. Error Response Formats

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
| 201 | Created | New resource created |
| 204 | No Content | Successful deletion |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |

---

## 7. Rate Limits

| Endpoint | Limit | Window |
|---|---|---|
| `/auth/register/` | 5 attempts | 1 hour |
| `/auth/login/` | 10 attempts | 15 minutes |
| `/auth/password/forgot/` | 3 attempts | 1 hour |
| `/auth/password/reset/` | 3 attempts | 1 hour |
| `/auth/users/search/` | 30 requests | 1 minute |
| `/auth/users/*/follow/` | 50 requests | 1 hour |

---

## 8. Authentication Headers

### For Protected Endpoints
```
Authorization: Bearer {access_token}
```

### Cookie Handling
- **Refresh Token:** Stored as HTTP-only cookie named `refresh_token`
- **Access Token:** Returned in response body, store in memory
- **CSRF:** Not required (JWT bearer token)

---

## Summary of All Account Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register/` | No | Register new user |
| POST | `/auth/verify-email/` | No | Verify email with token |
| POST | `/auth/login/` | No | Login & get tokens |
| POST | `/auth/refresh/` | No | Refresh access token |
| POST | `/auth/logout/` | Yes | Logout & blacklist token |
| POST | `/auth/password/forgot/` | No | Send reset link |
| POST | `/auth/password/reset/{uid}/{token}/` | No | Reset password |
| POST | `/auth/password/change/` | Yes | Change password |
| GET | `/auth/me/` | Yes | Get my profile |
| PATCH | `/auth/me/` | Yes | Update my profile |
| GET | `/auth/users/{username}/` | Optional | Get public profile |
| GET | `/auth/users/search/` | Optional | Search users |
| POST | `/auth/users/{user_id}/follow/` | Yes | Follow user |
| DELETE | `/auth/users/{user_id}/unfollow/` | Yes | Unfollow user |
| GET | `/auth/preferences/` | Yes | Get preferences |
| PATCH | `/auth/preferences/` | Yes | Update preferences |