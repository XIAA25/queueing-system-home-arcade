import asyncio
import base64
import io
import random
import socket
import time
from dataclasses import dataclass, field
from pathlib import Path

import qrcode
from fastapi import Cookie, FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import (
    COURTESY_COOLDOWN_SECONDS,
    GAME_NAMES,
    SERVER_PORT,
    TURN_TIMEOUT_SECONDS,
)

app = FastAPI()
app.mount("/static", StaticFiles(directory=Path(__file__).parent), name="static")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


def get_local_ip() -> str:
    """Get the local IP address for LAN access."""
    try:
        # Connect to an external address to determine the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        # Fallback: try to get hostname-based IP
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"


def is_host(request_client_host: str | None) -> bool:
    """Check if the request is coming from the host machine."""
    if not request_client_host:
        return False
    # Check common localhost addresses
    if request_client_host in {"127.0.0.1", "localhost", "::1"}:
        return True
    # Check if it matches the server's local IP
    if request_client_host == LOCAL_IP:
        return True
    # Check IPv6-mapped IPv4 addresses (e.g., ::ffff:127.0.0.1)
    if request_client_host.startswith("::ffff:"):
        ipv4_part = request_client_host[7:]  # Remove "::ffff:" prefix
        if ipv4_part in {"127.0.0.1", LOCAL_IP}:
            return True
    return False


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
LOCAL_IP = get_local_ip()
HOSTNAME = socket.gethostname()
QR_URL = f"http://{HOSTNAME}:{SERVER_PORT}"
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


# In-memory state
games: dict[str, Game] = {name: Game(name=name) for name in GAME_NAMES}
queue_paused: bool = False
pause_started_at: float | None = None  # When the queue was paused
lock = asyncio.Lock()

# Courtesy cooldowns: (player, game_name) -> cooldown_ends_at timestamp
courtesy_cooldowns: dict[tuple[str, str], float] = {}


def get_cooldown_remaining(player: str, game_name: str) -> float:
    """Get remaining cooldown seconds for a player on a game. Returns 0 if no cooldown."""
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


def skip_current_player(game: Game) -> None:
    """Skip current player - they go behind next person or leave if queue empty."""
    if game.now_playing is None:
        return

    skipped_player = game.now_playing

    if game.queue:
        # Increment skip count for this player
        game.skip_counts[skipped_player] = game.skip_counts.get(skipped_player, 0) + 1
        # There's someone waiting - skip behind them
        advance_game(game)
        game.queue.insert(0, skipped_player)
    else:
        # No one waiting - player leaves entirely, clear their skip count
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


@app.get("/")
async def index(request: Request, player: str = Cookie(default="")):
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

        client_host = None
        if request.client:
            client_host = request.client.host
        # Also check X-Forwarded-For header in case of proxy
        if not client_host:
            client_host = request.headers.get("X-Forwarded-For", "unknown")

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
                "is_host": is_host(client_host),
            },
        )


@app.post("/register")
async def register(name: str = Form(default="")):
    display_name = name.strip() or f"Guest-{random.randint(1000, 9999)}"
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="player", value=display_name, max_age=86400)
    return response


@app.post("/join/{game_name}")
async def join_game(game_name: str, player: str = Cookie(default="")):
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

    return RedirectResponse(url="/", status_code=303)


@app.post("/leave/{game_name}")
async def leave_game(game_name: str, player: str = Cookie(default="")):
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

    return RedirectResponse(url="/", status_code=303)


@app.post("/swap")
async def swap_places(
    game_name: str = Form(...),
    target_player: str = Form(...),
    player: str = Cookie(default=""),
):
    """Swap places with someone below you in the queue."""
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

    return RedirectResponse(url="/", status_code=303)


@app.post("/accept/{game_name}")
async def accept_turn(game_name: str, player: str = Cookie(default="")):
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

    return RedirectResponse(url="/", status_code=303)


@app.post("/skip/{game_name}")
async def skip_turn(game_name: str, player: str = Cookie(default="")):
    """Skip your turn - go behind next person, or leave if queue empty."""
    if not player or game_name not in games:
        return RedirectResponse(url="/", status_code=303)

    async with lock:
        game = games[game_name]
        if game.now_playing == player and not game.turn_accepted:
            skip_current_player(game)

    return RedirectResponse(url="/", status_code=303)


@app.post("/done/{game_name}")
async def done_playing(game_name: str, player: str = Cookie(default="")):
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

    return RedirectResponse(url="/", status_code=303)


@app.post("/logout")
async def logout(player: str = Cookie(default="")):
    async with lock:
        # Remove player from all games
        for game in games.values():
            if player in game.queue:
                game.queue.remove(player)
            if game.now_playing == player:
                advance_game(game)

    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="player")
    return response


@app.post("/toggle-pause")
async def toggle_pause(request: Request):
    global queue_paused, pause_started_at
    client_host = request.client.host if request.client else None
    if not is_host(client_host):
        # Only host can toggle pause
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
    return RedirectResponse(url="/", status_code=303)


@app.post("/admin/kick")
async def admin_kick_player(request: Request, game_name: str = Form(...)):
    """Host only: Kick the current player from a game."""
    client_host = request.client.host if request.client else None
    if not is_host(client_host):
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

    return RedirectResponse(url="/", status_code=303)


@app.post("/admin/remove")
async def admin_remove_from_queue(
    request: Request, game_name: str = Form(...), player_name: str = Form(...)
):
    """Host only: Remove a player from a game's queue."""
    client_host = request.client.host if request.client else None
    if not is_host(client_host):
        return RedirectResponse(url="/", status_code=303)

    if game_name not in games:
        return RedirectResponse(url="/", status_code=303)

    async with lock:
        game = games[game_name]
        if player_name in game.queue:
            game.queue.remove(player_name)
            # Clear their skip count
            game.skip_counts.pop(player_name, None)

    return RedirectResponse(url="/", status_code=303)


@app.post("/admin/bump-up")
async def admin_bump_up(
    request: Request, game_name: str = Form(...), player_name: str = Form(...)
):
    """Host only: Move a player up in the queue (closer to front)."""
    client_host = request.client.host if request.client else None
    if not is_host(client_host):
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

    return RedirectResponse(url="/", status_code=303)


@app.post("/admin/bump-down")
async def admin_bump_down(
    request: Request, game_name: str = Form(...), player_name: str = Form(...)
):
    """Host only: Move a player down in the queue (closer to back)."""
    client_host = request.client.host if request.client else None
    if not is_host(client_host):
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

    return RedirectResponse(url="/", status_code=303)


if __name__ == "__main__":
    import uvicorn

    print(f"Starting server on http://{HOSTNAME}:{SERVER_PORT}")
    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT)
