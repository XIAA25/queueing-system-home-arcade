# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A queue management system for a home arcade (XIAA-Play). Players join game queues from their phones, get notified when it's their turn, and manage play sessions. Built with Python 3.10+ and FastAPI.

## Development Commands

```bash
# Install dependencies
poetry install

# Run the application (binds to 0.0.0.0:5050 for LAN access)
poetry run python main.py

# Run with auto-reload during development
poetry run uvicorn main:app --host 0.0.0.0 --port 5050 --reload

# Run all tests
poetry run pytest

# Run a specific test
poetry run pytest tests/test_app.py::test_join_game -v

# Lint and format
poetry run ruff check .
poetry run ruff check . --fix
poetry run ruff format .
```

## Docker Deployment

```bash
# Build and start the container
docker compose up --build

# Run in background
docker compose up -d --build

# Stop
docker compose down

# View logs
docker compose logs -f

# Data is persisted in a Docker volume (data:/app/data)
# To fully reset, remove the volume:
docker compose down -v
```

Set `HOST_IPS` env var in `docker-compose.yml` to add extra IPs recognized as host/admin (comma-separated).

## Architecture

Single-file FastAPI app (`main.py`) with all state in module-level globals, protected by a single `asyncio.Lock`. State is persisted to SQLite via `database.py` and loaded on startup.

### State Model

State lives in-memory during runtime and is persisted to SQLite (`data/queue.db`). Key globals in `main.py`:
- `games: dict[str, Game]` — One `Game` dataclass per configured game, each with its own queue (list), now_playing slot, turn/play timestamps, skip counts, and session stats.
- `queue_paused` / `pause_started_at` — Global pause state (host-only control). When paused, `advance_game()` and `check_expired_turns()` are no-ops.
- `courtesy_cooldowns` — Per-(player, game) cooldowns preventing immediate re-queue after finishing with no one waiting.
- `gacha_*` globals — Gacha collection/pull state, awarded based on cumulative play time across all games.
- `sessions` — In-memory dict mapping session tokens to usernames (also stored in DB).
- `sse_clients` — Set of `asyncio.Queue` objects for Server-Sent Events; every state mutation calls `broadcast()` to push "refresh" to all connected browsers.

### Persistence (database.py)

SQLite database at `data/queue.db` (configurable via `DB_PATH` env var). Tables: `users`, `sessions`, `game_state`, `player_game_stats`, `gacha_collections`, `gacha_pulls_given`, `courtesy_cooldowns`, `global_state`. On startup, `lifespan()` calls `init_db()` then `load_state()` to populate all globals. After each mutation, the relevant `save_*()` function is called inside the lock.

### Authentication

Username + password login with bcrypt hashing. Session tokens (uuid4) stored in `session` cookie (httponly). The `get_player_from_session()` function resolves session cookies to usernames. Host detection remains IP-based for admin controls.

### Request Flow

All POST endpoints follow the same pattern: resolve session → validate params → acquire `lock` → mutate state → save to DB → `broadcast()` → return `RedirectResponse(303)`. The browser follows the redirect back to `GET /` which re-renders the full page with current state.

### Key Business Logic

- **Turn acceptance**: When a player reaches front of queue, they have `TURN_TIMEOUT_SECONDS` (default 60s) to accept. `check_expired_turns()` runs on every `GET /` to auto-skip expired turns.
- **Cross-game skipping**: `advance_game()` skips players currently playing another game (checked via `get_player_playing_game()`), placing them back at the front of the queue.
- **Skip behavior**: `skip_current_player()` puts skipped players behind the next *available* person. If no one available is waiting, the player leaves the queue entirely.
- **Host detection**: `is_host()` checks request IP against localhost/local IP/Docker host IP/HOST_IPS env var for admin endpoints (`/toggle-pause`, `/admin/*`).

### Real-time Updates

`GET /events` provides an SSE stream. The template uses `EventSource` to listen for "refresh" events and reloads the page.

### Configuration

`config.py` contains all configurable values: game names, timeout durations, server port, gacha character pool and rarity weights.

### Testing

Tests use `httpx.AsyncClient` with `ASGITransport` (no server needed). Autouse fixtures `setup_db` (temporary SQLite) and `reset_state` reset all state between tests. The `set_session()` helper sets up authenticated sessions for test users. Tests can also manipulate `main.games` directly for unit-style tests of `advance_game()`, `check_expired_turns()`, etc.
