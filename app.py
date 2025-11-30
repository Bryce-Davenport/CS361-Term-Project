from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import timedelta
from data import GAMES, REVIEWS
import requests

app = Flask(__name__)
app.secret_key = "dev-secret-change"
app.permanent_session_lifetime = timedelta(minutes=30)


def _get_cart():
    """Return the current cart from session, create if missing."""
    if "cart" not in session:
        session["cart"] = []
    return session["cart"]


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
    # Show a Small Pool microservice announcement on the home page
    announcement = _get_random_announcement()
    return render_template("home.html", announcement=announcement)


@app.route("/games")
def games():
    # IH #7: Allow search OR browse
    query = request.args.get("query", "").lower()
    if query:
        filtered = [g for g in GAMES if query in g["title"].lower()]
    else:
        filtered = GAMES

    return render_template(
        "games.html",
        games=filtered,
        query=query,
        total=len(GAMES)
    )


# allow POST here so the form on the details page works
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
        cart.append({
            "id": game_id,
            "title": game["title"],
            "platform": platform,
            "price": game["price"]
        })
        session["cart"] = cart
        flash(f'Added "{game["title"]}" for {platform} to your cart.', "success")
        return redirect(url_for("cart"))

    ratings = REVIEWS.get(game_id, [])

    return render_template(
        "game_details.html",
        game=game,
        ratings=ratings
    )


@app.route("/cart/add", methods=["POST"])
def add_to_cart():
    game_id = int(request.form.get("game_id"))
    platform = request.form.get("platform", "").strip()

    game = next((g for g in GAMES if g["id"] == game_id), None)
    if not game:
        flash("Game not found.", "error")
        return redirect(url_for("games"))

    # IH #8: help tinkerers be careful
    if not platform:
        flash("Please select a platform before adding to cart.", "warning")
        return redirect(url_for("game_details", game_id=game_id))

    cart = _get_cart()
    cart.append({
        "id": game_id,
        "title": game["title"],
        "platform": platform,
        "price": game["price"]
    })
    session["cart"] = cart
    flash(f'Added "{game["title"]}" for {platform} to your cart.', "success")
    return redirect(url_for("cart"))


@app.route("/cart")
def cart():
    cart = _get_cart()
    total = sum(item["price"] for item in cart)
    return render_template("cart.html", cart=cart, total=total)


@app.route("/cart/remove", methods=["POST"])
def cart_remove():
    idx = int(request.form.get("index"))
    cart = _get_cart()
    if 0 <= idx < len(cart):
        removed = cart.pop(idx)
        session["cart"] = cart
        flash(f'Removed {removed["title"]} ({removed["platform"]})', "info")
    return redirect(url_for("cart"))


@app.route("/announcements")
def announcements():
    # Separate page that also shows a random announcement from the Small Pool microservice

    announcement = _get_random_announcement()
    return render_template("announcements.html", announcement=announcement)


if __name__ == "__main__":
    app.run(debug=True)  # will run on 127.0.0.1:5000 by default
