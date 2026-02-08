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

# Minutes of total play time (across all games) required per gacha pull
GACHA_MINUTES_PER_PULL = 15


def _char(name: str, rarity: str, image: str, description: str) -> dict:
    return {"name": name, "rarity": rarity, "image": image, "description": description}


# Gacha character pool
# Images stored in gacha/<rarity>/<image>
GACHA_CHARACTERS = [
    # ── Godslayer  —
    _char("Squirp", "Godslayer", "SQUIRP.png", "The kindest soul in the roster—always cheering you on, even in the worst runs. Named after Squirp from Super Paper Mario."),
    _char("Bébé Evoli", "Godslayer", "BB_EVOLI.png", "Tiny, adorable, and absolutely terrifying. Looks like a cuddle, fights like a warning label—do not stand in his way."),
    _char("Arme de Destruction Massive", "Godslayer", "GIVROU.png", "A sleepy Glaceon adopted in Lyon—peaceful until awakened. Then it's instant winter… and collateral damage."),
    _char("Nijntje Gang", "Godslayer", "NIJNTJE_GANG.png", "The most feared crew of Miffys on the street. A little Spheal earned its place—now the gang rolls deeper than ever."),
    _char("Hot Doggie / Grande Ninette", "Godslayer", "NINETTE.png", "Not just a dog, not just a hotdog: a menace with charm. In love she's the one biting—affectionately. Mostly."),
    # ── Godlike —
    _char("Phi le Phoque", "Godlike", "PHI.png", "The third seal of the family, and a certified genius. Somehow holds 34 doctorates before age three—asks questions that break reality."),
    _char("Pha la Phoque", "Godlike", "PHA.png", "Also known as the Pet Demon. Second seal to arrive, XIAA's strict coach, and the #1 fan of \"Heavenly Blast.\""),
    _char("Pho le Phoque", "Godlike", "PHO.png", "The first seal to join the family—pure kindness in blubbery form. XIAA's trusted babysitter and a professional comfort provider."),
    _char("Shadow", "Godlike", "SHADOW.png", "A big white fluffy seal from Japan: half cloud, half pillow. If you nap near him, you're not waking up on schedule."),
    _char("Powow", "Godlike", "POWOW.png", "An unbelievably sweet grey seal you might have spotted around the couch. Gentle vibes, strong hugs, zero judgment—ever."),
    _char("Doudou Phoque", "Godlike", "DOUDOU_PHOQUE.png", "A seal lovingly crocheted by XIAA's mom. Soft as a spell and secretly magical—can transform into a turtle when duty calls."),
    # ── Uber —
    _char("Shama", "Uber", "SHAMA.png", "A maimai-born rival with sharp timing and sharper attitude. Shows up smiling—then farms perfects like it's nothing."),
    _char("Milk", "Uber", "MILK.png", "Sweet, calming, and deceptively strong. The kind of character that heals the party… and still top-scores the chart."),
    _char("Salt", "Uber", "SALT.png", "All sass, no mercy. Salt turns tiny mistakes into tragic stories—then laughs and offers a rematch anyway."),
    _char("Ras", "Uber", "RAS.png", "A stormy maimai spirit with restless energy. Every beat is a spark—miss one and the whole room feels it."),
    _char("Chiffon", "Uber", "CHIFFON.png", "Light as air, elegant as a combo streak. Chiffon drifts through chaos and leaves only glittering accuracy behind."),
    _char("Otohime", "Uber", "OTOHIME.png", "A rhythm princess with ocean-deep presence. Her steps sound like waves—beautiful, inevitable, and impossible to stop."),
    # ── Legendary —
    _char("Acid", "Legendary", "ACID.png", "The maimai icon from \"Straight Into The Lights.\" Neon confidence, razor focus—hits like a flashbang of precision."),
    _char("Raguel", "Legendary", "RAGUEL.png", "The maimai figure from \"Regulus.\" Celestial and severe—moves like starlight, judges like a constellation."),
    _char("Shikoku", "Legendary", "SHIKOKU.png", "The maimai character from \"Yorugao.\" Quiet midnight strength—gentle on the surface, devastating once the chorus drops."),
    _char("Mika Yurisaki", "Legendary", "MIKA_YURISAKI.png", "The maimai presence of \"Temptation.\" Graceful, dangerous, and charismatic—she turns pressure into performance art."),
    _char("Hatsune Miku", "Legendary", "HATSUNE MIKU.png", "The eternal virtual diva: bright, iconic, and endlessly adaptable. If a melody exists, Miku can become it."),
    _char("Zundamon", "Legendary", "ZUNDAMON.jpg", "A mischievous green mascot with unstoppable energy. Cute voice, chaotic spirit—turns every stage into a festival."),
    _char("Kagamine Rin", "Legendary", "KAGAMINE RIN.png", "A burst of sunshine with a rebellious edge. Rin's vocals cut clean—like laughter sprinting through distortion."),
    _char("Kagamine Len", "Legendary", "KAGAMINE LEN.png", "Cool, bright, and surprisingly tender. Len can go fierce or fragile in a heartbeat—and make both feel true."),
    _char("Megurine Luka", "Legendary", "MEGURINE LUKA.png", "Velvet voice, ocean gaze. Luka sings like dusk—smooth, powerful, and quietly impossible to forget."),
    _char("Kaito", "Legendary", "KAITO.png", "A classic blue vocalist with steady charisma. Kaito brings calm control—like a winter coat over a raging beat."),
    _char("Meiko", "Legendary", "MEIKO.png", "Warm power with a confident grin. Meiko's presence is pure stagecraft—bold, clean, and built for big choruses."),
    # ── Epic —
    _char("Kasane Teto (SV)", "Epic", "KASANE TETO _SV_.png", "The SynthV glow-up: sharper tone, brighter bite. Teto SV arrives with drill-hair pride and main-character energy."),
    _char("Kasane Teto (UTAU)", "Epic", "KASANE TETO _UTAU_.png", "The original legend—scrappy, iconic, and loud in the best way. UTAU Teto wins hearts by refusing to be ignored."),
    _char("Megpoid Gumi", "Epic", "MEGPOID GUMI.png", "A green pop comet with effortless charm. Gumi's voice is playful and punchy—made for hooks that stick forever."),
    _char("Kafu", "Epic", "KAFU.png", "Dreamy and delicate, like a song whispered into fog. Kafu turns softness into power—gentle notes, heavy impact."),
    _char("Flower", "Epic", "FLOWER.png", "A fierce voice with a razor edge—built for intensity. Flower doesn't ask for space; she takes the whole stage."),
    _char("Akita Neru", "Epic", "AKITA NERU.png", "The classic \"I'm not impressed\" vibe in human form. Neru's glare crits harder than most ultimates."),
    _char("Yowane Haku", "Epic", "YOWANE HAKU.png", "A gentle troublemaker with bittersweet charm. Haku looks fragile—until she lands the cleanest comeback of your life."),
    _char("Mesmerizer", "Epic", "MESMERIZER.png", "A hypnotic presence that turns attention into currency. The beat pulls you in—then your willpower quietly logs off."),
    _char("Rolling Girl", "Epic", "ROLLING GIRL.png", "A relentless runner fueled by emotion and momentum. She stumbles, stands, and keeps going—because stopping hurts more."),
    _char("Snobbism", "Epic", "SNOBBISM.png", "All swagger and side-eye, dressed in sharp rhythm. Snobbism fights with style—every move says, \"Try harder.\""),
    _char("Two Faced Lovers", "Epic", "TWO FACED LOVERS.png", "A romance with a glitch in the mirror. Sweetness and betrayal trade places mid-verse—blink and you'll miss the switch."),
    _char("World's End Dancehall", "Epic", "WORLD_S END DANCEHALL.png", "A party on the edge of collapse. The floor shakes, the lights scream, and you dance like the ending is the point."),
    _char("Meltdown (Adult Rin)", "Epic", "MELTDOWN _ADULT RIN_.png", "Grown-up fire with a dangerous calm. Adult Rin carries the same fuse—just smarter about when to light it."),
    _char("God-ish", "Epic", "GOD-ISH.png", "Confidence dialed past 100. God-ish doesn't claim divinity—she performs it, and dares you to disagree."),
    # ── Rare —
    _char("Defoko", "Rare", "DEFOKO.png", "The quiet default who somehow becomes everyone's favorite. Simple, sincere, and strangely unstoppable with the right team."),
    _char("Momone Momo", "Rare", "MOMONE MOMO.png", "A soft smile with surprising strength. Momo's vibe is cozy pop—but her timing hits like a practiced spell."),
    _char("Marry Kozakura", "Rare", "MARRY KOZAKURA _KAGEPRO_.png", "A gentle presence wrapped in mystery. Marry moves like a whisper—easy to overlook, impossible to forget."),
    _char("Lost One's Weeping", "Rare", "LOST ONE_S WEEPING.png", "A storm of frustration and speed. Every note feels like a confession you didn't mean to say out loud."),
    _char("Abstract Nonsense", "Rare", "ABSTRACT NONSENSE.png", "A brain-twister in musical form. Abstract Nonsense fights by confusing your instincts—then punishes hesitation."),
    _char("Melancholic", "Rare", "MELANCHOLIC.png", "Sweet on the surface, bittersweet underneath. Melancholic is the smile that wobbles when the chorus hits too hard."),
    _char("Calc.", "Rare", "CALC.png", "Quiet feelings measured in tiny steps. Calc. turns distance into decimals—then turns decimals into longing."),
    _char("Leia", "Rare", "LEIA.png", "A distant star of emotion—beautiful, untouchable, and sharp. Leia's melody feels like reaching for something just out of range."),
    _char("Shinzou Democracy", "Rare", "SHINZOU DEMOCRACY.png", "A heart-beat manifesto with marching energy. Loud, bright, and rebellious—turns a crowd into a chorus."),
    _char("Dear Doppelganger", "Rare", "DEAR DOPPELGANGER.png", "A letter to the version of you that wins. It's inspiring, unsettling, and way too accurate about your weak spots."),
    _char("Nyanyanyanyanyanyanya", "Rare", "NYANYANYANYANYANYANYA.png", "A cat-tastic combo machine. Ridiculous, catchy, and impossible to un-hear—your brain will be meowing for hours."),
    _char("Spinal Fluid Explosion Girl", "Rare", "SPINAL FLUID EXPLOSION GIRL.png", "Chaotic energy with a grin that says \"bad idea.\" She detonates the rhythm, then dances in the blast radius."),
    _char("Two Breaths Walking", "Rare", "TWO BREATHS WALKING.png", "A calm march through heavy feelings. Two breaths, one step—keeps moving even when the air runs thin."),
    _char("Junky Night Town Orchestra", "Rare", "JUNKY NIGHT TOWN ORCHESTRA.png", "A midnight parade of brass, neon, and bad decisions. The groove is glamorous—until you realize it never ends."),
    _char("Queen", "Rare", "QUEEN _GIRLS LIKE ME_.png", "Royal attitude, clean execution. Queen doesn't chase approval—she commands the room and makes the beat bow."),
    _char("Yowamushi Mont Blanc", "Rare", "YOWAMUSHI MONTBLANC.png", "A shy heart wrapped in fluffy snow. Mont Blanc looks soft—until the chorus reveals how deep the feelings go."),
    _char("Sarishinohara", "Rare", "SARISHINOHARA.png", "A nostalgic ache with gentle strength. Sarishinohara hits like an old photo—warm, painful, and real."),
    _char("Heat Abnormal", "Rare", "HEAT ABNORMAL.png", "Overheated emotions, boiling tempo. Heat Abnormal burns bright—stay too close and your timing starts to melt."),
    _char("Yurufuwa Jukai Girl", "Rare", "YURUFUWA JUKAI GIRL.png", "Cute, dreamy, and mildly cursed. A soft forest haze hides thorny rhythms that trap careless players."),
    _char("Goodbye Sengen (Rena)", "Rare", "GOODBYE SENGEN _RENA_.png", "A polite farewell with a surprisingly firm boundary. Rena smiles, waves, and shuts the door—no arguments accepted."),
    _char("Confessions of a Rotten Girl", "Rare", "CONFESSIONS OF A ROTTEN GIRL.png", "Honesty with teeth. She confesses everything—then weaponizes the truth to land critical hits on your pride."),
    _char("Idola Circus", "Rare", "IDOLA CIRCUS.png", "A carnival of chaos and charm. Bright colors, dark corners—Idola laughs while the rhythm tightrope snaps."),
    _char("Setsuna Trip", "Rare", "SETSUNA TRIP.png", "A short-lived adventure that feels like forever. Setsuna Trip rushes forward—because the moment won't wait."),
    _char("Hitomania", "Rare", "HITOMANIA.png", "A pulse of obsession dressed as a bop. Hitomania locks in, drowns out the world, and calls it devotion."),
    _char("Rotten Heresy & Chocolate", "Rare", "ROTTEN HERESY _ CHOCOLATE.png", "Sweet-and-sinful elegance. Chocolate on the tongue, heresy in the heart—stylish, dangerous, and weirdly addictive."),
    # ── Uncommon —
    _char("Mesmerizer II", "Uncommon", "MESMERIZER_2.png", "An awakened hypnotist—stronger pull, fewer escapes. The same charm, but now the rhythm stares back."),
    _char("Melancholic II", "Uncommon", "MELANCHOLIC_2.png", "A brighter smile with heavier undertones. Melancholic II feels sweeter… until you notice the hidden cracks."),
    _char("Leia II", "Uncommon", "LEIA_2.png", "More distant, more luminous. Leia II turns longing into a laser—precise, cold, and gorgeous to watch."),
    _char("Dear Doppelganger II", "Uncommon", "DEAR DOPPELGANGER_2.png", "The reply arrives—written in your own handwriting. Doppelganger II predicts your moves and counters your confidence."),
    _char("Spinal Fluid Explosion Girl II", "Uncommon", "SPINAL FLUID EXPLOSION GIRL_2.png", "Same chaos, refined ignition. Explosion Girl II doesn't just blow up—she aims the blast for maximum style points."),
    _char("Two Breaths Walking II", "Uncommon", "TWO BREATHS WALKING_2.png", "A steadier stride through heavier air. Two Breaths II keeps moving—slower, stronger, and far more determined."),
    _char("Junky Night Town Orchestra II", "Uncommon", "JUNKY NIGHT TOWN ORCHESTRA_2.png", "The parade returns with louder brass and darker neon. Orchestra II feels like a dream you shouldn't revisit… but do."),
    _char("Heat Abnormal II", "Uncommon", "HEAT ABNORMAL_2.png", "Temperature rising, patience dropping. Heat Abnormal II turns pressure into tempo—blink and you're already behind."),
    _char("Sarishinohara II", "Uncommon", "SARISHINOHARA_2.png", "A deeper nostalgia with sharper edges. Sarishinohara II hits like an old promise—still warm, still painful."),
    _char("Goodbye Sengen (Rena) II", "Uncommon", "GOODBYE SENGEN _RENA__2.png", "A stronger goodbye with zero hesitation. Rena II is kindness with boundaries—soft voice, locked door."),
    _char("Monitoring", "Uncommon", "MONITORING.png", "A watchful presence that counts every mistake. Monitoring doesn't attack loudly—she simply records, then punishes later."),
    _char("Monitoring II", "Uncommon", "MONITORING_2.png", "Upgraded sensors, harsher verdicts. Monitoring II sees through panic inputs and turns your habits into weaknesses."),
    _char("Shoujo Rei", "Uncommon", "SHOUJO REI.png", "A ghostly calm drifting under moonlight. Shoujo Rei is gentle, haunting, and strangely comforting—until the drop."),
    _char("Shoujo Rei II", "Uncommon", "SHOUJO REI_2.png", "The same moonlit hush, but closer. Shoujo Rei II feels like a hand on your shoulder—cold, honest, inescapable."),
    _char("Toumei Elegy", "Uncommon", "TOUMEI ELEGY.png", "Transparent sorrow with a beautiful sheen. Toumei Elegy fights quietly—by making your heart sync with the beat."),
    _char("Toumei Elegy II", "Uncommon", "TOUMEI ELEGY_2.png", "Sharper clarity, deeper ache. Toumei Elegy II turns subtle feelings into crisp timing checks you can't ignore."),
    _char("Kimi no Taion", "Uncommon", "KIMI NO TAION.png", "Warmth remembered like a lingering scarf. Kimi no Taion is intimate and soft—then hits you with sudden honesty."),
    _char("Kimi no Taion II", "Uncommon", "KIMI NO TAION_2.png", "The warmth fades, the truth remains. Taion II is calmer, but the emotional damage ticks harder every measure."),
    _char("Setsuna Plus", "Uncommon", "SETSUNA PLUS.png", "A bonus chapter of momentum—faster, brighter, riskier. Setsuna Plus turns \"one more try\" into a lifestyle."),
    _char("Setsuna Plus II", "Uncommon", "SETSUNA PLUS_2.png", "Double the rush, half the mercy. Setsuna Plus II is a sprint with fireworks strapped to your ankles."),
    _char("Lower", "Uncommon", "LOWER.png", "A cool descent into darker groove. Lower moves like gravity—steady, stylish, and impossible to resist."),
    _char("Lower II", "Uncommon", "LOWER_2.png", "Deeper bass, tighter steps. Lower II drags your rhythm downward—then rewards perfect control with pure swagger."),
    _char("Reon", "Uncommon", "REON.png", "A bright spark with a futuristic grin. Reon fights with clean lines—fast inputs, sharper returns."),
    _char("Reon II", "Uncommon", "REON_2.png", "An upgraded signal—stronger glow, stricter tempo. Reon II turns the arena into a neon chessboard."),
    _char("Meru", "Uncommon", "MERU.png", "A tender dreamer with hidden backbone. Meru's rhythm feels like floating—until you notice you're being pulled."),
    _char("Meru II", "Uncommon", "MERU_2.png", "More confident, more intense. Meru II stops drifting and starts steering—straight into your combo's weak points."),
    _char("Adorador", "Uncommon", "ADORADOR.png", "A devoted performer who shines under pressure. Adorador turns admiration into fuel—and fuel into flawless timing."),
    _char("MYK-IV", "Uncommon", "MYK-IV.png", "A glitchy unit with perfect calibration. MYK-IV doesn't feel emotions—yet somehow plays like it knows yours."),
    _char("Adachi Rei", "Uncommon", "ADACHI REI.png", "Deadpan charm with a quietly sharp edge. Adachi Rei speaks softly—then drops a chorus that stuns the whole room."),
    _char("Matsudappoiyo", "Uncommon", "MATSUDAPPOIYO.png", "Goofy chaos in human shape. Matsudappoiyo turns jokes into combos—messy, loud, and inexplicably effective."),
    _char("Android Girl", "Uncommon", "ANDROID GIRL.png", "A synthetic heart running on real feelings. Android Girl looks controlled—until the melody reveals the cracks in her code."),
    _char("Chain Girl", "Uncommon", "CHAIN GIRL.png", "Bound by rhythm, powered by rebellion. Chain Girl turns restraints into choreography—and makes it look effortless."),
    _char("Eh? Ah, Sou.", "Uncommon", "EH_ AH_ SOU.png", "Flirty confidence with a wink of danger. \"Eh? Ah, Sou.\" doesn't chase you—she waits, and you come anyway."),
    _char("Loveit", "Uncommon", "LOVEIT.png", "A sugar-rush anthem with sharp teeth. Loveit is adorable obsession—smiling while it squeezes your stamina bar."),
    _char("Magical Girl & Chocolate", "Uncommon", "MAGICAL GIRL _ CHOCOLATE.png", "Cute aesthetics, dark aftertaste. A magical-girl sparkle that hides something bitter—and keeps you coming back for more."),
    # ── Common —
    _char("4Gou", "Common", "4GOU.png", "A dependable unit with straightforward rhythm. 4Gou isn't flashy—just consistent, reliable, and always on-beat."),
    _char("Adorador II", "Common", "ADORADOR_2.png", "A simpler form of devotion—steady and bright. Adorador II is the warm-up that still surprises you."),
    _char("Adorador III", "Common", "ADORADOR_3.png", "More confidence, cleaner groove. Adorador III turns applause into armor and walks straight through pressure."),
    _char("Adorador IV", "Common", "ADORADOR_4.png", "The final, polished shine. Adorador IV performs like a legend-in-training—smooth, bold, and hard to interrupt."),
    _char("Aisuu", "Common", "AISUU.png", "A cool, bubbly presence—like a fizzy drink in summer. Aisuu keeps morale high and fingers moving."),
    _char("Android Girl II", "Common", "ANDROID GIRL_2.png", "A lighter, more stable build—still emotional, but better at hiding it. Android Girl II punishes sloppy rhythms politely."),
    _char("Butcher Vanity", "Common", "BUTCHER VANITY.png", "A stylish menace with a dramatic flair. Butcher Vanity slices through combos with elegance—then bows for applause."),
    _char("Chis-A", "Common", "CHIS-A.png", "A quirky voice with a friendly vibe. Chis-A feels like lo-fi pop—simple charm that keeps the run comfortable."),
    _char("Chis-A (English)", "Common", "CHIS-A _ENGLISH_.png", "Same charm, different flavor. English Chis-A sounds like a global broadcast—clear, upbeat, and easy to sing along to."),
    _char("Cyber Thunder Cider", "Common", "CYBER THUNDER CIDER.png", "Neon soda energy in musical form. Cyber Thunder Cider crackles with fizz, speed, and bright arcade confidence."),
    _char("Darling Dance (Nana)", "Common", "DARLING DANCE _NANA_.png", "A playful dance with just enough bite. Nana's version sparkles—cute steps, sly eyes, and combo-friendly swagger."),
    _char("How-To Sekai Seifuku (Azuma)", "Common", "HOW-TO SEKAI SEIFUKU _AZUMA_.png", "A cheerful \"world domination\" manual with sing-along energy. Azuma leads like a captain of pure enthusiasm."),
    _char("How-To Sekai Seifuku (Azuma) II", "Common", "HOW-TO SEKAI SEIFUKU _AZUMA__2.png", "Azuma returns with extra pep and tighter rhythm. Same plan, better execution—now the chorus hits harder."),
    _char("How-To Sekai Seifuku (Tsuji)", "Common", "HOW-TO SEKAI SEIFUKU _TSUJI_.png", "Tsuji's take is calmer, cooler, and a little sneaky. World domination, but with strategy and smooth timing."),
    _char("How-To Sekai Seifuku (Tsuji) II", "Common", "HOW-TO SEKAI SEIFUKU _TSUJI__2.png", "Sharper steps, stronger confidence. Tsuji II turns the \"how-to\" into an \"already done\"—and you're just catching up."),
    _char("Igaku", "Common", "IGAKU.png", "A clinical, precise vibe—like rhythm dissected under bright lights. Igaku rewards accuracy and punishes sloppy habits."),
    _char("Kirune", "Common", "KIRUNE.png", "A gentle wanderer with a melodic heartbeat. Kirune keeps things steady—perfect for building confidence and streaks."),
    _char("Lamprey Hole", "Common", "LAMPREY HOLE.png", "Weird, catchy, and slightly unsettling. Lamprey Hole pulls you in with groove—then dares you not to look away."),
    _char("Liee", "Common", "LIEE.png", "A small liar with a big chorus. Liee's charm is suspiciously sweet—until the rhythm reveals the prank."),
    _char("Messed Up Wonderful World", "Common", "MESSED UP WONDERFUL WORLD.png", "Bright colors over cracked reality. It's wonderful, it's broken—somehow both at once, and you can't stop dancing."),
    _char("Migi ni Ma Girl", "Common", "MIGI NI MA GIRL.png", "A sideways-step specialist with a playful twist. Migi ni Ma Girl turns odd rhythms into clean, satisfying patterns."),
    _char("NurseRobotType_T", "Common", "NURSEROBOTTYPE_T.png", "A medical android with gentle hands and strict timing. She'll patch you up—then lecture you for missing easy notes."),
    _char("Override", "Common", "OVERRIDE.png", "A command prompt with attitude. Override takes control of the tempo—if you fight it, you lose."),
    _char("Protodisco", "Common", "PROTODISCO.png", "A slick retro-future groove with sharp edges. Protodisco moves like chrome—smooth, reflective, and coldly stylish."),
    _char("Q", "Common", "Q.png", "A minimalist mystery. Q says little, does everything—one perfect input at a time, like it's solving you."),
    _char("Queen II", "Common", "QUEEN _GIRLS LIKE ME__2.png", "A calmer crown, stronger control. Queen II rules through precision—less attitude, more inevitability."),
    _char("Queen III", "Common", "QUEEN _GIRLS LIKE ME__3.png", "The throne hardens into steel. Queen III punishes hesitations and rewards confident, clean execution."),
    _char("Queen IV", "Common", "QUEEN _GIRLS LIKE ME__4.png", "Fully ascended royalty. Queen IV doesn't just win—she makes winning look like the default state of existence."),
    _char("Saihate", "Common", "SAIHATE.png", "A faraway ending with a quiet glow. Saihate feels like a long road—beautiful, lonely, and worth walking anyway."),
    _char("Saihate II", "Common", "SAIHATE_2.png", "The horizon shifts closer—but the ache deepens. Saihate II turns distance into tempo and asks you to endure."),
    _char("Sarishinohara III", "Common", "SARISHINOHARA_3.png", "A sturdier nostalgia—less fragile, more resolved. Sarishinohara III turns regret into rhythm you can actually hold."),
    _char("Sarishinohara IV", "Common", "SARISHINOHARA_4.png", "The final form of remembering: calm, clear, and heavy. Sarishinohara IV hits like acceptance—quietly devastating."),
    _char("Suicide Parade", "Common", "SUICIDE PARADE.png", "A dark parade with a catchy step. It's not here to be gentle—just honest, loud, and painfully memorable."),
    _char("Tanaka San", "Common", "TANAKA SAN.png", "A comedic everyperson with unexpected groove. Tanaka San stumbles into the spotlight—and somehow nails the chorus."),
    _char("Unfriendly Hater (Mizuki)", "Common", "UNFRIENDLY HATER _MIZUKI_.png", "Mizuki's flavor is sharp and unapologetic. An unfriendly hater who thrives on spite—and converts it into perfect timing."),
    _char("Unfriendly Hater (Momose)", "Common", "UNFRIENDLY HATER _MOMOSE_.png", "Momose brings colder sarcasm and cleaner rhythm. Still a hater—just with smoother footwork and scarier consistency."),
    _char("Yi Er Fan Club (Gumi)", "Common", "YI ER FAN CLUB _GUMI_.png", "High-energy fan-club chaos—Gumi edition. Cheerful, bouncy, and built for making even hard charts feel like a party."),
    _char("Yi Er Fan Club (Rin)", "Common", "YI ER FAN CLUB _RIN_.png", "Rin's version is extra bright and extra loud. The fan club marches forward—smiling—and your fingers follow."),
    _char("Yogatari Tobari", "Common", "YOGATARI TOBARI.png", "A storyteller wrapped in dusk-colored calm. Yogatari Tobari spins rhythm like folklore—soft voice, sharp cadence."),
]

# Rarity weights for gacha pulls
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
