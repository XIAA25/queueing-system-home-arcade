# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A queueing system for XIAA-Play built with Python 3.10+ and FastAPI.

## Development Commands

```bash
# Install dependencies
poetry install

# Run the application (localhost only)
poetry run uvicorn main:app --reload

# Run for LAN access (other devices on same Wi-Fi)
poetry run uvicorn main:app --host 0.0.0.0 --port 8080 --reload

# Or run directly
poetry run python main.py

# Run all tests
poetry run pytest

# Run a single test file
poetry run pytest tests/test_app.py

# Run a specific test
poetry run pytest tests/test_app.py::test_placeholder -v

# Lint code
poetry run ruff check .

# Lint and auto-fix
poetry run ruff check . --fix

# Format code
poetry run ruff format .
```

## Project Structure

```
main.py              # FastAPI app entry point
templates/
  index.html         # Jinja2 template for the queue UI
tests/
  test_app.py        # Test suite
```

## Technology Stack

- **FastAPI** - Async web framework
- **Jinja2** - Server-side HTML templating
- **uvicorn** - ASGI server
- **Poetry** - Dependency management

## Architecture

This is an async-first REST API application. Key patterns:

- **ASGI application** - Event-driven, async I/O via anyio/Starlette
- **Type-driven development** - Pydantic models for request/response validation
- **Auto-generated API docs** - FastAPI provides OpenAPI documentation at `/docs` and `/redoc`
- **In-memory state** - Queue state stored in memory with asyncio.Lock for thread safety
- **Server-side rendering** - Jinja2 templates, no JavaScript required

## LAN Access

To allow other devices on the same Wi-Fi to access the queue:

1. Run with `--host 0.0.0.0` to bind to all network interfaces
2. Find your local IP: `ipconfig` (Windows) or `ip addr` (Linux/Termux)
3. Other devices access via `http://<your-ip>:8080`
4. Windows may prompt to allow firewall access - click "Allow"
