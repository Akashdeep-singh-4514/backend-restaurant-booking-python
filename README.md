# Little Lemon Backend

## Database Migrations

This project uses Alembic for database migrations. All migration commands should be run through Poetry.

### Prerequisites

1. Ensure PostgreSQL is running
2. Create the database (if it doesn't exist):
   ```bash
   createdb little-lemon
   # Or using psql:
   psql -U postgres -c "CREATE DATABASE little-lemon;"
   ```
3. Configure your `.env` file with the correct `SQLALCHEMY_DATABASE_URI`

### Migration Commands

#### Generate a new migration

Create a new migration file based on model changes:

```bash
poetry run alembic revision --autogenerate -m "description of changes"
```

Example:

```bash
poetry run alembic revision --autogenerate -m "add restaurant table"
```

#### Create an empty migration

Create an empty migration file for manual SQL:

```bash
poetry run alembic revision -m "description of changes"
```

#### Run migrations

Apply all pending migrations to the database:

```bash
poetry run alembic upgrade head
```

#### Run a specific migration

Upgrade to a specific revision:

```bash
poetry run alembic upgrade <revision_id>
```

Example:

```bash
poetry run alembic upgrade 1b040ee253bc
```

#### Revert migrations

Revert the last migration:

```bash
poetry run alembic downgrade -1
```

Revert to a specific revision:

```bash
poetry run alembic downgrade <revision_id>
```

Revert all migrations:

```bash
poetry run alembic downgrade base
```

#### Check migration status

View current migration status:

```bash
poetry run alembic current
```

View migration history:

```bash
poetry run alembic history
```

View detailed migration history:

```bash
poetry run alembic history --verbose
```

## Running the Application

Start the development server:

```bash
poetry run uvicorn src.app:app --reload
```

Or activate the Poetry shell first:

```bash
poetry shell
uvicorn src.app:app --reload
```
