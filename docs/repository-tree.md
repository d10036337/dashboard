# Repository Tree

The target repository is `taiwan-tradovate` / **Taiwan Tradovate (TTX Trader)**. Phase 1 creates the production foundation and reserves clean architecture module boundaries for later phases.

```text
taiwan-tradovate/
├── .env.example
├── .github/
│   └── workflows/
│       └── ci.yml
├── .gitignore
├── Dockerfile.backend
├── Dockerfile.frontend
├── README.md
├── backend/
│   ├── alembic.ini
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── health.py
│   │   │   └── router.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── exceptions.py
│   │   │   ├── logging.py
│   │   │   └── shioaji_client.py
│   │   ├── dependencies/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── health.py
│   │   ├── domain/
│   │   │   └── __init__.py
│   │   ├── main.py
│   │   ├── models/
│   │   │   └── __init__.py
│   │   ├── repositories/
│   │   │   └── __init__.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── health.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── authentication_service.py
│   │   ├── utils/
│   │   │   └── __init__.py
│   │   ├── websocket/
│   │   │   └── __init__.py
│   │   └── workers/
│   │       └── __init__.py
│   ├── migrations/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       └── .gitkeep
│   ├── pyproject.toml
│   └── tests/
│       ├── api/
│       │   └── test_auth.py
│       ├── services/
│       │   └── test_authentication_service.py
│       ├── test_health.py
│       ├── test_health_dependencies.py
│       └── test_shioaji_client.py
├── docker/
│   ├── .gitkeep
│   ├── nginx.conf
│   └── nginx.frontend.conf
├── docker-compose.yml
├── docs/
│   ├── api-specification.md
│   ├── architecture.md
│   ├── database-schema.md
│   ├── implementation-plan.md
│   ├── phase1-app-shell.md
│   └── repository-tree.md
└── frontend/
    ├── index.html
    ├── package.json
    ├── src/
    │   ├── account/
    │   ├── charts/
    │   ├── components/
    │   ├── dom/
    │   ├── hooks/
    │   ├── main.tsx
    │   ├── orders/
    │   ├── pages/
    │   │   └── App.tsx
    │   ├── positions/
    │   ├── services/
    │   ├── stores/
    │   ├── types/
    │   ├── utils/
    │   └── websocket/
    ├── tests/
    │   ├── App.test.tsx
    │   └── setup.ts
    ├── tsconfig.app.json
    ├── tsconfig.json
    ├── tsconfig.node.json
    └── vite.config.ts
```
