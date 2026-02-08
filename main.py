import asyncio
import base64
import io
import os
import random
import socket
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path

import bcrypt
import qrcode
from fastapi import Cookie, FastAPI, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import (
    COURTESY_COOLDOWN_SECONDS,
    GACHA_CHARACTERS,
    GACHA_MINUTES_PER_PULL,
    GACHA_RARITY_WEIGHTS,
    GAME_NAMES,
    SERVER_PORT,
    TURN_TIMEOUT_SECONDS,
)
from database import (
    create_session,
    create_user,
    delete_session,
    get_all_usernames,
    get_user,
    init_db,
    load_state,
    save_courtesy_cooldowns,
    save_gacha_state,
    save_game_state,
    save_global_state,
)


def is_admin(player: str) -> bool:
    """Check if the player is the admin user."""
    return player.lower().strip() == "admin"


def generate_qr_code_data_url(url: str) -> str:
    """Generate a QR code and return as a base64 data URL."""
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


# Generate QR code once at startup
# QR_URL can be set via BASE_URL env var (e.g. "http://192.168.1.100:5050")
# Falls back to hostname-based URL for local development
QR_URL = os.environ.get("BASE_URL", f"http://{socket.gethostname()}:{SERVER_PORT}")
QR_CODE_DATA_URL = generate_qr_code_data_url(QR_URL)


@dataclass
class Game:
    name: str
    queue: list[str] = field(default_factory=list)
    now_playing: str | None = None
    turn_started_at: float | None = None
    turn_accepted: bool = False
    play_started_at: float | None = None  # When player accepted their turn
    skip_counts: dict[str, int] = field(default_factory=dict)  # Skips per player
    total_play_time: dict[str, float] = field(default_factory=dict)  # Cumulative secs
    session_counts: dict[str, int] = field(default_factory=dict)  # Times played
    play_time_offset: dict[str, float] = field(default_factory=dict)


# In-memory state
games: dict[str, Game] = {name: Game(name=name) for name in GAME_NAMES}
queue_paused: bool = False
pause_started_at: float | None = None  # When the queue was paused
lock = asyncio.Lock()

# Courtesy cooldowns: (player, game_name) -> cooldown_ends_at timestamp
courtesy_cooldowns: dict[tuple[str, str], float] = {}

# Gacha state (global, not per-game)
gacha_collections: dict[str, dict[str, int]] = {}  # player -> {char: count}
gacha_last_pull: dict[str, list[dict]] = {}  # player -> list of pull results
gacha_pulls_given: dict[str, int] = {}  # player -> total pulls awarded

# Session store: token -> username (loaded from DB on startup)
sessions: dict[str, str] = {}

# SSE: connected clients
sse_clients: set[asyncio.Queue] = set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global games, queue_paused, pause_started_at
    global courtesy_cooldowns, gacha_collections, gacha_pulls_given, sessions

    await init_db()
    state = await load_state()

    # Populate game state from DB
    for name in GAME_NAMES:
        if name in state["games_data"]:
            gd = state["games_data"][name]
            game = games[name]
            game.queue = gd["queue"]
            game.now_playing = gd["now_playing"]
            game.turn_started_at = gd["turn_started_at"]
            game.turn_accepted = gd["turn_accepted"]
            game.play_started_at = gd["play_started_at"]

    # Populate per-player stats
    for (username, game_name), stats in state["player_stats"].items():
        if game_name in games:
            game = games[game_name]
            if stats["skip_count"]:
                game.skip_counts[username] = stats["skip_count"]
            if stats["total_play_time"]:
                game.total_play_time[username] = stats["total_play_time"]
            if stats["session_count"]:
                game.session_counts[username] = stats["session_count"]
            if stats.get("play_time_offset"):
                game.play_time_offset[username] = stats["play_time_offset"]

    gacha_collections = state["gacha_collections"]
    gacha_pulls_given = state["gacha_pulls_given"]
    courtesy_cooldowns = state["courtesy_cooldowns"]
    sessions = state["sessions"]
    queue_paused = state["queue_paused"]
    pause_started_at = state["pause_started_at"]

    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=Path(__file__).parent), name="static")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


def get_player_from_session(session_token: str) -> str:
    """Look up username from session token. Returns empty string if invalid."""
    if not session_token:
        return ""
    return sessions.get(session_token, "")


def subscribe() -> asyncio.Queue:
    q: asyncio.Queue = asyncio.Queue()
    sse_clients.add(q)
    return q


def unsubscribe(q: asyncio.Queue) -> None:
    sse_clients.discard(q)


async def broadcast() -> None:
    for q in sse_clients:
        await q.put("refresh")


def get_cooldown_remaining(player: str, game_name: str) -> float:
    """Get remaining cooldown seconds for a player on a game."""
    key = (player, game_name)
    if key not in courtesy_cooldowns:
        return 0
    remaining = courtesy_cooldowns[key] - time.time()
    if remaining <= 0:
        del courtesy_cooldowns[key]
        return 0
    return remaining


def get_player_playing_game(player: str) -> str | None:
    """Return the game name the player is currently playing, or None."""
    for game in games.values():
        if game.now_playing == player:
            return game.name
    return None


def gacha_pull(player: str) -> tuple[dict, bool]:
    """Perform a gacha pull for a player. Returns (character_info, is_duplicate)."""
    # Group characters by rarity
    by_rarity: dict[str, list[dict]] = {}
    for char in GACHA_CHARACTERS:
        by_rarity.setdefault(char["rarity"], []).append(char)

    # Pick rarity first using weights
    rarities = list(GACHA_RARITY_WEIGHTS.keys())
    weights = [GACHA_RARITY_WEIGHTS[r] for r in rarities]
    chosen_rarity = random.choices(rarities, weights=weights, k=1)[0]

    # Pick a random character from that rarity
    character = random.choice(by_rarity[chosen_rarity])

    # Update collection
    if player not in gacha_collections:
        gacha_collections[player] = {}
    collection = gacha_collections[player]
    is_duplicate = character["name"] in collection
    collection[character["name"]] = collection.get(character["name"], 0) + 1

    return character, is_duplicate


def advance_game(game: Game) -> None:
    """Advance to next available player. Skip players who are playing other games."""
    if queue_paused:
        return

    game.now_playing = None
    game.turn_started_at = None
    game.turn_accepted = False
    game.play_started_at = None
    skipped: list[str] = []

    while game.queue:
        candidate = game.queue.pop(0)
        if get_player_playing_game(candidate) is None:
            game.now_playing = candidate
            game.turn_started_at = time.time()
            game.turn_accepted = False
            game.play_started_at = None
            break
        else:
            skipped.append(candidate)

    # Put skipped players at the front of the queue (like a normal skip)
    # They go behind the new now_playing but ahead of others
    for player in reversed(skipped):
        game.queue.insert(0, player)


def has_available_player_in_queue(game: Game) -> bool:
    """Check if there's anyone in the queue who isn't playing another game."""
    for player in game.queue:
        if get_player_playing_game(player) is None:
            return True
    return False


def skip_current_player(game: Game) -> None:
    """Skip current player - they go behind next available person or leave if none."""
    if game.now_playing is None:
        return

    skipped_player = game.now_playing

    # Check if there's anyone available in queue (not playing another game)
    if has_available_player_in_queue(game):
        # Increment skip count for this player
        game.skip_counts[skipped_player] = game.skip_counts.get(skipped_player, 0) + 1
        # There's someone available waiting - skip behind them
        advance_game(game)
        game.queue.insert(0, skipped_player)
    else:
        # No one available waiting - player leaves entirely, clear their skip count
        game.skip_counts.pop(skipped_player, None)
        advance_game(game)

    # Check other games - maybe someone waiting can now play
    for other_game in games.values():
        if other_game.name != game.name and other_game.now_playing is None:
            advance_game(other_game)


def check_expired_turns() -> None:
    """Check all games for expired turns and auto-skip them."""
    if queue_paused:
        return

    now = time.time()
    for game in games.values():
        if (
            game.now_playing is not None
            and not game.turn_accepted
            and game.turn_started_at is not None
            and (now - game.turn_started_at) >= TURN_TIMEOUT_SECONDS
        ):
            skip_current_player(game)


@app.get("/events")
async def sse_events():
    q = subscribe()

    async def event_stream():
        try:
            while True:
                msg = await q.get()
                yield f"data: {msg}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            unsubscribe(q)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/")
async def index(request: Request, session: str = Cookie(default="")):
    player = get_player_from_session(session)

    async with lock:
        # Check for expired turns before rendering
        check_expired_turns()

        player_games = {}
        pending_turns = {}  # Games where it's the player's turn but not yet accepted
        cooldowns = {}  # Games where the player has a courtesy cooldown
        now = time.time()

        if player:
            for game in games.values():
                if game.now_playing == player:
                    if game.turn_accepted:
                        player_games[game.name] = "playing"
                    else:
                        # Turn not yet accepted - calculate remaining time
                        elapsed = now - (game.turn_started_at or now)
                        remaining = max(0, TURN_TIMEOUT_SECONDS - elapsed)
                        pending_turns[game.name] = remaining
                        player_games[game.name] = "pending"
                elif player in game.queue:
                    player_games[game.name] = game.queue.index(player) + 1
                else:
                    # Check for courtesy cooldown
                    cooldown = get_cooldown_remaining(player, game.name)
                    if cooldown > 0:
                        cooldowns[game.name] = cooldown
                    player_games[game.name] = None

        # Gacha data for template
        player_gacha_pulls = gacha_last_pull.get(player) if player else None
        player_collection = gacha_collections.get(player, {}) if player else {}

        # Calculate time progress toward next pull
        gacha_next_pull_secs = 0
        if player:
            total_time = sum(g.total_play_time.get(player, 0) for g in games.values())
            pull_interval = GACHA_MINUTES_PER_PULL * 60
            time_into_current = total_time % pull_interval
            gacha_next_pull_secs = int(pull_interval - time_into_current)

        # Get error from query params
        error = request.query_params.get("error", "")

        # Load all usernames for admin dropdowns
        all_users = await get_all_usernames() if is_admin(player) else []

        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "player": player,
                "games": games,
                "player_games": player_games,
                "pending_turns": pending_turns,
                "cooldowns": cooldowns,
                "timeout_seconds": TURN_TIMEOUT_SECONDS,
                "qr_code": QR_CODE_DATA_URL,
                "qr_url": QR_URL,
                "paused": queue_paused,
                "now": pause_started_at if queue_paused and pause_started_at else now,
                "is_host": is_admin(player),
                "all_users": all_users,
                "gacha_pulls": player_gacha_pulls,
                "gacha_collection": player_collection,
                "gacha_characters": GACHA_CHARACTERS,
                "gacha_next_pull_secs": gacha_next_pull_secs,
                "error": error,
            },
        )


@app.post("/register")
async def register(
    username: str = Form(default=""),
    password: str = Form(default=""),
):
    username = username.strip()
    if not username or not password:
        return RedirectResponse(
            url="/?error=username_and_password_required", status_code=303
        )

    # Hash password
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    # Try to create user in DB
    success = await create_user(username, password_hash)
    if not success:
        return RedirectResponse(url="/?error=username_taken", status_code=303)

    # Create session
    token = await create_session(username)
    sessions[token] = username

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="session", value=token, max_age=86400 * 30, httponly=True)
    await broadcast()
    return response


@app.post("/login")
async def login(
    username: str = Form(default=""),
    password: str = Form(default=""),
):
    username = username.strip()
    if not username or not password:
        return RedirectResponse(
            url="/?error=username_and_password_required", status_code=303
        )

    user = await get_user(username)
    if not user:
        return RedirectResponse(url="/?error=wrong_credentials", status_code=303)

    if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return RedirectResponse(url="/?error=wrong_credentials", status_code=303)

    # Create session
    token = await create_session(username)
    sessions[token] = username

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="session", value=token, max_age=86400 * 30, httponly=True)
    await broadcast()
    return response


@app.post("/join/{game_name}")
async def join_game(game_name: str, session: str = Cookie(default="")):
    player = get_player_from_session(session)
    if not player or game_name not in games:
        return RedirectResponse(url="/", status_code=303)

    async with lock:
        # Check courtesy cooldown
        if get_cooldown_remaining(player, game_name) > 0:
            return RedirectResponse(url="/", status_code=303)

        game = games[game_name]
        if player not in game.queue and game.now_playing != player:
            game.queue.append(player)
            # If no one is playing, advance to start the game
            if game.now_playing is None:
                advance_game(game)

        await save_game_state(games)

    await broadcast()
    return RedirectResponse(url="/", status_code=303)


@app.post("/leave/{game_name}")
async def leave_game(game_name: str, session: str = Cookie(default="")):
    player = get_player_from_session(session)
    if not player or game_name not in games:
        return RedirectResponse(url="/", status_code=303)

    async with lock:
        game = games[game_name]
        if player in game.queue:
            game.queue.remove(player)
        elif game.now_playing == player and not game.turn_accepted:
            # Player is pending - advance to next player
            advance_game(game)
            # Check other games
            for other_game in games.values():
                if other_game.name != game_name and other_game.now_playing is None:
                    advance_game(other_game)

        await save_game_state(games)

    await broadcast()
    return RedirectResponse(url="/", status_code=303)


@app.post("/swap")
async def swap_places(
    game_name: str = Form(...),
    target_player: str = Form(...),
    session: str = Cookie(default=""),
):
    """Swap places with someone below you in the queue."""
    player = get_player_from_session(session)
    if not player or game_name not in games:
        return RedirectResponse(url="/", status_code=303)

    async with lock:
        game = games[game_name]
        if player in game.queue and target_player in game.queue:
            my_idx = game.queue.index(player)
            target_idx = game.queue.index(target_player)
            # Can only swap with someone below (higher index)
            if target_idx > my_idx:
                game.queue[my_idx], game.queue[target_idx] = (
                    game.queue[target_idx],
                    game.queue[my_idx],
                )

        await save_game_state(games)

    await broadcast()
    return RedirectResponse(url="/", status_code=303)


@app.post("/accept/{game_name}")
async def accept_turn(game_name: str, session: str = Cookie(default="")):
    player = get_player_from_session(session)
    if not player or game_name not in games:
        return RedirectResponse(url="/", status_code=303)

    async with lock:
        game = games[game_name]
        if (
            game.now_playing == player
            and not game.turn_accepted
            and game.turn_started_at is not None
        ):
            elapsed = time.time() - game.turn_started_at
            if elapsed < TURN_TIMEOUT_SECONDS:
                game.turn_accepted = True
                game.play_started_at = time.time()
                # Increment session count
                game.session_counts[player] = game.session_counts.get(player, 0) + 1
                # Clear skip count when they start playing
                game.skip_counts.pop(player, None)

        await save_game_state(games)

    await broadcast()
    return RedirectResponse(url="/", status_code=303)


@app.post("/skip/{game_name}")
async def skip_turn(game_name: str, session: str = Cookie(default="")):
    """Skip your turn - go behind next person, or leave if queue empty."""
    player = get_player_from_session(session)
    if not player or game_name not in games:
        return RedirectResponse(url="/", status_code=303)

    async with lock:
        game = games[game_name]
        if game.now_playing == player and not game.turn_accepted:
            skip_current_player(game)

        await save_game_state(games)

    await broadcast()
    return RedirectResponse(url="/", status_code=303)


@app.post("/done/{game_name}")
async def done_playing(game_name: str, session: str = Cookie(default="")):
    player = get_player_from_session(session)
    if not player or game_name not in games:
        return RedirectResponse(url="/", status_code=303)

    async with lock:
        game = games[game_name]
        if game.now_playing == player:
            # Add play time to total if they were playing
            if game.play_started_at is not None:
                play_duration = time.time() - game.play_started_at
                game.total_play_time[player] = (
                    game.total_play_time.get(player, 0) + play_duration
                )
            # Gacha: award pulls based on total play time
            total_time = sum(g.total_play_time.get(player, 0) for g in games.values())
            entitled = int(total_time // (GACHA_MINUTES_PER_PULL * 60))
            given = gacha_pulls_given.get(player, 0)
            new_pulls = entitled - given
            if new_pulls > 0:
                results = []
                for _ in range(new_pulls):
                    char, is_dupe = gacha_pull(player)
                    count = gacha_collections[player][char["name"]]
                    results.append(
                        {
                            **char,
                            "is_duplicate": is_dupe,
                            "count": count,
                        }
                    )
                gacha_last_pull[player] = results
                gacha_pulls_given[player] = entitled
            # Set courtesy cooldown if queue is empty
            if not game.queue:
                courtesy_cooldowns[(player, game_name)] = (
                    time.time() + COURTESY_COOLDOWN_SECONDS
                )
            advance_game(game)
            # Check other games - maybe someone waiting can now play
            for other_game in games.values():
                if other_game.name != game_name and other_game.now_playing is None:
                    advance_game(other_game)

            await save_game_state(games)
            await save_gacha_state(gacha_collections, gacha_pulls_given)
            await save_courtesy_cooldowns(courtesy_cooldowns)

    await broadcast()
    return RedirectResponse(url="/", status_code=303)


@app.post("/gacha-dismiss")
async def gacha_dismiss(session: str = Cookie(default="")):
    player = get_player_from_session(session)
    if player and player in gacha_last_pull:
        gacha_last_pull.pop(player, None)
    return RedirectResponse(url="/", status_code=303)


@app.post("/logout")
async def logout(session: str = Cookie(default="")):
    player = get_player_from_session(session)

    async with lock:
        # Remove player from all games
        if player:
            for game in games.values():
                if player in game.queue:
                    game.queue.remove(player)
                if game.now_playing == player:
                    advance_game(game)
            await save_game_state(games)

    # Remove session from memory and DB
    if session and session in sessions:
        del sessions[session]
        await delete_session(session)

    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="session")
    await broadcast()
    return response


@app.post("/toggle-pause")
async def toggle_pause(session: str = Cookie(default="")):
    global queue_paused, pause_started_at
    player = get_player_from_session(session)
    if not is_admin(player):
        return RedirectResponse(url="/", status_code=303)
    async with lock:
        queue_paused = not queue_paused
        if queue_paused:
            pause_started_at = time.time()
        else:
            # Adjust play_started_at for all playing games to account for pause duration
            if pause_started_at is not None:
                pause_duration = time.time() - pause_started_at
                for game in games.values():
                    if game.play_started_at is not None:
                        game.play_started_at += pause_duration
            pause_started_at = None

        await save_game_state(games)
        await save_global_state(queue_paused, pause_started_at)

    await broadcast()
    return RedirectResponse(url="/", status_code=303)


@app.post("/admin/kick")
async def admin_kick_player(
    game_name: str = Form(...), session: str = Cookie(default="")
):
    """Admin only: Kick the current player from a game."""
    player = get_player_from_session(session)
    if not is_admin(player):
        return RedirectResponse(url="/", status_code=303)

    if game_name not in games:
        return RedirectResponse(url="/", status_code=303)

    async with lock:
        game = games[game_name]
        if game.now_playing:
            # Add play time if they were playing
            if game.play_started_at is not None:
                play_duration = time.time() - game.play_started_at
                game.total_play_time[game.now_playing] = (
                    game.total_play_time.get(game.now_playing, 0) + play_duration
                )
            advance_game(game)
            # Check other games
            for other_game in games.values():
                if other_game.name != game_name and other_game.now_playing is None:
                    advance_game(other_game)

        await save_game_state(games)

    await broadcast()
    return RedirectResponse(url="/", status_code=303)


@app.post("/admin/remove")
async def admin_remove_from_queue(
    game_name: str = Form(...),
    player_name: str = Form(...),
    session: str = Cookie(default=""),
):
    """Admin only: Remove a player from a game's queue."""
    player = get_player_from_session(session)
    if not is_admin(player):
        return RedirectResponse(url="/", status_code=303)

    if game_name not in games:
        return RedirectResponse(url="/", status_code=303)

    async with lock:
        game = games[game_name]
        if player_name in game.queue:
            game.queue.remove(player_name)
            # Clear their skip count
            game.skip_counts.pop(player_name, None)

        await save_game_state(games)

    await broadcast()
    return RedirectResponse(url="/", status_code=303)


@app.post("/admin/bump-up")
async def admin_bump_up(
    game_name: str = Form(...),
    player_name: str = Form(...),
    session: str = Cookie(default=""),
):
    """Admin only: Move a player up in the queue (closer to front)."""
    player = get_player_from_session(session)
    if not is_admin(player):
        return RedirectResponse(url="/", status_code=303)

    if game_name not in games:
        return RedirectResponse(url="/", status_code=303)

    async with lock:
        game = games[game_name]
        if player_name in game.queue:
            idx = game.queue.index(player_name)
            if idx > 0:  # Can't bump up if already first
                game.queue[idx], game.queue[idx - 1] = (
                    game.queue[idx - 1],
                    game.queue[idx],
                )

        await save_game_state(games)

    await broadcast()
    return RedirectResponse(url="/", status_code=303)


@app.post("/admin/bump-down")
async def admin_bump_down(
    game_name: str = Form(...),
    player_name: str = Form(...),
    session: str = Cookie(default=""),
):
    """Admin only: Move a player down in the queue (closer to back)."""
    player = get_player_from_session(session)
    if not is_admin(player):
        return RedirectResponse(url="/", status_code=303)

    if game_name not in games:
        return RedirectResponse(url="/", status_code=303)

    async with lock:
        game = games[game_name]
        if player_name in game.queue:
            idx = game.queue.index(player_name)
            if idx < len(game.queue) - 1:  # Can't bump down if already last
                game.queue[idx], game.queue[idx + 1] = (
                    game.queue[idx + 1],
                    game.queue[idx],
                )

        await save_game_state(games)

    await broadcast()
    return RedirectResponse(url="/", status_code=303)


@app.post("/admin/set-playing")
async def admin_set_playing(
    game_name: str = Form(...),
    player_name: str = Form(...),
    session: str = Cookie(default=""),
):
    """Admin only: Set a user as now_playing on a game."""
    player = get_player_from_session(session)
    if not is_admin(player):
        return RedirectResponse(url="/", status_code=303)

    if game_name not in games:
        return RedirectResponse(url="/", status_code=303)

    async with lock:
        game = games[game_name]
        # End current player's turn if someone is playing
        if game.now_playing and game.play_started_at is not None:
            play_duration = time.time() - game.play_started_at
            game.total_play_time[game.now_playing] = (
                game.total_play_time.get(game.now_playing, 0) + play_duration
            )
        # Remove player_name from queue if present
        if player_name in game.queue:
            game.queue.remove(player_name)
        # Set as now_playing
        game.now_playing = player_name
        game.turn_started_at = time.time()
        game.turn_accepted = True
        game.play_started_at = time.time()

        await save_game_state(games)

    await broadcast()
    return RedirectResponse(url="/", status_code=303)


@app.post("/admin/add-to-queue")
async def admin_add_to_queue(
    game_name: str = Form(...),
    player_name: str = Form(...),
    session: str = Cookie(default=""),
):
    """Admin only: Add a user to the end of a game's queue."""
    player = get_player_from_session(session)
    if not is_admin(player):
        return RedirectResponse(url="/", status_code=303)

    if game_name not in games:
        return RedirectResponse(url="/", status_code=303)

    async with lock:
        game = games[game_name]
        # Skip if already in queue or already now_playing
        if player_name not in game.queue and game.now_playing != player_name:
            game.queue.append(player_name)
            # If no one is playing, advance to start
            if game.now_playing is None:
                advance_game(game)

        await save_game_state(games)

    await broadcast()
    return RedirectResponse(url="/", status_code=303)


@app.post("/admin/reset-stats")
async def admin_reset_stats(session: str = Cookie(default="")):
    """Admin only: Reset displayed session counts and play times (gacha unaffected)."""
    player = get_player_from_session(session)
    if not is_admin(player):
        return RedirectResponse(url="/", status_code=303)

    async with lock:
        for game in games.values():
            for p in list(game.total_play_time.keys()):
                game.play_time_offset[p] = game.total_play_time[p]
            game.session_counts.clear()

        await save_game_state(games)

    await broadcast()
    return RedirectResponse(url="/", status_code=303)


@app.post("/idle/start")
async def idle_start(session: str = Cookie(default="")):
    player = get_player_from_session(session)
    if not player:
        return JSONResponse({"error": "not_logged_in"}, status_code=401)
    return JSONResponse({"status": "started"})


@app.post("/idle/complete")
async def idle_complete(session: str = Cookie(default="")):
    player = get_player_from_session(session)
    if not player:
        return JSONResponse({"error": "not_logged_in"}, status_code=401)
    async with lock:
        char, is_dupe = gacha_pull(player)
        count = gacha_collections[player][char["name"]]
        gacha_last_pull[player] = [
            {**char, "is_duplicate": is_dupe, "count": count}
        ]
        await save_gacha_state(gacha_collections, gacha_pulls_given)
    await broadcast()
    return JSONResponse({"status": "completed"})


if __name__ == "__main__":
    import uvicorn

    print(f"Starting server on {QR_URL}")
    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT)
