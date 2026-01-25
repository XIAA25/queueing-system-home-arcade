# Configuration settings for the queueing system

# List of available games
GAME_NAMES = ["Maimai", "Chunithm", "Wacca", "Sound Voltex", "Groove Coaster"]
GAME_NAMES.append("Tea party")
GAME_NAMES.extend([f"You should read, but if you really want to play a game, continue scrolling down ({i}) Maimai Chunithm Wacca Sound Voltex Groove Coaster (no ctrl-f for you)"for i in range(40000, 0, -1)])
GAME_NAMES.extend([f"Math book {i} "for i in range(40, 0, -1)])
GAME_NAMES.extend([f"Deep in Abyss {i} "for i in range(12, 0, -1)])
GAME_NAMES.extend([f"Apothicary diaries {i} "for i in range(13, 0, -1)])
GAME_NAMES.extend([f"Assassins Creed {i} "for i in range(5, 0, -1)])
GAME_NAMES.extend([f"Final Fantasy {i} "for i in range(16, 0, -1)])

# Seconds before an unaccepted turn auto-skips
TURN_TIMEOUT_SECONDS = 60

# Server port for the web application
SERVER_PORT = 8080

# Courtesy cooldown in seconds when finishing with empty queue
# Gives others a chance to join before the same player can requeue
COURTESY_COOLDOWN_SECONDS = 10
