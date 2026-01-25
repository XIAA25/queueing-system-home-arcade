import time

import pytest
from httpx import ASGITransport, AsyncClient

import main
from main import Game, app


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True
    ) as ac:
        yield ac


@pytest.fixture(autouse=True)
def reset_state():
    """Reset game state before each test."""
    main.games = {name: Game(name=name) for name in main.GAME_NAMES}
    main.queue_paused = False
    main.pause_started_at = None
    yield
    main.games = {name: Game(name=name) for name in main.GAME_NAMES}
    main.queue_paused = False
    main.pause_started_at = None


async def test_index_without_player(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert "Enter Your Name" in response.text


async def test_register(client):
    response = await client.post("/register", data={"name": "Alice"})
    assert response.status_code == 200
    assert "Alice" in response.text
    assert "player" in client.cookies


async def test_register_empty_name_generates_guest(client):
    response = await client.post("/register", data={"name": ""})
    assert response.status_code == 200
    assert "Guest-" in response.text


async def test_join_game(client):
    client.cookies.set("player", "Bob")
    response = await client.post("/join/Maimai")
    assert response.status_code == 200
    assert main.games["Maimai"].now_playing == "Bob"


async def test_join_multiple_games(client):
    client.cookies.set("player", "Carol")

    # Carol joins Maimai - becomes player since queue empty
    await client.post("/join/Maimai")
    # Accept the turn first
    await client.post("/accept/Maimai")
    assert main.games["Maimai"].now_playing == "Carol"

    # Carol joins Chunithm - should be in queue (already playing Maimai)
    await client.post("/join/Chunithm")
    assert "Carol" in main.games["Chunithm"].queue
    assert main.games["Chunithm"].now_playing is None  # No one available


async def test_skip_player_already_playing():
    """When advancing, skip players who are already playing another game."""
    main.games["Maimai"].now_playing = "Alice"
    main.games["Maimai"].turn_accepted = True
    main.games["Maimai"].queue = []
    main.games["Chunithm"].now_playing = None
    main.games["Chunithm"].queue = ["Alice", "Bob", "Carol"]

    main.advance_game(main.games["Chunithm"])

    # Alice should be skipped (playing Maimai), Bob becomes player
    assert main.games["Chunithm"].now_playing == "Bob"
    # Alice should be at front of queue (like a normal skip), ahead of Carol
    assert main.games["Chunithm"].queue == ["Alice", "Carol"]


async def test_done_playing(client):
    main.games["Maimai"].now_playing = "Dave"
    main.games["Maimai"].turn_accepted = True
    main.games["Maimai"].queue = ["Eve"]
    client.cookies.set("player", "Dave")

    response = await client.post("/done/Maimai")
    assert response.status_code == 200
    assert main.games["Maimai"].now_playing == "Eve"
    assert main.games["Maimai"].queue == []


async def test_done_playing_triggers_other_games():
    """When a player finishes, they may become available for other games."""
    main.games["Maimai"].now_playing = "Frank"
    main.games["Maimai"].turn_accepted = True
    main.games["Maimai"].queue = []
    main.games["Chunithm"].now_playing = None
    main.games["Chunithm"].queue = ["Frank"]

    # Frank finishes Maimai
    main.games["Maimai"].now_playing = None
    main.advance_game(main.games["Maimai"])

    # Now advance Chunithm - Frank should be available
    main.advance_game(main.games["Chunithm"])
    assert main.games["Chunithm"].now_playing == "Frank"


async def test_leave_queue(client):
    main.games["Wacca"].queue = ["Grace", "Henry"]
    client.cookies.set("player", "Grace")

    response = await client.post("/leave/Wacca")
    assert response.status_code == 200
    assert main.games["Wacca"].queue == ["Henry"]


async def test_logout_removes_from_all_games(client):
    main.games["Maimai"].now_playing = "Ivan"
    main.games["Maimai"].turn_accepted = True
    main.games["Chunithm"].queue = ["Ivan"]
    client.cookies.set("player", "Ivan")

    response = await client.post("/logout")
    assert response.status_code == 200
    assert main.games["Maimai"].now_playing is None
    assert "Ivan" not in main.games["Chunithm"].queue


async def test_accept_turn(client):
    """Player must accept their turn within the timeout period."""
    client.cookies.set("player", "Kim")
    await client.post("/join/Maimai")

    # Kim should be now_playing but not yet accepted
    assert main.games["Maimai"].now_playing == "Kim"
    assert main.games["Maimai"].turn_accepted is False
    assert main.games["Maimai"].turn_started_at is not None

    # Accept the turn
    response = await client.post("/accept/Maimai")
    assert response.status_code == 200
    assert main.games["Maimai"].turn_accepted is True


async def test_turn_expires_without_accept():
    """If player doesn't accept within timeout, they get skipped."""
    main.games["Maimai"].now_playing = "Slow"
    main.games["Maimai"].turn_accepted = False
    main.games["Maimai"].turn_started_at = time.time() - 65  # Past timeout
    main.games["Maimai"].queue = ["Next"]

    main.check_expired_turns()

    # Slow should be skipped, Next becomes player
    assert main.games["Maimai"].now_playing == "Next"
    assert main.games["Maimai"].turn_started_at is not None


async def test_accepted_turn_does_not_expire():
    """If player accepted, they don't get skipped even after timeout."""
    main.games["Maimai"].now_playing = "Active"
    main.games["Maimai"].turn_accepted = True
    main.games["Maimai"].turn_started_at = time.time() - 60  # 60 seconds ago
    main.games["Maimai"].queue = ["Waiting"]

    main.check_expired_turns()

    # Active should still be playing since they accepted
    assert main.games["Maimai"].now_playing == "Active"


async def test_skip_turn(client):
    """Skip puts you behind next person but ahead of others."""
    # Setup: A is playing, B and C are in queue
    main.games["Maimai"].now_playing = "A"
    main.games["Maimai"].turn_accepted = False
    main.games["Maimai"].turn_started_at = time.time()
    main.games["Maimai"].queue = ["B", "C"]
    client.cookies.set("player", "A")

    response = await client.post("/skip/Maimai")
    assert response.status_code == 200

    # B should now be playing, A should be first in queue (before C)
    assert main.games["Maimai"].now_playing == "B"
    assert main.games["Maimai"].queue == ["A", "C"]


async def test_skip_only_works_before_accept(client):
    """Cannot skip after accepting turn."""
    main.games["Maimai"].now_playing = "Player"
    main.games["Maimai"].turn_accepted = True
    main.games["Maimai"].turn_started_at = time.time()
    main.games["Maimai"].queue = ["Other"]
    client.cookies.set("player", "Player")

    await client.post("/skip/Maimai")

    # Should still be playing since already accepted
    assert main.games["Maimai"].now_playing == "Player"
    assert main.games["Maimai"].queue == ["Other"]


async def test_skip_with_empty_queue_leaves(client):
    """Skip when no one else in queue means you leave entirely."""
    main.games["Maimai"].now_playing = "Solo"
    main.games["Maimai"].turn_accepted = False
    main.games["Maimai"].turn_started_at = time.time()
    main.games["Maimai"].queue = []
    client.cookies.set("player", "Solo")

    await client.post("/skip/Maimai")

    # Player should be gone entirely
    assert main.games["Maimai"].now_playing is None
    assert main.games["Maimai"].queue == []


async def test_timeout_same_as_skip():
    """Timeout has same effect as skip - go behind next person."""
    main.games["Maimai"].now_playing = "Slow"
    main.games["Maimai"].turn_accepted = False
    main.games["Maimai"].turn_started_at = time.time() - 65  # Past timeout
    main.games["Maimai"].queue = ["Next", "Last"]

    main.check_expired_turns()

    # Next should be playing, Slow should be first in queue
    assert main.games["Maimai"].now_playing == "Next"
    assert main.games["Maimai"].queue == ["Slow", "Last"]


async def test_timeout_with_empty_queue_leaves():
    """Timeout when no one else in queue means player leaves."""
    main.games["Maimai"].now_playing = "Alone"
    main.games["Maimai"].turn_accepted = False
    main.games["Maimai"].turn_started_at = time.time() - 65  # Past timeout
    main.games["Maimai"].queue = []

    main.check_expired_turns()

    assert main.games["Maimai"].now_playing is None
    assert main.games["Maimai"].queue == []


async def test_leave_during_pending(client):
    """Can leave queue even when it's your turn (pending)."""
    main.games["Maimai"].now_playing = "Leaving"
    main.games["Maimai"].turn_accepted = False
    main.games["Maimai"].turn_started_at = time.time()
    main.games["Maimai"].queue = ["Next"]
    client.cookies.set("player", "Leaving")

    await client.post("/leave/Maimai")

    # Next should now be playing
    assert main.games["Maimai"].now_playing == "Next"
    assert main.games["Maimai"].queue == []


async def test_toggle_pause(client):
    """Toggle pause should switch the paused state."""
    assert main.queue_paused is False

    await client.post("/toggle-pause")
    assert main.queue_paused is True

    await client.post("/toggle-pause")
    assert main.queue_paused is False


async def test_paused_prevents_advance():
    """When paused, advance_game should not change state."""
    main.queue_paused = True
    main.games["Maimai"].now_playing = None
    main.games["Maimai"].queue = ["Alice"]

    main.advance_game(main.games["Maimai"])

    # Should not have advanced because paused
    assert main.games["Maimai"].now_playing is None
    assert main.games["Maimai"].queue == ["Alice"]


async def test_paused_prevents_timeout():
    """When paused, expired turns should not be skipped."""
    main.queue_paused = True
    main.games["Maimai"].now_playing = "Slow"
    main.games["Maimai"].turn_accepted = False
    main.games["Maimai"].turn_started_at = time.time() - 120  # Long expired
    main.games["Maimai"].queue = ["Next"]

    main.check_expired_turns()

    # Should not have skipped because paused
    assert main.games["Maimai"].now_playing == "Slow"
    assert main.games["Maimai"].queue == ["Next"]


async def test_multiple_players_skipped_stay_in_order():
    """Multiple busy players should maintain relative order when skipped."""
    main.games["Maimai"].now_playing = "Alice"
    main.games["Maimai"].turn_accepted = True
    main.games["Chunithm"].now_playing = "Bob"
    main.games["Chunithm"].turn_accepted = True
    main.games["Wacca"].now_playing = None
    main.games["Wacca"].queue = ["Alice", "Bob", "Carol", "Dave"]

    main.advance_game(main.games["Wacca"])

    # Carol should be playing, Alice and Bob skipped but in original order
    assert main.games["Wacca"].now_playing == "Carol"
    assert main.games["Wacca"].queue == ["Alice", "Bob", "Dave"]


async def test_skip_count_increments(client):
    """Skip count should increment each time a player skips."""
    main.games["Maimai"].now_playing = "Skipper"
    main.games["Maimai"].turn_accepted = False
    main.games["Maimai"].turn_started_at = time.time()
    main.games["Maimai"].queue = ["Next"]
    client.cookies.set("player", "Skipper")

    # First skip
    await client.post("/skip/Maimai")
    assert main.games["Maimai"].skip_counts.get("Skipper") == 1

    # Simulate becoming current player again
    main.games["Maimai"].now_playing = "Skipper"
    main.games["Maimai"].turn_accepted = False
    main.games["Maimai"].turn_started_at = time.time()
    main.games["Maimai"].queue = ["Next"]

    # Second skip
    await client.post("/skip/Maimai")
    assert main.games["Maimai"].skip_counts.get("Skipper") == 2


async def test_accept_clears_skip_count(client):
    """Accepting a turn should clear the skip count."""
    main.games["Maimai"].now_playing = "Player"
    main.games["Maimai"].turn_accepted = False
    main.games["Maimai"].turn_started_at = time.time()
    main.games["Maimai"].skip_counts["Player"] = 3
    client.cookies.set("player", "Player")

    await client.post("/accept/Maimai")

    assert main.games["Maimai"].skip_counts.get("Player") is None


async def test_session_count_increments_on_accept(client):
    """Session count should increment when player accepts turn."""
    main.games["Maimai"].now_playing = "Player"
    main.games["Maimai"].turn_accepted = False
    main.games["Maimai"].turn_started_at = time.time()
    client.cookies.set("player", "Player")

    await client.post("/accept/Maimai")

    assert main.games["Maimai"].session_counts.get("Player") == 1
    assert main.games["Maimai"].play_started_at is not None


async def test_total_play_time_accumulates(client):
    """Total play time should accumulate across sessions."""
    client.cookies.set("player", "Player")

    # First session
    main.games["Maimai"].now_playing = "Player"
    main.games["Maimai"].turn_accepted = True
    main.games["Maimai"].play_started_at = time.time() - 120  # 2 minutes ago

    await client.post("/done/Maimai")

    assert main.games["Maimai"].total_play_time.get("Player", 0) >= 119  # ~2 mins


async def test_skip_leaves_when_only_unavailable_players_in_queue(client):
    """Skipping should leave queue if everyone else is playing other games.

    Scenario: A plays Game1, A queued for Game2. B joins Game2.
    B gets prompted (A skipped because playing). If B skips, B should leave
    since A is the only other person and A is unavailable.
    """
    # A is playing Maimai and queued for Chunithm
    main.games["Maimai"].now_playing = "PlayerA"
    main.games["Maimai"].turn_accepted = True
    main.games["Chunithm"].queue = ["PlayerA"]

    # B joins Chunithm - B becomes now_playing (A is skipped because playing)
    client.cookies.set("player", "PlayerB")
    await client.post("/join/Chunithm")

    assert main.games["Chunithm"].now_playing == "PlayerB"
    assert "PlayerA" in main.games["Chunithm"].queue

    # B skips - B should leave entirely (not go behind A who is unavailable)
    await client.post("/skip/Chunithm")

    assert main.games["Chunithm"].now_playing is None  # No one available
    assert "PlayerB" not in main.games["Chunithm"].queue  # B left
    assert "PlayerA" in main.games["Chunithm"].queue  # A still waiting
