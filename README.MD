
<div align="center">

# JourneyHub

**A social platform for documenting the process of building things—not just the final result.**

[![React](https://img.shields.io/badge/Frontend-React-61DAFB?logo=react&logoColor=white)]()
[![Django](https://img.shields.io/badge/Backend-Django-092E20?logo=django&logoColor=white)]()
[![Django REST Framework](https://img.shields.io/badge/API-Django_REST_Framework-red)]()
[![Cloudinary](https://img.shields.io/badge/Media-Cloudinary-3448C5?logo=cloudinary&logoColor=white)]()
[![JWT](https://img.shields.io/badge/Auth-JWT-black)]()
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

</div>

---

# 📖 Overview

JourneyHub is a **social platform** where creators share the complete journey of building something—not just the finished product.

Whether you're building:

- 🚀 Startups
- 💻 Software Projects
- 🤖 AI Applications
- 📱 Mobile Apps
- 🎨 Design Projects
- 📚 Learning Roadmaps
- 🔧 Hardware Projects
- 🌍 Open Source Contributions
- 💭 Or any other things

JourneyHub enables builders to document every milestone, receive feedback, ask for help, celebrate progress, and build a public record of their work.

---

# ✨ Features

## 👤 Authentication & Accounts

- JWT Authentication
- User Registration
- Login & Logout
- Refresh Tokens
- Email Verification
- Forgot Password
- Password Reset
- Change Password
- User Profiles
- Profile Pictures
- User Preferences
- Follow / Unfollow Users

---

## 📚 Journey Management

- Create Journey
- Edit Journey
- Soft Delete Journey
- Public & Private Visibility
- Progress Tracking
- Journey Categories
- Cover Images
- Ownership Validation

---

## 📝 Journey Updates

- Publish Progress Updates
- Upload Multiple Images
- Progress Percentage
- Milestones
- Help Needed Posts
- Tags
- Timeline View
- Visibility Controls

---

## ❤️ Community Interaction

- Like Updates
- Unlike Updates
- Comments
- Replies
- Bookmarks
- Notifications
- Accepted Solutions

---

## 🏆 Builder Score System

Automatically calculates user reputation based on meaningful contributions.

### Score Categories

- 📅 Consistency
- 💬 Engagement
- 🎯 Milestones
- 🌟 Influence

Includes:

- Anti-spam protection
- Score history
- Automatic recalculation

---

## 📰 Feed System

Optimized feeds include:

- Latest
- Following
- Trending
- Help Needed

Features:

- Cursor Pagination
- Infinite Scrolling
- Optimized Database Queries

---

## 🛡 Moderation & Audit

- Report Users
- Report Content
- Activity Logs
- Moderation Workflow
- Audit Trail

---

## ☁️ Media Management

Powered by Cloudinary.

Supports:

- Avatar Uploads
- Journey Covers
- Update Images
- Automatic Image Optimization

---

# 🛠 Tech Stack

| Layer | Technology |
|--------|------------|
| **Frontend** | React + Tailwind CSS |
| **Backend** | Django 5 + Django REST Framework |
| **Authentication** | JWT (SimpleJWT) |
| **Database** | PostgreSQL (Supabase Compatible) |
| **Media Storage** | Cloudinary |
| **API Documentation** | DRF Spectacular (Swagger/OpenAPI) |

---

# 📂 Project Structure

```text
JourneyHub/
│
├── server/
│   ├── accounts/
│   ├── audit/
│   ├── config/
│   ├── feed/
│   ├── journey/
│   ├── reaction/
│   ├── score/
│   ├── shared/
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   └── src/
│
├── API_DOCUMENTATION/
│
├── LICENSE
└── README.md
```

---

# 📦 Module Responsibilities

| Module | Responsibility |
|----------|----------------|
| **accounts** | Authentication, Profiles, Preferences, Follow System |
| **journey** | Journeys, Updates, Images, Tags |
| **reaction** | Likes, Comments, Replies, Bookmarks |
| **feed** | Latest, Following, Trending, Help Needed Feeds |
| **score** | Builder Score & Leaderboards |
| **audit** | Reports, Moderation & Activity Logs |
| **shared** | Common Utilities, Pagination, Responses, Middleware |
| **config** | Django Configuration |

---

# ⚡ Quick Start

## 1️⃣ Clone Repository

```bash
git clone <repository-url>
cd JourneyHub
```

---

## 2️⃣ Backend Setup

```bash
cd server

python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
python manage.py migrate
```

Start development server:

```bash
python manage.py runserver
```

---

## 3️⃣ Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

---

# 🔐 Environment Variables

Create a `.env` file inside the `server/` directory.

```env
SECRET_KEY=

DATABASE_URL=

CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=

FRONTEND_RESET_PASSWORD_URL=
FRONTEND_VERIFY_EMAIL_URL=
```

---

# 📚 API Documentation

After running the backend server:

## Swagger UI

```text
http://localhost:8000/api/docs/
```

## OpenAPI Schema

```text
http://localhost:8000/api/schema/
```

---

## API Reference

| Module | Documentation |
|---------|---------------|
| Accounts | `API_DOCUMENTATION/accounts_api.md` |
| Journey | `API_DOCUMENTATION/journey_api.md` |
| Reaction | `API_DOCUMENTATION/reaction_api.md` |
| Feed | `API_DOCUMENTATION/feed_api.md` |
| Score | `API_DOCUMENTATION/score_api.md` |
| Audit | `API_DOCUMENTATION/audit_api.md` |

> **Note**
>
> Documentation files may occasionally lag behind implementation. Swagger/OpenAPI always reflects the latest API version.

---

# 🏗 Project Architecture

JourneyHub follows a clean layered architecture.

```text
                Client (React)
                      │
                      ▼
            Django REST Views
                      │
                      ▼
              DRF Serializers
                      │
                      ▼
             Service Layer
                      │
                      ▼
            Django ORM Models
                      │
                      ▼
               PostgreSQL
```

### Architecture Principles

- Thin Views
- Business Logic in Services
- Reusable Serializers
- Modular Apps
- Separation of Concerns
- Scalable API Design

---

# 📈 Builder Score System

| Category | Points | Anti-Spam Protection |
|------------|---------|----------------------|
| Consistency | +5 / Update | Max 3 updates/day |
| Engagement | +2 / Comment<br>+1 / Like | Max 10 comments/day<br>100 likes/week |
| Milestones | +15 Milestone<br>+50 Completed Journey | Awarded once |
| Influence | +25 Accepted Solution | Unlimited |

## Level Formula

```text
Level = floor(√(Total Score / 10)) + 1
```

---

# 🎯 Project Goals

- Encourage builders to share progress publicly.
- Reward consistency over perfection.
- Build meaningful developer portfolios.
- Foster collaboration through community engagement.
- Create an open ecosystem for makers and learners.

---

# 📜 License

Distributed under the **MIT License**.

See the **LICENSE** file for additional information.

---

<div align="center">

## 👨‍💻 Author

### Muhammed Aflah P P

**Full Stack Developer**

Made  using **React**, **Django**, and **PostgreSQL**

© 2026 JourneyHub. All Rights Reserved.

</div>