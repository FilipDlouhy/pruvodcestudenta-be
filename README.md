# pruvodcestudenta-be

Backend of Průvodce studenta UTB, the student guide of Studentská unie UTB. The guide has sections, each section has topics, and every topic belongs to a city (location).
The public JSON API serves the sections and topics and has a text search. Staff log in to the Django admin to edit sections, topics and locations.
It is a Django rewrite of the old Laravel backend, with the same public API paths and JSON. Its frontend is the separate project `pruvodcestudenta-fe`.

## Stack

- Python 3.12, Django 5.1, Django REST Framework
- PostgreSQL 16 (Docker image `postgres:16`), driver `psycopg`
- JWT in httpOnly cookies (`djangorestframework-simplejwt`, with token blacklist)
- Pillow for image processing (WebP variants)
- WhiteNoise for static files, gunicorn (3 workers) as the server
- `django-cors-headers`, `dj-database-url`
- Docker Compose with two services: `db` and `web`
- `uv` for dependencies (`pyproject.toml`, `uv.lock`), `ruff` and `mypy` for linting

## Project structure

```
pruvodcestudenta-be/
├── docker-compose.yml     # db + web services, volumes pgdata and media
├── Makefile               # shortcuts for docker compose commands
├── .env.example           # all configuration variables
└── api/
    ├── Dockerfile
    ├── manage.py
    ├── pyproject.toml, uv.lock
    ├── config/            # settings.py, urls.py, wsgi.py
    ├── common/            # shared code: exceptions, middleware, base repository
    └── apps/
        ├── guide/         # sections, topics, locations, search, image handling, change log, seed_data command
        └── user/          # admin user model, JWT login/refresh/logout/me
```

Inside an app the layers are: controller (DRF `ViewSet`, in `controllers/`) → service (`services/`) → repository (`repositories/`, extends `common/repositories.py`) → model (`models.py`).
Request and response shapes are in `dtos.py`. The services are created once in `services/__init__.py` and the Django admin calls the same services, so admin changes are logged and images are processed the same way.

## Requirements

- Docker with Compose v2
- `make` (optional, on Windows use Git Bash)
- `uv` (only for `make lint`)

## Run locally

```bash
cp .env.example .env
```

Change these lines in `.env`:

```
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=*
DJANGO_USE_HTTPS=false
```

`DJANGO_USE_HTTPS=false` is needed because the login cookies are `Secure` otherwise and the browser would not send them over plain http. The other values (`POSTGRES_*`, `WEB_PORT=8001`) can stay as they are.

Start it and create an admin user:

```bash
make up
make superuser
```

Without make:

```bash
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

URLs (with `WEB_PORT=8001`):

- API: http://localhost:8001/api/pages/landing
- Admin: http://localhost:8001/admin/
- Uploaded images: http://localhost:8001/media/... (served by Django from the `media` volume)

On every start the `web` container runs, in this order:

1. `collectstatic --noinput` (static files for WhiteNoise)
2. `migrate`
3. `seed_data`
4. gunicorn on port 8000 inside the container (published as `WEB_PORT`)

`seed_data` loads reference data only into empty tables: the locations Zlín and Uherské Hradiště (only if there are no locations), and the eight sections of the live site (Software univerzity, Volný čas, Studentské organizace, Kam na jídlo, káva či pivo, Praktické rady, Život na univerzitě, Akademické poradny, Studium) with their real descriptions, colors and icon URLs (only if there are no sections). It never overwrites or re-creates what staff changed or deleted, so it is safe to run repeatedly. Topics are not seeded.

## Make commands

| Target | What it does |
| --- | --- |
| `make up` | `docker compose up -d --build` |
| `make down` | `docker compose down` (volumes are kept) |
| `make ps` | `docker compose ps` |
| `make logs` | follow the `web` logs |
| `make psql` | open `psql` in the `db` container |
| `make shell` | open the Django shell in the `web` container |
| `make migrate` | run `migrate` in the `web` container |
| `make seed` | run `seed_data` in the `web` container |
| `make superuser` | run `createsuperuser` in the `web` container |
| `make lint` | `ruff check` and `mypy` in `api/` (needs `uv`) |

## Configuration

Set in `.env` (read by Compose and passed to the `web` container). `DATABASE_URL` is built by `docker-compose.yml` from the `POSTGRES_*` values.

| Variable | Example / default | What it does |
| --- | --- | --- |
| `DJANGO_DEBUG` | `false` | `true` turns on Django debug mode. Anything else means off. |
| `DJANGO_SECRET_KEY` | `change-me-to-a-long-random-string` | Django secret key. With `DJANGO_DEBUG` off, the app refuses to start if it is missing. Use a long random value in production. |
| `DJANGO_ALLOWED_HOSTS` | `api.example.cz` | Comma-separated host names Django accepts (`*` for local use). |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://api.example.cz` | Comma-separated origins trusted for CSRF (needed for the admin behind HTTPS). Optional. |
| `DJANGO_USE_HTTPS` | `true` | `true` makes the session, CSRF and JWT cookies `Secure`. Set `false` for plain http locally. |
| `POSTGRES_DB` | `pruvodce` | Database name. |
| `POSTGRES_USER` | `pruvodce` | Database user. |
| `POSTGRES_PASSWORD` | `change-me` | Database password. |
| `WEB_PORT` | `8001` | Host port published for the `web` container. |

## API

All paths have no trailing slash, except the auth endpoints, which end with `/`. Public endpoints need no login.

| Method | Path | Auth | What it does |
| --- | --- | --- | --- |
| GET | `/api/pages/landing` | none | visible sections (each with an empty `topics` list) |
| POST | `/api/pages/landing/search` | none | search visible topics, max 60 requests/min |
| GET | `/api/pages/sections/{slug}` | none | a visible section with its visible topics |
| GET | `/api/pages/topics/{slug}` | none | a visible topic |
| POST | `/api/auth/login/` | none | log in with `username` and `password`, sets cookies, max 20 requests/min |
| POST | `/api/auth/refresh/` | refresh cookie | new access token cookie, 204 |
| POST | `/api/auth/logout/` | refresh cookie | blacklists the refresh token and deletes the cookies, 204 |
| GET | `/api/auth/me/` | access cookie | the logged-in user |

Notes:

- Search body: `{"query": "text", "sections": [1, 2], "locations": [1]}`. `query` is required, the two id lists are optional. It matches the text (case-insensitive) in title or description of visible topics in visible sections, and returns `{"topics": [{"title", "slug", "sectionSlug", "color"}]}`.
- A topic or section is returned only if it is `visible` (a topic also needs a visible section). Otherwise the answer is 404 `{"detail": "..."}`.
- The `image` field is an absolute URL of the 1920 px WebP variant (`/media/<folder>/<slug>.jpg.fhd.webp`), or an empty string when there is no image. In a topic, the `location` field holds the `map_url` of the topic.
- Auth: the tokens are httpOnly cookies `access_token` (15 minutes, path `/`) and `refresh_token` (1 day, path `/api/auth/`). `me` also checks the CSRF token.
- API errors are in English, the admin is in Czech. CORS is open for `/api/` paths.

## Django admin

At `/admin/`. The start page shows the number of sections, topics and locations. Models:

- **Sekce (Section)**: title, slug, description (HTML), color (color picker), icon URL, image, visible. Slug is filled from the title on create and read-only afterwards. A section with topics cannot be deleted.
- **Téma (Topic)**: title, slug, description (HTML), section, location, Google Maps embed URL, link URL, image, visible. The color is copied from the section on create and never synced afterwards (read-only). Slug is read-only after create.
- **Lokalita (Location)**: name. A location with topics cannot be deleted.
- **Logy (LogMessage)**: read-only list of the change log, filterable by level.
- **Users**: standard Django user admin (`apps.user`). These are the accounts used for the API login too.

Images: an upload is always stored as `media/sections/<slug>.jpg` or `media/topics/<slug>.jpg` and replaces the old file. Next to it, two WebP files are generated (quality 80): `<slug>.jpg.webp` (full size) and `<slug>.jpg.fhd.webp` (at most 1920 px wide). The API serves the `.fhd.webp` one. Clearing the image or deleting the item removes all three files.

Change log: every create, update and delete of a section, topic or location is saved as a `NOTICE` entry (for example "Topic created") with the data of the item and the acting user (id, username, email, name).

## Deploy

A guide for a Linux server with Docker and Compose v2.

1. Copy this folder to the server and go into it.
2. Create the config:

   ```bash
   cp .env.example .env
   ```

   Set at least: `DJANGO_DEBUG=false`, `DJANGO_SECRET_KEY` (long random string), `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS` (your domain, the latter with `https://`), `DJANGO_USE_HTTPS=true`, `POSTGRES_PASSWORD`, and `WEB_PORT` if 8001 is taken.

3. Build and start (migrations, static files and seed run automatically), then create the admin user:

   ```bash
   docker compose up -d --build
   docker compose exec web python manage.py createsuperuser
   ```

4. Put a reverse proxy with HTTPS in front of `WEB_PORT`. Example `Caddyfile` (Caddy gets the certificate by itself):

   ```
   api.example.cz {
       reverse_proxy localhost:8001
   }
   ```

   Replace the domain with yours and the port with `WEB_PORT`. The app trusts the `X-Forwarded-Proto` header from the proxy (Caddy sets it). The port is published on all interfaces, so block it in the firewall and allow only the proxy.

5. Static files are served by WhiteNoise. Uploaded images (`/media/...`) are served by Django itself from the `media` volume, no proxy rule is needed because the traffic is low.

The database port is not published, `db` is reachable only from the `web` container. Data lives in the Docker volumes `pgdata` (database) and `media` (uploaded images).

Update:

```bash
git pull   # or copy the new files
docker compose up -d --build
```

Logs:

```bash
docker compose logs -f web
docker compose logs -f db
```

Database backup and restore:

```bash
# backup
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" --clean --if-exists "$POSTGRES_DB"' > backup.sql

# restore (into the running db container)
docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" "$POSTGRES_DB"' < backup.sql
```

Backup and restore of the uploaded images (`media` volume, mounted at `/app/media` in `web`):

```bash
# backup
docker compose exec -T web tar -czf - -C /app media > media.tar.gz

# restore
docker compose exec -T web tar -xzf - -C /app < media.tar.gz
```

Back up both the database and the media files, they belong together.
