# CodeLearnAI (Django MVP)

Quick start:

- Create env
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

- Env vars
```bash
cp .env .env.local  # edit OPENAI_API_KEY, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
```

- Migrate & run
```bash
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

- Admin
```bash
user: admin
pass: adminpass
```

Key endpoints:
- /api/auth/ (login/logout, token)
- /api/auth/registration/ (signup)
- /api/projects/items/ (CRUD projects)
- /api/projects/items/import_github/ (POST {token, repo})
- /api/projects/files/?project=<id>
- /api/community/questions/
- /api/ai/explain/ (POST {content, path})

UI:
- /
- /projects/<id>/ (project detail, code viewer + explain)