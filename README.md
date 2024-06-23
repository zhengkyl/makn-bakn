# makn ba<sub>c</sub>k<sub>e</sub>n<sub>d</sub>

## Setup

Initialize database tables.

```sh
python app/init_db.py
```

### Development
```sh
fastapi dev
```

### Production
```sh
fastapi run
```

## Environment bariables

Loaded via `.env` in dev

`OPENAI_API_KEY`

`DATABASE_URL`

`GOOGLE_CLIENT_ID`

`GOOGLE_CLIENT_SECRET`

`GOOGLE_REDIRECT_URI`

Set with `fly secrets set` for prod, except for `DATABASE_URL` which is automatic b/c using Fly Postgres.