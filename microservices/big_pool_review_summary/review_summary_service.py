from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/rating-summary", methods=["POST"])
def rating_summary():

    try:
        data = request.get_json(silent=True) or {}
        ratings = data.get("ratings", None)

        if ratings is None or not isinstance(ratings, list):        # validates data format
            return jsonify({
                "status": "rating_data_invalid",
                "message": "Request JSON must include a 'ratings' list.",
                "average_rating": None,
                "review_count": 0
            }), 200


        if len(ratings) == 0: # check if empty
            return jsonify({
                "status": "no_rating_yet",
                "message": "No ratings provided.",
                "average_rating": None,
                "review_count": 0
            }), 200

        # Convert to floats and keep only values in [1.0, 5.0]
        numeric_ratings = []
        for r in ratings:
            try:
                value = float(r)
            except (TypeError, ValueError): #checks if numeric 
                continue

            if 1.0 <= value <= 5.0: #checkis if in range
                numeric_ratings.append(value)
            else:
                continue

        if not numeric_ratings:
            return jsonify({
                "status": "rating_data_invalid",
                "message": "No valid numeric ratings in range 1.0–5.0.",
                "average_rating": None,
                "review_count": 0
            }), 200

        # Compute average (rounded to one decimal place)
        review_count = len(numeric_ratings)
        avg = sum(numeric_ratings) / review_count
        avg_rounded = round(avg, 1)

        return jsonify({
            "status": "ok",
            "average_rating": avg_rounded,
            "review_count": review_count
        }), 200

    except Exception as e:
        # Reliability / robustness: fail gracefully
        return jsonify({
            "status": "no_rating_available",
            "message": "The review summary service failed safely.",
            "average_rating": None,
            "review_count": 0
        }), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=True)