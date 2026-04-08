import os
import math

from flask import Flask, render_template, request, jsonify


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Feature names and dataset built from your examples.
FEATURE_NAMES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

CROP_SAMPLES = [
    # --- First set ---
    {"crop": "Rice", "N": 90, "P": 42, "K": 43, "temperature": 26, "humidity": 80, "ph": 6.5, "rainfall": 200},
    {"crop": "Maize", "N": 80, "P": 35, "K": 40, "temperature": 24, "humidity": 65, "ph": 6.0, "rainfall": 90},
    {"crop": "Wheat", "N": 70, "P": 40, "K": 45, "temperature": 20, "humidity": 60, "ph": 6.5, "rainfall": 75},
    {"crop": "Mango", "N": 20, "P": 15, "K": 25, "temperature": 30, "humidity": 50, "ph": 5.5, "rainfall": 80},
    {"crop": "Chickpea", "N": 40, "P": 60, "K": 20, "temperature": 22, "humidity": 45, "ph": 7.0, "rainfall": 60},
    {"crop": "Onion", "N": 50, "P": 40, "K": 35, "temperature": 25, "humidity": 70, "ph": 6.0, "rainfall": 100},
    {"crop": "Watermelon", "N": 60, "P": 50, "K": 50, "temperature": 28, "humidity": 65, "ph": 6.5, "rainfall": 85},
    {"crop": "Banana", "N": 100, "P": 60, "K": 50, "temperature": 27, "humidity": 85, "ph": 6.5, "rainfall": 220},
    {"crop": "Apple", "N": 20, "P": 125, "K": 200, "temperature": 21, "humidity": 90, "ph": 6.5, "rainfall": 110},
    {"crop": "Orange", "N": 20, "P": 10, "K": 10, "temperature": 24, "humidity": 70, "ph": 6.0, "rainfall": 90},
    {"crop": "Grapes", "N": 40, "P": 40, "K": 40, "temperature": 23, "humidity": 80, "ph": 6.5, "rainfall": 70},
    {"crop": "Coconut", "N": 30, "P": 20, "K": 40, "temperature": 27, "humidity": 90, "ph": 5.5, "rainfall": 250},
    {"crop": "Coffee", "N": 100, "P": 30, "K": 20, "temperature": 23, "humidity": 85, "ph": 6.0, "rainfall": 200},
    {"crop": "Cotton", "N": 120, "P": 50, "K": 40, "temperature": 25, "humidity": 60, "ph": 6.0, "rainfall": 80},
    {"crop": "Jute", "N": 80, "P": 40, "K": 40, "temperature": 27, "humidity": 85, "ph": 6.5, "rainfall": 180},
    {"crop": "Kidney Beans", "N": 20, "P": 60, "K": 20, "temperature": 21, "humidity": 60, "ph": 6.5, "rainfall": 60},
    {"crop": "Lentil", "N": 30, "P": 60, "K": 25, "temperature": 20, "humidity": 50, "ph": 7.0, "rainfall": 40},
    {"crop": "Mung Bean", "N": 25, "P": 50, "K": 20, "temperature": 28, "humidity": 60, "ph": 6.2, "rainfall": 85},
    {"crop": "Black Gram", "N": 40, "P": 50, "K": 30, "temperature": 30, "humidity": 65, "ph": 6.5, "rainfall": 75},
    # --- Second set ---
    {"crop": "Rice", "N": 92, "P": 45, "K": 42, "temperature": 27, "humidity": 82, "ph": 6.4, "rainfall": 210},
    {"crop": "Maize", "N": 78, "P": 38, "K": 40, "temperature": 25, "humidity": 64, "ph": 6.1, "rainfall": 95},
    {"crop": "Wheat", "N": 72, "P": 42, "K": 44, "temperature": 19, "humidity": 58, "ph": 6.6, "rainfall": 70},
    {"crop": "Chickpea", "N": 42, "P": 62, "K": 22, "temperature": 21, "humidity": 48, "ph": 7.1, "rainfall": 55},
    {"crop": "Kidney Beans", "N": 18, "P": 58, "K": 22, "temperature": 20, "humidity": 62, "ph": 6.4, "rainfall": 65},
    {"crop": "Lentil", "N": 28, "P": 65, "K": 30, "temperature": 18, "humidity": 50, "ph": 6.9, "rainfall": 40},
    {"crop": "Mung Bean", "N": 26, "P": 52, "K": 24, "temperature": 29, "humidity": 62, "ph": 6.3, "rainfall": 88},
    {"crop": "Black Gram", "N": 38, "P": 48, "K": 28, "temperature": 30, "humidity": 67, "ph": 6.6, "rainfall": 72},
    {"crop": "Pigeon Pea", "N": 36, "P": 56, "K": 22, "temperature": 28, "humidity": 63, "ph": 6.8, "rainfall": 92},
    {"crop": "Moth Beans", "N": 22, "P": 36, "K": 18, "temperature": 31, "humidity": 48, "ph": 7.0, "rainfall": 50},
    {"crop": "Banana", "N": 102, "P": 58, "K": 52, "temperature": 28, "humidity": 86, "ph": 6.6, "rainfall": 230},
    {"crop": "Apple", "N": 24, "P": 120, "K": 195, "temperature": 20, "humidity": 88, "ph": 6.7, "rainfall": 105},
    {"crop": "Orange", "N": 18, "P": 12, "K": 14, "temperature": 25, "humidity": 72, "ph": 6.1, "rainfall": 85},
    {"crop": "Grapes", "N": 42, "P": 42, "K": 45, "temperature": 24, "humidity": 78, "ph": 6.4, "rainfall": 75},
    {"crop": "Watermelon", "N": 65, "P": 55, "K": 48, "temperature": 29, "humidity": 67, "ph": 6.4, "rainfall": 90},
    {"crop": "Muskmelon", "N": 58, "P": 50, "K": 52, "temperature": 30, "humidity": 68, "ph": 6.5, "rainfall": 85},
    {"crop": "Mango", "N": 22, "P": 18, "K": 28, "temperature": 32, "humidity": 55, "ph": 5.6, "rainfall": 95},
    {"crop": "Coconut", "N": 34, "P": 24, "K": 45, "temperature": 28, "humidity": 92, "ph": 5.4, "rainfall": 260},
    {"crop": "Papaya", "N": 50, "P": 45, "K": 40, "temperature": 27, "humidity": 75, "ph": 6.3, "rainfall": 150},
    {"crop": "Coffee", "N": 95, "P": 35, "K": 25, "temperature": 24, "humidity": 87, "ph": 6.1, "rainfall": 210},
    {"crop": "Cotton", "N": 118, "P": 52, "K": 42, "temperature": 26, "humidity": 62, "ph": 6.2, "rainfall": 78},
    {"crop": "Jute", "N": 82, "P": 45, "K": 40, "temperature": 27, "humidity": 84, "ph": 6.4, "rainfall": 190},
    {"crop": "Lentil", "N": 32, "P": 68, "K": 26, "temperature": 19, "humidity": 52, "ph": 7.0, "rainfall": 45},
    {"crop": "Maize", "N": 84, "P": 40, "K": 38, "temperature": 26, "humidity": 66, "ph": 6.2, "rainfall": 100},
    {"crop": "Rice", "N": 95, "P": 48, "K": 44, "temperature": 28, "humidity": 85, "ph": 6.5, "rainfall": 215},
    {"crop": "Chickpea", "N": 44, "P": 64, "K": 24, "temperature": 23, "humidity": 50, "ph": 7.2, "rainfall": 58},
    {"crop": "Grapes", "N": 46, "P": 44, "K": 42, "temperature": 23, "humidity": 76, "ph": 6.3, "rainfall": 72},
    {"crop": "Orange", "N": 22, "P": 14, "K": 12, "temperature": 24, "humidity": 70, "ph": 6.0, "rainfall": 88},
    {"crop": "Watermelon", "N": 62, "P": 52, "K": 50, "temperature": 29, "humidity": 66, "ph": 6.5, "rainfall": 92},
    {"crop": "Coffee", "N": 98, "P": 32, "K": 22, "temperature": 24, "humidity": 84, "ph": 6.0, "rainfall": 205},
]


def _compute_feature_stats():
    stats = {name: {"min": float("inf"), "max": float("-inf")} for name in FEATURE_NAMES}
    for sample in CROP_SAMPLES:
        for name in FEATURE_NAMES:
            v = float(sample[name])
            if v < stats[name]["min"]:
                stats[name]["min"] = v
            if v > stats[name]["max"]:
                stats[name]["max"] = v
    # Avoid zero ranges
    for name in FEATURE_NAMES:
        if stats[name]["min"] == float("inf"):
            stats[name]["min"] = 0.0
        if stats[name]["max"] == float("-inf"):
            stats[name]["max"] = 1.0
        if stats[name]["max"] == stats[name]["min"]:
            stats[name]["max"] = stats[name]["min"] + 1.0
    return stats


FEATURE_STATS = _compute_feature_stats()


def _normalize_vector(vec):
    normed = []
    for i, name in enumerate(FEATURE_NAMES):
        v = float(vec[i])
        mn = FEATURE_STATS[name]["min"]
        mx = FEATURE_STATS[name]["max"]
        normed.append((v - mn) / (mx - mn))
    return normed


def _euclidean_distance(a, b):
    return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))


def recommend_crops(features, k=5):
    """
    K-nearest-neighbor style recommendation over the in-memory dataset.

    Returns (best_crop, ranked_crops) where ranked_crops is a list of
    dicts: {"crop": name, "count": n, "avg_distance": d}.
    """
    user_vec_norm = _normalize_vector(features)

    distances = []
    for sample in CROP_SAMPLES:
        sample_vec = [float(sample[name]) for name in FEATURE_NAMES]
        sample_vec_norm = _normalize_vector(sample_vec)
        dist = _euclidean_distance(user_vec_norm, sample_vec_norm)
        distances.append((dist, sample["crop"]))

    distances.sort(key=lambda x: x[0])
    neighbors = distances[: max(1, k)]

    by_crop = {}
    for dist, crop in neighbors:
        if crop not in by_crop:
            by_crop[crop] = {"crop": crop, "count": 0, "total_distance": 0.0}
        by_crop[crop]["count"] += 1
        by_crop[crop]["total_distance"] += dist

    ranked = []
    for crop, info in by_crop.items():
        ranked.append(
            {
                "crop": crop,
                "count": info["count"],
                "avg_distance": info["total_distance"] / info["count"],
            }
        )

    ranked.sort(key=lambda x: (-x["count"], x["avg_distance"]))
    best_crop = ranked[0]["crop"] if ranked else "Unknown"
    return best_crop, ranked


app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    """
    Render the main page with the input form.
    """
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    """
    Accept form or JSON data and return crop recommendation.

    Assumed feature order (adjust to match your model):
      - N: Nitrogen
      - P: Phosphorus
      - K: Potassium
      - temperature (°C)
      - humidity (%)
      - ph
      - rainfall (mm)
    """
    try:
        if request.is_json:
            data = request.get_json() or {}
        else:
            data = request.form or {}

        # Extract and convert features
        features = []
        for name in FEATURE_NAMES:
            value = data.get(name)
            if value is None or value == "":
                raise ValueError(f"Missing value for '{name}'")
            try:
                features.append(float(value))
            except ValueError:
                raise ValueError(f"Invalid numeric value for '{name}': {value}")

        # KNN-style recommendation against the built-in dataset
        best_crop, ranked_crops = recommend_crops(features, k=7)

        response = {
            "success": True,
            "prediction": str(best_crop),
            "ranked": ranked_crops,
        }

        if request.is_json:
            return jsonify(response)

        # For form POST, re-render the page with the result
        return render_template(
            "index.html",
            prediction=response["prediction"],
            ranked=response["ranked"],
            form_values=data,
        )

    except Exception as e:
        error_msg = str(e)
        if request.is_json:
            # For API clients, keep the 400 status code.
            return jsonify({"success": False, "error": error_msg}), 400
        # For browser form submissions, return a normal 200 so the
        # page renders instead of showing a generic "400" error screen.
        return render_template("index.html", error=error_msg, form_values=request.form), 200


if __name__ == "__main__":
    # Allow overriding port via environment variable, default to 5000
    port = int(os.environ.get("PORT", 5002))
    app.run(host="0.0.0.0", port=port, debug=True)

