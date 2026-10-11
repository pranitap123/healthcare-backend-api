# Healthcare Backend

REST API for managing patients, doctors and patient-doctor assignments. Built with Django, Django REST Framework, PostgreSQL and JWT authentication (`djangorestframework-simplejwt`).

## Stack

- Python 3.12+
- Django 5.1, Django REST Framework
- PostgreSQL (via `psycopg` 3)
- JWT auth with `djangorestframework-simplejwt`
- OpenAPI schema and Swagger UI via `drf-spectacular`

## Project layout

```
config/     project settings, root urls, wsgi/asgi
core/       shared base model, pagination, permissions, error handling, health check
accounts/   custom email-based user model, register / login / token refresh
patients/   patient model and endpoints
doctors/    doctor model and endpoints
mappings/   patient-doctor assignments
```

## Setup

1. Create a virtual environment and install dependencies.

   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Create a PostgreSQL database.

   ```bash
   createdb healthcare
   ```

3. Copy `.env.example` to `.env` and fill in the values (`DJANGO_SECRET_KEY` is mandatory).

4. Apply migrations and start the server.

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

### Docker

```bash
docker compose up --build
```

The API is served on `http://localhost:8000`. Migrations run on start.

## Configuration

All sensitive configuration is read from environment variables (or `.env`).

| Variable | Purpose | Default |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Django secret key (required) | - |
| `DJANGO_DEBUG` | Debug mode | `False` |
| `DJANGO_ALLOWED_HOSTS` | Comma separated hosts | `localhost,127.0.0.1` |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | PostgreSQL connection | `healthcare`, `postgres`, empty, `localhost`, `5432` |
| `JWT_ACCESS_MINUTES` | Access token lifetime | `30` |
| `JWT_REFRESH_DAYS` | Refresh token lifetime | `7` |
| `AUTH_THROTTLE_RATE` | Rate limit on auth endpoints | `20/min` |

## API

Interactive docs: `http://localhost:8000/api/docs/` (schema at `/api/schema/`). Send the access token as `Authorization: Bearer <token>`.

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/api/auth/register/` | Register with `name`, `email`, `password` |
| POST | `/api/auth/login/` | Returns `access` and `refresh` tokens |
| POST | `/api/auth/token/refresh/` | Exchange a refresh token for a new access token |
| POST | `/api/patients/` | Create a patient |
| GET | `/api/patients/` | List patients created by the authenticated user |
| GET | `/api/patients/<id>/` | Patient details |
| PUT | `/api/patients/<id>/` | Update a patient |
| DELETE | `/api/patients/<id>/` | Delete a patient |
| POST | `/api/doctors/` | Create a doctor |
| GET | `/api/doctors/` | List all doctors (`?specialization=` filter) |
| GET | `/api/doctors/<id>/` | Doctor details |
| PUT | `/api/doctors/<id>/` | Update a doctor (creator only) |
| DELETE | `/api/doctors/<id>/` | Delete a doctor (creator only) |
| POST | `/api/mappings/` | Assign a doctor to one of your patients |
| GET | `/api/mappings/` | List mappings of your patients (`?patient=`, `?doctor=`) |
| GET | `/api/mappings/<patient_id>/` | Doctors assigned to a patient |
| DELETE | `/api/mappings/<id>/` | Remove a mapping |
| GET | `/api/health/` | Liveness and database check |

### Behaviour notes

- Patients are private to the user who created them. Accessing another user's patient returns `404`.
- Doctors are a shared directory: any authenticated user can read them, only the creator can update or delete.
- A doctor can be assigned to a patient once; duplicates return `400`.
- List endpoints are paginated (`page`, `page_size`, max 100).
- Errors share one shape:

```json
{
  "error": {
    "status": 400,
    "code": "validation_error",
    "message": "Validation failed.",
    "details": {"email": ["Enter a valid email address."]}
  }
}
```

## Testing

```bash
python manage.py test
```

The test runner creates a temporary `test_<DB_NAME>` database, so the configured database user needs permission to create databases.

A Postman collection is available in `postman/healthcare.postman_collection.json`. Run **Login** first; the token and created ids are stored in collection variables automatically.
