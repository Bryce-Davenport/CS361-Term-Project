from datetime import datetime
from typing import Any, Dict, List

from flask import Flask, jsonify, request

app = Flask(__name__)


def _parse_int(value: Any) -> int | None:

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@app.post("/upcoming-releases")
def upcoming_releases():

    current_year = datetime.now().year

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "games" not in data:
        return jsonify(
            {
                "status": "game_data_invalid",
                "message": "Request JSON must include a 'games' list.",
                "current_year": current_year,
                "upcoming_games": [],
                "skipped_count": 0,
            }
        )

    games_raw = data.get("games")
    if not isinstance(games_raw, list):
        return jsonify(
            {
                "status": "game_data_invalid",
                "message": "'games' must be a list.",
                "current_year": current_year,
                "upcoming_games": [],
                "skipped_count": 0,
            }
        )

    upcoming: List[Dict[str, Any]] = []
    skipped = 0

    for game in games_raw:
        # Robustness: ensure each item is a dict
        if not isinstance(game, dict):
            skipped += 1
            continue

        # Extract and validate release_year
        year_value = game.get("release_year")
        year_int = _parse_int(year_value)
        if year_int is None:
            skipped += 1
            continue

        # Only include future releases
        if year_int > current_year:
            upcoming.append(game)
        else:
            # Valid data, just not an upcoming release
            pass

    if not upcoming:
        return jsonify(
            {
                "status": "no_upcoming_releases",
                "message": "No upcoming releases found after the current year.",
                "current_year": current_year,
                "upcoming_games": [],
                "skipped_count": skipped,
            }
        )

    return jsonify(
        {
            "status": "ok",
            "current_year": current_year,
            "upcoming_games": upcoming,
            "skipped_count": skipped,
        }
    )


@app.get("/health")
def health():

    return jsonify({"status": "up"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5003, debug=True)
