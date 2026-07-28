# JourneyHub

JourneyHub is a social platform for documenting the **process** of building things, not just the final result. It helps users share progress updates, track long-term journeys, get feedback, and engage with other builders in the community.

[![React](https://img.shields.io/badge/Frontend-React-blue?logo=react)]()
[![Django](https://img.shields.io/badge/Backend-Django-green?logo=django)]()
[![DRF](https://img.shields.io/badge/API-DRF-red)]()
[![Cloudinary](https://img.shields.io/badge/Media-Cloudinary-lightgrey)]()
[![JWT](https://img.shields.io/badge/Auth-JWT-black)]()
[![License](https://img.shields.io/badge/License-MIT-yellow)]()

## Overview

JourneyHub is built for creators, developers, and builders who want to share the process behind their work instead of only showcasing finished results. Users create journeys, post updates, mark milestones, and engage with other builders through likes, comments, and a reputation-based Builder Score.

The backend is built with Django REST Framework, JWT authentication, and Cloudinary for media storage. The frontend will be built with React.

## Features

- User accounts with JWT-based authentication.
- Create and manage journeys — long-term goals or projects.
- Post chronological journey updates tracking progress.
- Like, comment, reply, and save journey updates.
- Builder Score system rewarding consistent, meaningful activity.
- Audit logging of key user actions.
- Standardized API responses, pagination, permissions, and rate limiting.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React |
| Backend | Django 5, Django REST Framework |
| Authentication | JWT |
| Media Storage | Cloudinary |
| Database | SQLite (development) |
| Email | Django SMTP backend |

## Project Structure

```
server/
├── accounts/       # Custom user model, JWT auth, registration/login
├── audit/          # Activity/audit logging
├── config/         # Django project settings, root URLs, ASGI/WSGI
├── journey/        # Journeys and journey updates
├── reaction/       # Likes, comments, replies, saves
├── score/          # Builder Score system and history
├── shared/         # Pagination, permissions, throttles, responses,
│                   # cookies, email, JWT services
├── db.sqlite3
├── manage.py
├── pyproject.toml
└── requirements.txt

frontend/           # React app
```

## Core Concepts

### Journey
A long-term goal, project, or challenge a user is working on — building a product, learning a skill, or anything with a process worth documenting.

### Journey Update
A post inside a journey, published chronologically, representing progress on that journey.

### Reactions
Likes, comments, replies, and saves on journey updates — how the community engages with a builder's progress.

### Builder Score
A reputation system that rewards meaningful activity such as posting updates and receiving engagement, with a full score history for auditability.

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js
- Cloudinary account

### Backend Setup

```bash
cd server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

Create a `.env` file in `server/`:

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Debug mode toggle |
| `DATABASE_URL` | Database connection string |
| `CLOUDINARY_URL` | Cloudinary media storage |
| `JWT_SECRET` | JWT signing secret |

## Key Modules

- Authentication (`accounts`)
- Journeys and journey updates (`journey`)
- Reactions: likes, comments, replies, saves (`reaction`)
- Builder Score (`score`)
- Audit logging (`audit`)
- Shared infrastructure: pagination, permissions, throttling, responses, cookies, email, JWT (`shared`)

## Architecture Notes

- Django owns all business logic; the database layer stays portable.
- Business logic lives in a `service.py` layer within each app, separate from views and serializers.
- Denormalized counters and soft-delete patterns are used where relevant to keep feed and list queries fast.

## License

MIT License — see [LICENSE](LICENSE) for details.