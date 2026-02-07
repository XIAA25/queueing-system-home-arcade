# Configuration settings for the queueing system

# List of available games
GAME_NAMES = ["Maimai", "Chunithm", "Wacca", "Sound Voltex"]

# Seconds before an unaccepted turn auto-skips
TURN_TIMEOUT_SECONDS = 60

# Server port for the web application
SERVER_PORT = 5050

# Courtesy cooldown in seconds when finishing with empty queue
# Gives others a chance to join before the same player can requeue
COURTESY_COOLDOWN_SECONDS = 10

# Minutes of total play time (across all games) required per gacha pull
GACHA_MINUTES_PER_PULL = 15

# Gacha character pool with rarity tiers
GACHA_CHARACTERS = [
    # Common (8 characters) - 60% total
    {"name": "Derakkuma", "rarity": "Common", "emoji": "🐻‍❄️"},
    {"name": "Lime-kuma", "rarity": "Common", "emoji": "🐻"},
    {"name": "Lemon-kuma", "rarity": "Common", "emoji": "🍋"},
    {"name": "Ran", "rarity": "Common", "emoji": "🎀"},
    {"name": "Dorii", "rarity": "Common", "emoji": "🐱"},
    {"name": "Dandy Dan", "rarity": "Common", "emoji": "🎩"},
    {"name": "Chao", "rarity": "Common", "emoji": "🐧"},
    {"name": "Akatsuki", "rarity": "Common", "emoji": "🌅"},
    # Rare (7 characters) - 30% total
    {"name": "Ras", "rarity": "Rare", "emoji": "⚡"},
    {"name": "Chiffon", "rarity": "Rare", "emoji": "🧁"},
    {"name": "Salt", "rarity": "Rare", "emoji": "🧂"},
    {"name": "Shama", "rarity": "Rare", "emoji": "🔮"},
    {"name": "Milk", "rarity": "Rare", "emoji": "🥛"},
    {"name": "Owl", "rarity": "Rare", "emoji": "🦉"},
    {"name": "Ask", "rarity": "Rare", "emoji": "❓"},
    # Legendary (5 characters) - 10% total
    {"name": "Otohime", "rarity": "Legendary", "emoji": "👸"},
    {"name": "Kurohime", "rarity": "Legendary", "emoji": "🖤"},
    {"name": "Mika Yurisaki", "rarity": "Legendary", "emoji": "🌸"},
    {"name": "Acid", "rarity": "Legendary", "emoji": "💀"},
    {"name": "Ris", "rarity": "Legendary", "emoji": "✨"},
]

# Rarity weights for gacha pulls (total must match character distribution)
GACHA_RARITY_WEIGHTS = {
    "Common": 0.60,  # 60% total (7.5% each)
    "Rare": 0.30,  # 30% total (~4.3% each)
    "Legendary": 0.10,  # 10% total (2% each)
}
