# Configuration settings for the queueing system

# List of available games
GAME_NAMES = ["Maimai", "Chunithm", "Wacca", "Sound Voltex"]

# Seconds before an unaccepted turn auto-skips
TURN_TIMEOUT_SECONDS = 60

# Server port for the web application
SERVER_PORT = 8080

# Courtesy cooldown in seconds when finishing with empty queue
# Gives others a chance to join before the same player can requeue
COURTESY_COOLDOWN_SECONDS = 10
