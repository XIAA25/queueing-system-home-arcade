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


def _char(name: str, rarity: str, image: str) -> dict:
    return {"name": name, "rarity": rarity, "image": image}


# Gacha character pool — 119 Vocaloid pixel art characters
# Images stored in gacha/<rarity>/<image>
GACHA_CHARACTERS = [
    # ── Legendary (6) — The iconic Crypton Vocaloids ──
    _char("Hatsune Miku", "Legendary", "HATSUNE MIKU.png"),
    _char("Kagamine Rin", "Legendary", "KAGAMINE RIN.png"),
    _char("Kagamine Len", "Legendary", "KAGAMINE LEN.png"),
    _char("Megurine Luka", "Legendary", "MEGURINE LUKA.png"),
    _char("Kaito", "Legendary", "KAITO.png"),
    _char("Meiko", "Legendary", "MEIKO.png"),
    # ── Epic (14) — Popular Vocaloids + iconic song characters ──
    _char("Kasane Teto (SV)", "Epic", "KASANE TETO _SV_.png"),
    _char("Kasane Teto (UTAU)", "Epic", "KASANE TETO _UTAU_.png"),
    _char("Megpoid Gumi", "Epic", "MEGPOID GUMI.png"),
    _char("Kafu", "Epic", "KAFU.png"),
    _char("Flower", "Epic", "FLOWER.png"),
    _char("Akita Neru", "Epic", "AKITA NERU.png"),
    _char("Yowane Haku", "Epic", "YOWANE HAKU.png"),
    _char("Mesmerizer", "Epic", "MESMERIZER.png"),
    _char("Rolling Girl", "Epic", "ROLLING GIRL.png"),
    _char("Snobbism", "Epic", "SNOBBISM.png"),
    _char("Two Faced Lovers", "Epic", "TWO FACED LOVERS.png"),
    _char("World's End Dancehall", "Epic", "WORLD_S END DANCEHALL.png"),
    _char("Meltdown (Adult Rin)", "Epic", "MELTDOWN _ADULT RIN_.png"),
    _char("God-ish", "Epic", "GOD-ISH.png"),
    # ── Rare (25) — Well-known song characters + notable UTAUs ──
    _char("Defoko", "Rare", "DEFOKO.png"),
    _char("Momone Momo", "Rare", "MOMONE MOMO.png"),
    _char("Marry Kozakura", "Rare", "MARRY KOZAKURA _KAGEPRO_.png"),
    _char("Lost One's Weeping", "Rare", "LOST ONE_S WEEPING.png"),
    _char("Abstract Nonsense", "Rare", "ABSTRACT NONSENSE.png"),
    _char("Melancholic", "Rare", "MELANCHOLIC.png"),
    _char("Calc.", "Rare", "CALC.png"),
    _char("Leia", "Rare", "LEIA.png"),
    _char("Shinzou Democracy", "Rare", "SHINZOU DEMOCRACY.png"),
    _char("Dear Doppelganger", "Rare", "DEAR DOPPELGANGER.png"),
    _char("Nyanyanyanyanyanyanya", "Rare", "NYANYANYANYANYANYANYA.png"),
    _char(
        "Spinal Fluid Explosion Girl",
        "Rare",
        "SPINAL FLUID EXPLOSION GIRL.png",
    ),
    _char("Two Breaths Walking", "Rare", "TWO BREATHS WALKING.png"),
    _char(
        "Junky Night Town Orchestra",
        "Rare",
        "JUNKY NIGHT TOWN ORCHESTRA.png",
    ),
    _char("Queen", "Rare", "QUEEN _GIRLS LIKE ME_.png"),
    _char("Yowamushi Mont Blanc", "Rare", "YOWAMUSHI MONTBLANC.png"),
    _char("Sarishinohara", "Rare", "SARISHINOHARA.png"),
    _char("Heat Abnormal", "Rare", "HEAT ABNORMAL.png"),
    _char("Yurufuwa Jukai Girl", "Rare", "YURUFUWA JUKAI GIRL.png"),
    _char("Goodbye Sengen (Rena)", "Rare", "GOODBYE SENGEN _RENA_.png"),
    _char(
        "Confessions of a Rotten Girl",
        "Rare",
        "CONFESSIONS OF A ROTTEN GIRL.png",
    ),
    _char("Idola Circus", "Rare", "IDOLA CIRCUS.png"),
    _char("Setsuna Trip", "Rare", "SETSUNA TRIP.png"),
    _char("Hitomania", "Rare", "HITOMANIA.png"),
    _char(
        "Rotten Heresy & Chocolate",
        "Rare",
        "ROTTEN HERESY _ CHOCOLATE.png",
    ),
    # ── Uncommon (35) — Song variants + secondary characters ──
    _char("Mesmerizer II", "Uncommon", "MESMERIZER_2.png"),
    _char("Melancholic II", "Uncommon", "MELANCHOLIC_2.png"),
    _char("Leia II", "Uncommon", "LEIA_2.png"),
    _char("Dear Doppelganger II", "Uncommon", "DEAR DOPPELGANGER_2.png"),
    _char(
        "Spinal Fluid Explosion Girl II",
        "Uncommon",
        "SPINAL FLUID EXPLOSION GIRL_2.png",
    ),
    _char(
        "Two Breaths Walking II",
        "Uncommon",
        "TWO BREATHS WALKING_2.png",
    ),
    _char(
        "Junky Night Town Orchestra II",
        "Uncommon",
        "JUNKY NIGHT TOWN ORCHESTRA_2.png",
    ),
    _char("Heat Abnormal II", "Uncommon", "HEAT ABNORMAL_2.png"),
    _char("Sarishinohara II", "Uncommon", "SARISHINOHARA_2.png"),
    _char(
        "Goodbye Sengen (Rena) II",
        "Uncommon",
        "GOODBYE SENGEN _RENA__2.png",
    ),
    _char("Monitoring", "Uncommon", "MONITORING.png"),
    _char("Monitoring II", "Uncommon", "MONITORING_2.png"),
    _char("Shoujo Rei", "Uncommon", "SHOUJO REI.png"),
    _char("Shoujo Rei II", "Uncommon", "SHOUJO REI_2.png"),
    _char("Toumei Elegy", "Uncommon", "TOUMEI ELEGY.png"),
    _char("Toumei Elegy II", "Uncommon", "TOUMEI ELEGY_2.png"),
    _char("Kimi no Taion", "Uncommon", "KIMI NO TAION.png"),
    _char("Kimi no Taion II", "Uncommon", "KIMI NO TAION_2.png"),
    _char("Setsuna Plus", "Uncommon", "SETSUNA PLUS.png"),
    _char("Setsuna Plus II", "Uncommon", "SETSUNA PLUS_2.png"),
    _char("Lower", "Uncommon", "LOWER.png"),
    _char("Lower II", "Uncommon", "LOWER_2.png"),
    _char("Reon", "Uncommon", "REON.png"),
    _char("Reon II", "Uncommon", "REON_2.png"),
    _char("Meru", "Uncommon", "MERU.png"),
    _char("Meru II", "Uncommon", "MERU_2.png"),
    _char("Adorador", "Uncommon", "ADORADOR.png"),
    _char("MYK-IV", "Uncommon", "MYK-IV.png"),
    _char("Adachi Rei", "Uncommon", "ADACHI REI.png"),
    _char("Matsudappoiyo", "Uncommon", "MATSUDAPPOIYO.png"),
    _char("Android Girl", "Uncommon", "ANDROID GIRL.png"),
    _char("Chain Girl", "Uncommon", "CHAIN GIRL.png"),
    _char("Eh? Ah, Sou.", "Uncommon", "EH_ AH_ SOU.png"),
    _char("Loveit", "Uncommon", "LOVEIT.png"),
    _char(
        "Magical Girl & Chocolate",
        "Uncommon",
        "MAGICAL GIRL _ CHOCOLATE.png",
    ),
    # ── Common (39) — Remaining variants + obscure characters ──
    _char("4Gou", "Common", "4GOU.png"),
    _char("Adorador II", "Common", "ADORADOR_2.png"),
    _char("Adorador III", "Common", "ADORADOR_3.png"),
    _char("Adorador IV", "Common", "ADORADOR_4.png"),
    _char("Aisuu", "Common", "AISUU.png"),
    _char("Android Girl II", "Common", "ANDROID GIRL_2.png"),
    _char("Butcher Vanity", "Common", "BUTCHER VANITY.png"),
    _char("Chis-A", "Common", "CHIS-A.png"),
    _char("Chis-A (English)", "Common", "CHIS-A _ENGLISH_.png"),
    _char("Cyber Thunder Cider", "Common", "CYBER THUNDER CIDER.png"),
    _char("Darling Dance (Nana)", "Common", "DARLING DANCE _NANA_.png"),
    _char(
        "How-To Sekai Seifuku (Azuma)",
        "Common",
        "HOW-TO SEKAI SEIFUKU _AZUMA_.png",
    ),
    _char(
        "How-To Sekai Seifuku (Azuma) II",
        "Common",
        "HOW-TO SEKAI SEIFUKU _AZUMA__2.png",
    ),
    _char(
        "How-To Sekai Seifuku (Tsuji)",
        "Common",
        "HOW-TO SEKAI SEIFUKU _TSUJI_.png",
    ),
    _char(
        "How-To Sekai Seifuku (Tsuji) II",
        "Common",
        "HOW-TO SEKAI SEIFUKU _TSUJI__2.png",
    ),
    _char("Igaku", "Common", "IGAKU.png"),
    _char("Kirune", "Common", "KIRUNE.png"),
    _char("Lamprey Hole", "Common", "LAMPREY HOLE.png"),
    _char("Liee", "Common", "LIEE.png"),
    _char(
        "Messed Up Wonderful World",
        "Common",
        "MESSED UP WONDERFUL WORLD.png",
    ),
    _char("Migi ni Ma Girl", "Common", "MIGI NI MA GIRL.png"),
    _char("NurseRobotType_T", "Common", "NURSEROBOTTYPE_T.png"),
    _char("Override", "Common", "OVERRIDE.png"),
    _char("Protodisco", "Common", "PROTODISCO.png"),
    _char("Q", "Common", "Q.png"),
    _char("Queen II", "Common", "QUEEN _GIRLS LIKE ME__2.png"),
    _char("Queen III", "Common", "QUEEN _GIRLS LIKE ME__3.png"),
    _char("Queen IV", "Common", "QUEEN _GIRLS LIKE ME__4.png"),
    _char("Saihate", "Common", "SAIHATE.png"),
    _char("Saihate II", "Common", "SAIHATE_2.png"),
    _char("Sarishinohara III", "Common", "SARISHINOHARA_3.png"),
    _char("Sarishinohara IV", "Common", "SARISHINOHARA_4.png"),
    _char("Suicide Parade", "Common", "SUICIDE PARADE.png"),
    _char("Tanaka San", "Common", "TANAKA SAN.png"),
    _char(
        "Unfriendly Hater (Mizuki)",
        "Common",
        "UNFRIENDLY HATER _MIZUKI_.png",
    ),
    _char(
        "Unfriendly Hater (Momose)",
        "Common",
        "UNFRIENDLY HATER _MOMOSE_.png",
    ),
    _char("Yi Er Fan Club (Gumi)", "Common", "YI ER FAN CLUB _GUMI_.png"),
    _char("Yi Er Fan Club (Rin)", "Common", "YI ER FAN CLUB _RIN_.png"),
    _char("Yogatari Tobari", "Common", "YOGATARI TOBARI.png"),
]

# Rarity weights for gacha pulls
GACHA_RARITY_WEIGHTS = {
    "Common": 0.40,
    "Uncommon": 0.30,
    "Rare": 0.18,
    "Epic": 0.09,
    "Legendary": 0.03,
}
