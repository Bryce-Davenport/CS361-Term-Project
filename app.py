from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime, timedelta
from pathlib import Path
import requests

from data import GAMES, REVIEWS

app = Flask(__name__)
app.secret_key = "dev-secret-change"
app.permanent_session_lifetime = timedelta(minutes=30)


def _get_cart(): # Return the current cart from session, create if missing.
    if "cart" not in session:
        session["cart"] = []
    return session["cart"]

def _check_service_via_ping(name: str, ip: str, port: int, endpoint: str) -> dict: # Big Pool ms 4

    payload = {
        "ip": ip,
        "port": port,
        "endpoint": endpoint,
    }

    try:
        resp = requests.post(
            "http://127.0.0.1:5004/check",  # Server Ping microservice
            json=payload,
            timeout=3,
        )
        resp.raise_for_status()
        result = resp.json()  # expected to be a JSON boolean
        online = bool(result)
    except Exception: # If the ping service itself is down or errors, treat as offline.
        online = False

    return {
        "name": name,
        "ip": ip,
        "port": port,
        "endpoint": endpoint,
        "online": online,
    }


def _get_random_announcement():
    
    # Call the Small Pool Random Notification microservice and return one announcement string for the UI.
    announcements_path = "data/announcements.json"

    try:
        with open(announcements_path, "rb") as f:
            files = {
                "file": ("announcements.json", f, "application/json")
            }

            resp = requests.post(
                "http://localhost:5001/random-announcement",  # microservice port
                files=files,
                timeout=5
            )

        resp.raise_for_status()
        data = resp.json()
        return data.get("announcement", "Welcome to Catalyst Games!")

    except Exception as e:
        # Fallback message if the microservice is down
        return f"Welcome to Catalyst Games! (Notification service error: {e})"


@app.route("/")
def home():
    announcement_text = _get_random_announcement()
    return render_template("home.html", announcement=announcement_text)


@app.route("/games", methods=["GET"]) # browse or search
def games():
    """Browse or search the game library."""
    query = request.args.get("query", "").strip().lower()

    if query:
        filtered = [g for g in GAMES if query in g["title"].lower()]
    else:
        filtered = GAMES

    return render_template("games.html", games=filtered, query=query)


@app.route("/games/<int:game_id>", methods=["GET", "POST"])
def game_details(game_id):

    game = next((g for g in GAMES if g["id"] == game_id), None)
    if not game:
        flash("Game not found.", "error")
        return redirect(url_for("games"))

    if request.method == "POST":
        platform = request.form.get("platform", "").strip()

        # IH #8: help tinkerers be careful
        if not platform:
            flash("Please select a platform before adding to cart.", "warning")
            return redirect(url_for("game_details", game_id=game_id))

        cart = _get_cart()
        cart.append(
            {
                "id": game_id,
                "title": game["title"],
                "platform": platform,
                "price": game["price"],
            }
        )
        session["cart"] = cart
        flash(f'Added "{game["title"]}" for {platform} to your cart.', "success")
        return redirect(url_for("cart"))

    # ---- Local ratings data for this game ----
    ratings = REVIEWS.get(game_id, [])

    # ---- Call Review Summary Microservice over HTTP ----
    avg_rating = None
    review_count = 0

    try:
        resp = requests.post(
            "http://127.0.0.1:5002/rating-summary",
            json={"ratings": ratings},
            timeout=3,
        )
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status")

        if status == "ok":
            avg_rating = data.get("average_rating")
            review_count = data.get("review_count", 0)
        elif status in ("no_rating_yet", "rating_data_invalid", "no_rating_available"):
            avg_rating = None
            review_count = 0

    except Exception:
        # Reliability: if the microservice is down/slow, fail safely
        avg_rating = None
        review_count = 0

    return render_template(
        "game_details.html",
        game=game,
        ratings=ratings,
        avg_rating=avg_rating,
        review_count=review_count,
    )


@app.route("/cart")
def cart():
    """View current cart contents."""
    cart = _get_cart()
    total = sum(item["price"] for item in cart)
    return render_template("cart.html", cart=cart, total=total)


@app.route("/cart/remove", methods=["POST"])
def cart_remove():
    """Remove an item from the cart by index."""
    idx_raw = request.form.get("index", "").strip()
    try:
        idx = int(idx_raw)
    except ValueError:
        idx = -1

    cart = _get_cart()
    if 0 <= idx < len(cart):
        removed = cart.pop(idx)
        session["cart"] = cart
        flash(f'Removed {removed["title"]} ({removed["platform"]})', "info")
    else:
        flash("Could not remove that item from the cart.", "error")

    return redirect(url_for("cart"))


@app.route("/announcements") # Small Pool MS #1
def announcements():

    announcements_path = Path("data") / "announcements.json"
    announcement_text = None

    try:
        with announcements_path.open("rb") as f:
            files = {
                "file": (
                    "announcements.json",
                    f,
                    "application/json",
                )
            }

            resp = requests.post(
                "http://127.0.0.1:5001/random-announcement",
                files=files,
                timeout=3,
            )
        resp.raise_for_status()
        data = resp.json()
        announcement_text = data.get("announcement")

    except Exception:
        # Fail gracefully 
        announcement_text = (
            "Announcements are currently unavailable. "
            "Please check back again later."
        )

    return render_template("announcements.html", announcement=announcement_text)

@app.route("/upcoming", methods=["GET"]) # Big Pool MS #2
def upcoming():
    try:
        resp = requests.post(
            "http://127.0.0.1:5003/upcoming-releases",
            json={"games": GAMES},
            timeout=3,
        )
        data = resp.json()
    except Exception:
        data = {
            "status": "service_unavailable",
            "current_year": datetime.now().year,
            "upcoming_games": [],
            "skipped_count": 0,
        }

    return render_template(
        "upcoming.html",
        status=data.get("status"),
        current_year=data.get("current_year"),
        upcoming_games=data.get("upcoming_games", []),
    )

@app.route("/service-status", methods=["GET"]) #Big Pool MS #3
def service_status():
    targets = [
        {
            "name": "Random Announcement Service",
            "ip": "127.0.0.1",                "port": 5001,
            "endpoint": "random-announcement",
        },
        {
            "name": "Review Summary Service",
            "ip": "127.0.0.1",
            "port": 5002,
            "endpoint": "rating-summary",
        },
        {
            "name": "Upcoming Releases Service",
            "ip": "127.0.0.1",
            "port": 5003,
            "endpoint": "upcoming-releases",
        },
    ]

    services = [
        _check_service_via_ping(
            t["name"], t["ip"], t["port"], t["endpoint"]
        )
        for t in targets
    ]
    return render_template("service_status.html", services=services)

if __name__ == "__main__":
    app.run(debug=True)  # runs on 127.0.0.1:5000 by default
