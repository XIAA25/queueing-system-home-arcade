"""SQLite persistence layer for the queueing system."""

import json
import os
import time
import uuid
from pathlib import Path

import aiosqlite

_default_db = str(Path(__file__).parent / "data" / "queue.db")
DB_PATH = os.environ.get("DB_PATH", _default_db)

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    username TEXT NOT NULL REFERENCES users(username),
    created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS game_state (
    name TEXT PRIMARY KEY,
    queue TEXT NOT NULL DEFAULT '[]',
    now_playing TEXT,
    turn_started_at REAL,
    turn_accepted INTEGER NOT NULL DEFAULT 0,
    play_started_at REAL
);

CREATE TABLE IF NOT EXISTS player_game_stats (
    username TEXT NOT NULL,
    game_name TEXT NOT NULL,
    skip_count INTEGER NOT NULL DEFAULT 0,
    total_play_time REAL NOT NULL DEFAULT 0.0,
    session_count INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (username, game_name)
);

CREATE TABLE IF NOT EXISTS gacha_collections (
    username TEXT NOT NULL,
    character_name TEXT NOT NULL,
    count INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (username, character_name)
);

CREATE TABLE IF NOT EXISTS gacha_pulls_given (
    username TEXT NOT NULL PRIMARY KEY,
    total_pulls INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS courtesy_cooldowns (
    username TEXT NOT NULL,
    game_name TEXT NOT NULL,
    expires_at REAL NOT NULL,
    PRIMARY KEY (username, game_name)
);

CREATE TABLE IF NOT EXISTS global_state (
    key TEXT PRIMARY KEY,
    value TEXT
);
"""


async def init_db() -> None:
    """Create tables if they don't exist. Create data/ dir if needed."""
    db_dir = Path(DB_PATH).parent
    db_dir.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA)
        await db.commit()


async def load_state() -> dict:
    """Read all tables and return dicts to populate globals.

    Returns a dict with keys:
        games_data: dict of game state dicts
        player_stats: dict of per-player stats
        gacha_collections: dict[username, dict[char_name, count]]
        gacha_pulls_given: dict[username, total_pulls]
        courtesy_cooldowns: dict[(username, game_name), expires_at]
        sessions: dict[token, username]
        queue_paused: bool
        pause_started_at: float | None
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # Game state
        games_data = {}
        async with db.execute("SELECT * FROM game_state") as cur:
            async for row in cur:
                games_data[row["name"]] = {
                    "queue": json.loads(row["queue"]),
                    "now_playing": row["now_playing"],
                    "turn_started_at": row["turn_started_at"],
                    "turn_accepted": bool(row["turn_accepted"]),
                    "play_started_at": row["play_started_at"],
                }

        # Player stats
        player_stats = {}
        async with db.execute("SELECT * FROM player_game_stats") as cur:
            async for row in cur:
                player_stats[(row["username"], row["game_name"])] = {
                    "skip_count": row["skip_count"],
                    "total_play_time": row["total_play_time"],
                    "session_count": row["session_count"],
                }

        # Gacha collections
        gacha_collections: dict[str, dict[str, int]] = {}
        async with db.execute("SELECT * FROM gacha_collections") as cur:
            async for row in cur:
                gacha_collections.setdefault(row["username"], {})[
                    row["character_name"]
                ] = row["count"]

        # Gacha pulls given
        gacha_pulls_given = {}
        async with db.execute("SELECT * FROM gacha_pulls_given") as cur:
            async for row in cur:
                gacha_pulls_given[row["username"]] = row["total_pulls"]

        # Courtesy cooldowns (only non-expired)
        now = time.time()
        courtesy_cooldowns = {}
        async with db.execute(
            "SELECT * FROM courtesy_cooldowns WHERE expires_at > ?", (now,)
        ) as cur:
            async for row in cur:
                courtesy_cooldowns[(row["username"], row["game_name"])] = row[
                    "expires_at"
                ]

        # Sessions
        sessions = {}
        async with db.execute("SELECT token, username FROM sessions") as cur:
            async for row in cur:
                sessions[row["token"]] = row["username"]

        # Global state
        queue_paused = False
        pause_started_at = None
        async with db.execute("SELECT key, value FROM global_state") as cur:
            async for row in cur:
                if row["key"] == "queue_paused":
                    queue_paused = row["value"] == "1"
                elif row["key"] == "pause_started_at":
                    pause_started_at = float(row["value"]) if row["value"] else None

    return {
        "games_data": games_data,
        "player_stats": player_stats,
        "gacha_collections": gacha_collections,
        "gacha_pulls_given": gacha_pulls_given,
        "courtesy_cooldowns": courtesy_cooldowns,
        "sessions": sessions,
        "queue_paused": queue_paused,
        "pause_started_at": pause_started_at,
    }


async def save_game_state(games: dict) -> None:
    """Upsert game_state and player_game_stats rows from in-memory Game objects."""
    async with aiosqlite.connect(DB_PATH) as db:
        for name, game in games.items():
            await db.execute(
                """INSERT INTO game_state
                   (name, queue, now_playing,
                    turn_started_at, turn_accepted,
                    play_started_at)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT(name) DO UPDATE SET
                   queue=excluded.queue,
                   now_playing=excluded.now_playing,
                   turn_started_at=excluded.turn_started_at,
                   turn_accepted=excluded.turn_accepted,
                   play_started_at=excluded.play_started_at
                """,
                (
                    name,
                    json.dumps(game.queue),
                    game.now_playing,
                    game.turn_started_at,
                    int(game.turn_accepted),
                    game.play_started_at,
                ),
            )

            # Save per-player stats for this game
            all_players = (
                set(game.skip_counts.keys())
                | set(game.total_play_time.keys())
                | set(game.session_counts.keys())
            )
            for player in all_players:
                await db.execute(
                    """INSERT INTO player_game_stats
                       (username, game_name, skip_count,
                        total_play_time, session_count)
                       VALUES (?, ?, ?, ?, ?)
                       ON CONFLICT(username, game_name)
                       DO UPDATE SET
                       skip_count=excluded.skip_count,
                       total_play_time=excluded.total_play_time,
                       session_count=excluded.session_count
                    """,
                    (
                        player,
                        name,
                        game.skip_counts.get(player, 0),
                        game.total_play_time.get(player, 0.0),
                        game.session_counts.get(player, 0),
                    ),
                )

        await db.commit()


async def save_global_state(paused: bool, pause_started_at: float | None) -> None:
    """Upsert global_state rows."""
    async with aiosqlite.connect(DB_PATH) as db:
        upsert = (
            "INSERT INTO global_state (key, value) "
            "VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET "
            "value=excluded.value"
        )
        await db.execute(
            upsert,
            ("queue_paused", "1" if paused else "0"),
        )
        await db.execute(
            upsert,
            (
                "pause_started_at",
                str(pause_started_at) if pause_started_at else None,
            ),
        )
        await db.commit()


async def save_courtesy_cooldowns(
    cooldowns: dict[tuple[str, str], float],
) -> None:
    """Replace all cooldown rows."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM courtesy_cooldowns")
        for (username, game_name), expires_at in cooldowns.items():
            await db.execute(
                "INSERT INTO courtesy_cooldowns "
                "(username, game_name, expires_at) "
                "VALUES (?, ?, ?)",
                (username, game_name, expires_at),
            )
        await db.commit()


async def save_gacha_state(
    collections: dict[str, dict[str, int]],
    pulls_given: dict[str, int],
) -> None:
    """Upsert gacha collection and pulls_given rows."""
    async with aiosqlite.connect(DB_PATH) as db:
        for username, chars in collections.items():
            for char_name, count in chars.items():
                await db.execute(
                    "INSERT INTO gacha_collections "
                    "(username, character_name, count) "
                    "VALUES (?, ?, ?) "
                    "ON CONFLICT(username, character_name) "
                    "DO UPDATE SET count=excluded.count",
                    (username, char_name, count),
                )
        for username, total in pulls_given.items():
            await db.execute(
                "INSERT INTO gacha_pulls_given "
                "(username, total_pulls) "
                "VALUES (?, ?) "
                "ON CONFLICT(username) "
                "DO UPDATE SET total_pulls=excluded.total_pulls",
                (username, total),
            )
        await db.commit()


async def create_user(username: str, password_hash: str) -> bool:
    """Insert a new user. Returns True on success, False if username taken."""
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                "INSERT INTO users "
                "(username, password_hash, created_at) "
                "VALUES (?, ?, ?)",
                (username, password_hash, time.time()),
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False


async def get_user(username: str) -> dict | None:
    """Return user row as dict or None."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ) as cur:
            row = await cur.fetchone()
            if row:
                return {
                    "username": row["username"],
                    "password_hash": row["password_hash"],
                }
            return None


async def create_session(username: str) -> str:
    """Generate uuid4 token, insert session row, return token."""
    token = uuid.uuid4().hex
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO sessions (token, username, created_at) VALUES (?, ?, ?)",
            (token, username, time.time()),
        )
        await db.commit()
    return token


async def delete_session(token: str) -> None:
    """Delete a session by token."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM sessions WHERE token = ?", (token,))
        await db.commit()


async def delete_user_sessions(username: str) -> None:
    """Delete all sessions for a user."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM sessions WHERE username = ?", (username,))
        await db.commit()


async def get_all_usernames() -> list[str]:
    """Return all registered usernames, sorted alphabetically."""
    async with aiosqlite.connect(DB_PATH) as db, db.execute(
        "SELECT username FROM users ORDER BY username"
    ) as cur:
        return [row[0] async for row in cur]
