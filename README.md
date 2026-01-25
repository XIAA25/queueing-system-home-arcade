# Home Arcade Queue System

A simple queue management system for home arcades. Players can join queues for different games from their phones, get notified when it's their turn, and manage their play sessions fairly.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Features

- **Multi-game support** - Manage queues for multiple arcade games simultaneously
- **Mobile-friendly** - Works on any device with a web browser
- **QR code access** - Scan to join from your phone
- **Turn notifications** - Sound and vibration alerts when it's your turn
- **Fair play**
  - 60-second timer to accept your turn (configurable)
  - Courtesy cooldown prevents immediate re-queuing when no one is waiting
  - Skip tracking shows who's been skipping turns
- **Session stats** - Track play time and session counts
- **Host controls** - Pause queue, kick players, reorder queue

## Quick Start (Windows)

### Step 1: Install Python

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important:** Check the box that says "Add Python to PATH"
4. Click "Install Now"

To verify installation, open Command Prompt and type:
```
python --version
```
You should see something like `Python 3.12.0`

### Step 2: Install Poetry (Python package manager)

Open Command Prompt and run:
```
pip install poetry
```

### Step 3: Download This Project

**Option A: Download ZIP**
1. Click the green "Code" button on this page
2. Click "Download ZIP"
3. Extract the ZIP to a folder (e.g., `C:\queueing-system`)

**Option B: Using Git**
```
git clone https://github.com/XIAA25/queueing-system-home-arcade.git
cd queueing-system-home-arcade
```

### Step 4: Install Dependencies

Open Command Prompt, navigate to the project folder, and run:
```
cd C:\queueing-system
poetry install
```

### Step 5: Run the Server

```
poetry run python main.py
```

You'll see output like:
```
Starting server on http://YOUR-PC-NAME:8080
```

### Step 6: Connect

- **On the host PC:** Open `http://localhost:8080` in your browser
- **On phones/other devices:**
  1. Make sure you're on the same Wi-Fi network
  2. Scan the QR code shown on the host's screen, OR
  3. Type the URL shown (e.g., `http://YOUR-PC-NAME:8080`)

**Windows Firewall:** The first time you run the server, Windows may ask to allow network access. Click "Allow" to let other devices connect.

## Configuration

Edit `config.py` to customize:

```python
# Games available in your arcade
GAME_NAMES = ["Maimai", "Chunithm", "Wacca", "Sound Voltex"]

# Seconds before an unaccepted turn auto-skips
TURN_TIMEOUT_SECONDS = 60

# Server port
SERVER_PORT = 8080

# Cooldown when finishing with empty queue (gives others a chance to join)
COURTESY_COOLDOWN_SECONDS = 10
```

## How It Works

1. **Join** - Players enter their name and join game queues
2. **Wait** - See your position in real-time
3. **Accept** - When it's your turn, accept within 60 seconds or get skipped
4. **Play** - Enjoy your game!
5. **Done** - Mark yourself as done so the next person can play

### Queue Rules

- If you're playing one game, you'll be skipped in other queues (but keep your place)
- Skip your turn and you go behind the next person
- If no one else is waiting when you skip, you leave the queue
- After finishing with no one in queue, there's a 10-second courtesy cooldown

## Troubleshooting

### "Python is not recognized"
- Reinstall Python and make sure to check "Add Python to PATH"

### "poetry is not recognized"
- Close and reopen Command Prompt after installing poetry
- Try: `python -m pip install poetry`

### Other devices can't connect
1. Check you're on the same Wi-Fi network
2. Allow the app through Windows Firewall
3. Try using the IP address instead of PC name: `http://192.168.x.x:8080`
   - Find your IP by running `ipconfig` in Command Prompt

### No sound on phone
- Make sure your phone isn't on silent mode
- Tap the screen when the "YOUR TURN" overlay appears to enable sound

## For Developers

### Project Structure
```
main.py              # FastAPI application
config.py            # Configuration settings
templates/
  index.html         # Web UI template
tests/
  test_app.py        # Test suite
```

### Development Commands

```bash
# Run with auto-reload
poetry run uvicorn main:app --host 0.0.0.0 --port 8080 --reload

# Run tests
poetry run pytest

# Lint code
poetry run ruff check .

# Format code
poetry run ruff format .
```

### Tech Stack

- **FastAPI** - Modern Python web framework
- **Jinja2** - HTML templating
- **uvicorn** - ASGI server

## License

MIT License - Feel free to use, modify, and share!
