# 🚀 JourneyHub Backend Setup

Quick guide to set up the **JourneyHub Backend** for local development.

---

## 📋 Prerequisites

- Python **3.12+**
- pip

Verify your installation:

```bash
python --version
pip --version
```

---

## 📦 Installation

Go to the backend folder:

```bash
cd server
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it.

**macOS / Linux**

```bash
source venv/bin/activate
```

**Windows**

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

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

> **Do not commit your `.env` file.**

---

## ▶️ Running the Project

Apply migrations:

```bash
python manage.py migrate
```

Create an admin user:

```bash
python manage.py createsuperuser
```

Start the development server:

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

Check the project for configuration issues:

```bash
python manage.py check
```

---

## 🧪 Code Quality

JourneyHub uses **Black** for formatting and **Ruff** for linting.

### Format the code

```bash
black .
```

### Check formatting

```bash
black --check .
```

### Check linting

```bash
ruff check .
```

### Auto-fix lint issues

```bash
ruff check . --fix
```

---

## 📂 Project Modules

| Module | Purpose |
|---------|---------|
| **accounts** | Authentication, profiles, follow system |
| **journey** | Journeys, updates, tags, images |
| **reaction** | Likes, comments, replies, bookmarks |
| **feed** | Latest, following, trending feeds |
| **score** | Builder score & leaderboard |
| **audit** | Reports & activity logs |
| **shared** | Common utilities & pagination |

---

## ⚙️ Useful Commands

| Task | Command |
|------|---------|
| Run server | `python manage.py runserver` |
| Run tests | `python manage.py test` |
| Project check | `python manage.py check` |
| Create migrations | `python manage.py makemigrations` |
| Apply migrations | `python manage.py migrate` |
| Create superuser | `python manage.py createsuperuser` |
| Update trending scores | `python manage.py update_trending_scores` |
| Format code | `black .` |
| Check formatting | `black --check .` |
| Lint project | `ruff check .` |
| Auto-fix lint issues | `ruff check . --fix` |

---

## 📚 API Documentation

| Documentation | URL |
|---------------|-----|
| **Swagger UI** | `http://localhost:8000/api/docs/` |
| **OpenAPI Schema** | `http://localhost:8000/api/schema/` |

---

## ✅ Before You Push

Run these commands before creating a Pull Request:

```bash
black .

ruff check . --fix

black --check .

ruff check .

python manage.py check

python manage.py test
```

If you've changed models, also run:

```bash
python manage.py makemigrations

python manage.py migrate
```

---

## 📄 License

Licensed under the **MIT License**.

---

<div align="center">

### 🚀 JourneyHub Backend

Built with **Django**, **Django REST Framework**, **PostgreSQL**, and **Cloudinary**.

</div>