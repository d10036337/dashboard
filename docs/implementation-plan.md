# Implementation Plan

The project is intentionally implemented in reviewed phases. Each phase must include complete code for that phase, tests, a git commit, and a review stop.

## Phase 1: Project setup

Commit: `feat: initialize project structure`

- Create backend, frontend, docs, docker, and CI structure.
- Configure Python 3.12 FastAPI backend with Pydantic V2, SQLAlchemy 2.0, Alembic, Structlog, pytest, ruff, black, and mypy.
- Configure React 19 + TypeScript + Vite frontend with Material UI, TanStack Query, Zustand, AG Grid, Lightweight Charts, Vitest, and React Testing Library.
- Add `.env.example`, `.gitignore`, Dockerfiles, docker compose, Nginx config, and GitHub Actions CI.
- Add baseline health endpoint and frontend application shell tests.

## Phase 2: Authentication ✅

Commit: `feat: implement shioaji authentication and connection management`

- Implemented Shioaji login service and SDK adapter.
- Activated CA certificate using environment-provided CA path and password.
- Added startup login hook, session manager, connection monitor, account endpoint, and dependency health checks.
- Added reconnect policy with immediate, 5-second, 15-second, and 30-second retry windows.
- Added unit and integration tests using Shioaji test doubles with 90%+ backend coverage.

## Phase 3: Historical data

Commit: `feat: implement historical market data module`

- Use Shioaji `api.kbars()` for 1-minute data.
- Aggregate `5m`, `15m`, `60m`, and `1d` candles.
- Cache all supported intervals in Redis using required keys.
- Implement `GET /market/history`.
- Add deterministic aggregation and cache integration tests.

## Phase 4: Realtime market data

Commit: `feat: implement websocket market streaming`

- Subscribe to Shioaji tick and bid/ask streams.
- Implement `/ws/market/{symbol}`.
- Support multi-symbol subscription fan-out.
- Add reconnect handling and latency-focused message dispatch.
- Add WebSocket integration tests.

## Phase 5: TradingView charts

Commit: `feat: implement chart workspace and realtime updates`

- Implement multi-chart layouts: single, two horizontal, two vertical, four grid.
- Use localStorage persistence.
- Add TradingView Lightweight Charts candlesticks, volume, price line, markers, separators, and streaming updates.
- Add frontend tests for workspace state and chart data adapters.

## Phase 6: DOM Ladder

Commit: `feat: implement tradovate style dom ladder`

- Build price ladder with bid/ask depth, current price, working orders, and positions.
- Add click-to-trade, modify, cancel, and auto-center behavior.
- Add unit tests for ladder price-level projection.

## Phase 7: Order engine

Commit: `feat: implement order execution and management`

- Implement order REST API.
- Persist orders and executions.
- Map internal orders to Shioaji order operations.
- Add OCO bracket behavior.
- Add order lifecycle tests.

## Phase 8: Chart trading

Commit: `feat: implement chart trading and drag order management`

- Add chart click order popup.
- Add optional one-click trading with risk warning and local preference storage.
- Add draggable entry, take-profit, stop-loss, and position average lines.
- Confirm drag modifications and call `PATCH /orders/{id}`.

## Phase 9: ATM strategies and risk management

Commit: `feat: implement atm strategies and risk controls`

- Implement ATM templates API with default templates.
- Auto-attach brackets during entry.
- Implement maximum position size, maximum order quantity, maximum daily loss, and maximum daily trade count checks.
- Log all risk violations.

## Phase 10: Testing and deployment

Commit: `docs: complete tests docker deployment and documentation`

- Complete end-to-end integration coverage.
- Harden Docker and Nginx deployment.
- Finalize README with examples and operational guide.
- Add CI/CD deployment hooks and release checklist.
