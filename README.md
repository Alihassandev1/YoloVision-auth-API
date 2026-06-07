# FastAPI YOLO Vision Backend

FastAPI backend for user authentication, admin user management, and YOLO image inference. The API is designed around JWT bearer authentication, SQLAlchemy/PostgreSQL persistence, Alembic migrations, and Ultralytics YOLO models for detection, segmentation, classification, and pose estimation.

## Current Project Status

The current working tree contains the main FastAPI app, admin routes, YOLO routes, Alembic migrations, model weights, and generated image outputs. The `auth` package source files are currently missing from the working tree; only `auth/__pycache__/` exists. Because `main.py`, `admin/*`, `yolomodels/*`, and Alembic import `auth.models`, `auth.routes`, `auth.schemas`, `auth.crud`, and `auth.utils`, the app will not start until those Python source files are restored.

The README below documents the project according to the current source files plus the recoverable auth API surface referenced by cached bytecode and imports.

## Features

- FastAPI application with router-based modules.
- JWT bearer authentication with Argon2 password hashing.
- User registration, login, profile update, password change, avatar upload, and account deletion routes.
- Authenticated admin routes for listing, creating, reading, updating, and deleting users.
- YOLO image inference for four modes:
  - Detection
  - Segmentation
  - Classification
  - Pose estimation
- Uploaded images are validated with Pillow before inference.
- Annotated inference results are saved under `Images/{user_id}/...`.
- Inference history is stored in the `userhistory` table.
- PostgreSQL database access through SQLAlchemy.
- Alembic migration setup.
- Interactive API docs through FastAPI at `/docs` and `/redoc`.

## Tech Stack

| Area | Technology |
| --- | --- |
| API framework | FastAPI |
| ASGI server | Uvicorn |
| ORM | SQLAlchemy |
| Database | PostgreSQL |
| Migrations | Alembic |
| Authentication | JWT with `python-jose` |
| Password hashing | Passlib Argon2 |
| Image validation | Pillow |
| Computer vision | Ultralytics YOLO |
| Package manager | uv |
| Python version | 3.13 |

## Project Structure

```text
backend/
|-- main.py                  # FastAPI app and router registration
|-- database.py              # SQLAlchemy engine, session, Base, env loading
|-- pyproject.toml           # Project metadata and dependencies
|-- uv.lock                  # Locked dependency graph
|-- alembic.ini              # Alembic configuration
|-- .python-version          # Python 3.13
|
|-- auth/
|   `-- __pycache__/         # Source files are currently missing
|
|-- admin/
|   |-- routes.py            # /admin routes
|   |-- crud.py              # User admin database operations
|   |-- schemas.py           # Admin schemas and auth schema re-exports
|   `-- __init__.py
|
|-- yolomodels/
|   |-- routes.py            # /yoloModels routes
|   |-- utils.py             # Model loading, validation, inference, history save
|   `-- __init__.py
|
|-- alembic/
|   |-- env.py
|   |-- script.py.mako
|   `-- versions/
|
|-- models/
|   |-- yolo26n.pt
|   |-- yolo26n-seg.pt
|   |-- yolo26n-cls.pt
|   `-- yolo26n-pose.pt
|
|-- Images/                  # Saved avatars and annotated inference outputs
|-- env/
|   `-- .env                 # DATABASE_URL and SECRET_KEY
|
|-- cv_script.py             # Local request/CV experiment script
|-- trt.py                   # Older YOLO utility experiment
`-- data.json                # Local generated experiment data
```

## Requirements

- Python 3.13
- PostgreSQL
- uv
- Restored `auth/*.py` source files
- YOLO model files in `models/`

Install `uv` if needed:

```bash
pip install uv
```

## Environment Variables

`database.py` loads environment variables from `env/.env`.

Create or update `backend/env/.env`:

```env
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/Fastapi_Project
SECRET_KEY=replace-with-a-long-random-secret
```

Do not commit real database passwords or production secrets.

## Installation

From the `backend` directory:

```bash
uv sync
```

If using a traditional virtual environment instead:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

## Database Setup

Make sure PostgreSQL is running and `DATABASE_URL` points to an existing database.

Apply migrations:

```bash
alembic upgrade head
```

Create a new migration after model changes:

```bash
alembic revision --autogenerate -m "describe your change"
```

Important: Alembic imports `auth.models`, so migrations also require the missing auth source files to be restored.

## Run the API

```bash
uvicorn main:app --reload
```

Open:

- API root: `http://127.0.0.1:8000/`
- Swagger docs: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

The root route returns:

```json
{
  "Hello": "World"
}
```

## Authentication

Protected routes expect a bearer token:

```http
Authorization: Bearer <access_token>
```

The auth utilities referenced by the project use:

- `SECRET_KEY` from `database.py`
- JWT algorithm `HS256`
- token payload containing the user `id`
- Passlib Argon2 password hashing
- `current_user` dependency for protected routes

## API Routes

### Auth Routes

Mounted in `main.py` with prefix `/auth`.

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| POST | `/auth/register/` | No | Register a user |
| POST | `/auth/login` | No | Login and return an access token |
| GET | `/auth/me` | Yes | Return the current user profile |
| POST | `/auth/me/update-password` | Yes | Change the current user's password |
| PUT | `/auth/user/me` | Yes | Update first name, last name, username, or email |
| POST | `/auth/user/me` | Yes | Upload the current user's avatar image |
| DELETE | `/auth/user/me/logout` | Yes | Delete the current user account |

Register body:

```json
{
  "first_name": "Ali",
  "last_name": "Hassan",
  "username": "alihassan",
  "email": "ali@example.com",
  "password": "strong-password"
}
```

Login body:

```json
{
  "email": "ali@example.com",
  "password": "strong-password"
}
```

### Admin Routes

Mounted in `main.py` with prefix `/admin`.

All routes depend on `current_user`. The role check in `admin/routes.py` is currently commented out, so the code protects these routes by authentication but does not currently enforce `isSuperUser`.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/admin/users/` | List all users |
| GET | `/admin/user/{user_id}` | Get one user by ID |
| POST | `/admin/user` | Create a new user |
| PUT | `/admin/user/me` | Update the authenticated user's profile |
| DELETE | `/admin/user/{user_id}/delete` | Delete a user by ID |

### YOLO Routes

Mounted in `main.py` with prefix `/yoloModels`.

All routes require authentication. Each route accepts a multipart file field named `file`, validates that the upload is an image, runs the selected model, saves the annotated result, creates a `UserHistory` record, and returns the saved image as a file response.

| Method | Path | Mode |
| --- | --- | --- |
| POST | `/yoloModels/upload-detection-image` | Detection |
| POST | `/yoloModels/upload-segmentation-image` | Segmentation |
| POST | `/yoloModels/upload-classification-image` | Classification |
| POST | `/yoloModels/upload-pose-image` | Pose |
| POST | `/yoloModels/perform_different_modes?check=Detection` | Selected by `check` query parameter |

Allowed file extensions:

```text
.png, .jpg, .jpeg
```

Example request:

```bash
curl -X POST "http://127.0.0.1:8000/yoloModels/upload-detection-image" \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@image.jpg"
```

Example selectable mode request:

```bash
curl -X POST "http://127.0.0.1:8000/yoloModels/perform_different_modes?check=Segmentation" \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@image.jpg"
```

Valid `check` values:

```text
Detection
Segmentation
Classification
Pose
```

## YOLO Model Files

The project loads models at import time in `yolomodels/utils.py`, so these files must exist before the API starts:

| File | Purpose |
| --- | --- |
| `models/yolo26n.pt` | Detection |
| `models/yolo26n-seg.pt` | Segmentation |
| `models/yolo26n-cls.pt` | Classification |
| `models/yolo26n-pose.pt` | Pose estimation |

## Saved Files

Inference outputs are saved under:

```text
Images/{user_id}/detection/{filename}
Images/{user_id}/segmentation/{filename}
Images/{user_id}/classification/{filename}
Images/{user_id}/pose/{filename}
```

Avatar uploads are saved under:

```text
Images/{user_id}/avatars/{filename}
```

The current `Images/` directory contains generated local outputs. These are runtime artifacts and are normally excluded from source control.

## Database Tables

The SQLAlchemy models referenced by the project are `User` and `UserHistory`.

### users

| Column | Description |
| --- | --- |
| `id` | Primary key |
| `firstName` | User first name |
| `lastName` | User last name |
| `username` | Username |
| `isSuperUser` | Admin flag |
| `email` | Email address |
| `password` | Hashed password |
| `avatar` | Avatar path |
| `created_at` | Creation timestamp |

### userhistory

| Column | Description |
| --- | --- |
| `id` | Primary key |
| `user_id` | Foreign key to `users.id` |
| `images` | Saved result image path |
| `img_type` | Inference mode |

## Development Notes

- `main.py` calls `models.Base.metadata.create_all(bind=engine)` and also includes Alembic migrations. In a migration-managed project, prefer using Alembic consistently for schema changes.
- `database.py` loads `env/.env`, not the top-level `.env` file.
- `yolomodels/utils.py` loads all YOLO models during module import. Startup will fail if any model file is missing.
- `cv_script.py` contains local testing code, including a hard-coded sample token. Treat it as a development scratch file and do not use real tokens in committed code.
- `trt.py` appears to be an older experimental YOLO helper and is not imported by `main.py`.

## Troubleshooting

### `ModuleNotFoundError: No module named 'auth.models'`

Restore the missing `auth` source files:

```text
auth/__init__.py
auth/models.py
auth/schemas.py
auth/crud.py
auth/utils.py
auth/routes.py
```

### Database connection errors

Check that:

- PostgreSQL is running.
- The database in `DATABASE_URL` exists.
- Credentials in `env/.env` are correct.
- The URL uses a supported SQLAlchemy driver, for example `postgresql+psycopg2://...`.

### YOLO model loading errors

Check that all four `.pt` files exist in `models/` and that the process starts from the `backend` directory so relative paths resolve correctly.
