from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import timedelta
from data import GAMES

app = Flask(__name__)
app.secret_key = "dev-secret-change"
app.permanent_session_lifetime = timedelta(minutes=30)


def _get_cart():
    """Return the current cart from session, create if missing."""
    if "cart" not in session:
        session["cart"] = []
    return session["cart"]


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/games")
def games():
    # IH #7: Allow search OR browse
    query = request.args.get("q", "").lower()
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


@app.route("/games/<int:game_id>")
def game_details(game_id):
    game = next((g for g in GAMES if g["id"] == game_id), None)
    if not game:
        flash("Game not found.", "error")
        return redirect(url_for("games"))
    return render_template("game_details.html", game=game)


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


if __name__ == "__main__":
    app.run(debug=True) # I am using arch Linux, this will run on 127.0.0.1:5000 by default
