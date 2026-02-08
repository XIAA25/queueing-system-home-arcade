# Home Arcade Queue System (XIAA-Play)

A queue management system for a home arcade. Players join game queues from their phones, get notified when it's their turn, manage play sessions, collect gacha characters, and play a mini-game while they wait.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Features

- **Multi-game support** - Manage queues for multiple arcade games simultaneously
- **Mobile-friendly** - Works on any device with a web browser
- **QR code access** - Scan to join from your phone
- **Account system** - Username + password login with persistent sessions
- **Turn notifications** - Full-screen overlay with sound and vibration when it's your turn
- **Fair play**
  - 60-second timer to accept your turn (configurable)
  - Courtesy cooldown prevents immediate re-queuing when no one is waiting
  - Skip tracking shows who's been skipping turns
  - Cross-game skipping: players already playing another game are skipped (but keep their place)
- **Session stats** - Track play time and session counts per player
- **Admin controls** - Pause queue, kick players, reorder queue, set players as playing, reset stats
- **Gacha collection** - Earn character pulls through play time, with 8 rarity tiers from Common to Godslayer
- **Crystal Mine** - An idle mini-game where players mine crystals to earn bonus gacha pulls while waiting in queue
- **Collection viewer** - Browse owned characters, tap to view full art and lore descriptions
- **Real-time updates** - Server-Sent Events push instant updates to all connected browsers
- **Persistent state** - All data stored in SQLite, survives server restarts

## Installation

### Prerequisites

- **Python 3.10+**
- **Poetry** (Python package manager)

### Step 1: Install Python

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important:** Check the box that says **"Add Python to PATH"**
4. Click "Install Now"

Verify it works by opening a terminal and running:
```
python --version
```
You should see something like `Python 3.12.0`.

### Step 2: Install Poetry

```
pip install poetry
```

### Step 3: Get the project

**Option A: Download ZIP**
1. Click the green "Code" button on this page
2. Click "Download ZIP"
3. Extract to a folder (e.g., `C:\queueing-system`)

**Option B: Using Git**
```
git clone https://github.com/XIAA25/queueing-system-home-arcade.git
cd queueing-system-home-arcade
```

### Step 4: Install dependencies

Open a terminal in the project folder and run:
```
poetry install
```

### Step 5: Run the server

```
poetry run python main.py
```

You'll see:
```
Starting server on http://YOUR-PC-NAME:8080
```

### Step 6: Connect

- **On the host PC:** Open `http://localhost:8080`
- **On phones/other devices:**
  1. Make sure you're on the same Wi-Fi network
  2. Scan the QR code shown on the host's screen, OR
  3. Type the URL shown (e.g., `http://YOUR-PC-NAME:8080`)

**Windows Firewall:** The first time you run the server, Windows may ask to allow network access. Click "Allow" so other devices can connect.

## Docker Deployment

```bash
# Build and start
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

Set `HOST_IPS` env var in `docker-compose.yml` to add extra IPs recognized as admin (comma-separated).

## Configuration

Edit `config.py` to customize:

```python
# Games available in your arcade
GAME_NAMES = ["Maimai", "Chunithm", "Wacca", "Sound Voltex"]

# Seconds before an unaccepted turn auto-skips
TURN_TIMEOUT_SECONDS = 60

# Server port
SERVER_PORT = 8080

# Cooldown when finishing with empty queue
COURTESY_COOLDOWN_SECONDS = 10

# Minutes of play time per gacha pull
GACHA_MINUTES_PER_PULL = 15

# Gacha character pool and rarity weights
GACHA_CHARACTERS = [...]
GACHA_RARITY_WEIGHTS = {
    "Common": 0.40,
    "Uncommon": 0.30,
    "Rare": 0.17,
    "Epic": 0.08,
    "Legendary": 0.03,
    "Uber": 0.0125,
    "Godlike": 0.0050,
    "Godslayer": 0.0025,
}
```

## How It Works

### Queue Flow

1. **Register/Login** - Create an account or log in
2. **Join** - Join one or more game queues
3. **Wait** - See your position in real-time
4. **Accept** - When it's your turn, accept within 60 seconds or get skipped
5. **Play** - Enjoy your game!
6. **Done** - Mark yourself as done so the next person can play

### Queue Rules

- If you're playing one game, you'll be skipped in other queues (but keep your place)
- Skip your turn and you go behind the next available person
- If no one else is waiting when you skip, you leave the queue
- After finishing with no one in queue, there's a short courtesy cooldown

### Gacha System

Players earn gacha pulls by accumulating play time across all games (default: 1 pull per 15 minutes). Characters come in 8 rarity tiers with drop rates visible in the collection section. Tap any owned character to view their full art, rarity, and description.

### Crystal Mine

An idle mini-game embedded in the page for players waiting in queue. Click to mine crystals, buy auto-generators (Pickaxe, Drill, Blaster, Laser, Quantum), and upgrade click power. The goal is to accumulate 100,000 crystals — but buying upgrades costs crystals, so there's a strategic tradeoff between investing and saving. Completing the game awards one bonus gacha pull, and you can play again immediately.

Game state persists in localStorage and survives page reloads (SSE updates).

### Admin Controls

The user with username "admin" gets access to:
- Pause/resume the queue globally
- Kick the current player from any game
- Add/remove players from queues
- Reorder queue positions
- Set any user as currently playing
- Reset session stats

## Troubleshooting

### "Python is not recognized"
- Reinstall Python and make sure to check "Add Python to PATH"

### "poetry is not recognized"
- Close and reopen your terminal after installing poetry
- Try: `python -m pip install poetry`

### Other devices can't connect
1. Check you're on the same Wi-Fi network
2. Allow the app through Windows Firewall
3. Try using the IP address instead of PC name: `http://192.168.x.x:8080`
   - Find your IP by running `ipconfig` in Command Prompt (Windows) or `ifconfig` (Mac/Linux)

### No sound on phone
- Make sure your phone isn't on silent mode
- Tap the screen when the "YOUR TURN" overlay appears to enable sound

## For Developers

### Project Structure

```
main.py              # FastAPI application (all routes and game logic)
config.py            # Configuration: games, timeouts, gacha pool, rarity weights
database.py          # SQLite persistence layer
templates/
  index.html         # Web UI (HTML + CSS + JavaScript)
tests/
  test_app.py        # Test suite (pytest + httpx)
data/
  queue.db           # SQLite database (auto-created)
gacha/               # Character images organized by rarity
```

### Development Commands

```bash
# Run with auto-reload during development
poetry run uvicorn main:app --host 0.0.0.0 --port 8080 --reload

# Run all tests
poetry run pytest

# Run a specific test
poetry run pytest tests/test_app.py::test_join_game -v

# Lint and format
poetry run ruff check .
poetry run ruff check . --fix
poetry run ruff format .
```

### Tech Stack

- **FastAPI** - Python web framework
- **Jinja2** - HTML templating
- **uvicorn** - ASGI server
- **aiosqlite** - Async SQLite for persistence
- **bcrypt** - Password hashing
- **Server-Sent Events** - Real-time browser updates

## License

MIT License - Feel free to use, modify, and share!
