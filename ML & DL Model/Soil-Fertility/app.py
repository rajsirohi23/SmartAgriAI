from flask import Flask, render_template, request
import pickle
import numpy as np
import pandas as pd
import os

app = Flask(__name__)

# --------- CONFIG: UPDATE TO MATCH YOUR MODEL ---------
# Path to your trained model
MODEL_PATH = os.path.join("models", "soil_model.pkl")

# How to interpret model output.
# Example: 1 = Fertile, 0 = Not Fertile
LABEL_MAPPING = {
    # 0: "Not Fertile",
    # 1: "Fertile",
}
# ------------------------------------------------------


def load_model(model_path: str):
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    return model


model = load_model(MODEL_PATH)

# Try to read the exact feature names the model was trained with.
# This avoids mismatches like "Feature names should match those that were passed during fit".
if hasattr(model, "feature_names_in_"):
    FEATURE_COLUMNS = list(model.feature_names_in_)
else:
    # Fallback: keep a default list (update if needed)
    FEATURE_COLUMNS = [
        "N",
        "P",
        "K",
        "pH",
        "EC",
        "OC",
        "S",
    ]


def analyze_nutrient_status(features: dict):
    """
    Farmer‑friendly rule-based analysis.
    Returns:
        issues: list of things that may limit soil fertility
        strengths: list of things that are in a good/healthy range
        overview: short text summary of overall soil health
    Thresholds are generic and should be tuned to local guidelines.
    """
    issues = []
    strengths = []
    low_count = 0

    # --- Macronutrients ---
    n = features.get("N")
    if n is not None:
        if n < 80:
            low_count += 1
            issues.append({
                "name": "Nitrogen (N)",
                "status": "Low",
                "detail": "Nitrogen appears below the comfortable range. Gradual addition of nitrogen sources or organic matter can support better growth over time."
            })
        elif n > 200:
            issues.append({
                "name": "Nitrogen (N)",
                "status": "High",
                "detail": "Nitrogen level is high. Avoid heavy nitrogen additions to reduce losses and protect soil life."
            })
        else:
            strengths.append("Nitrogen is within a generally healthy range for most soils.")

    p = features.get("P")
    if p is not None:
        if p < 20:
            low_count += 1
            issues.append({
                "name": "Phosphorus (P)",
                "status": "Low",
                "detail": "Phosphorus is on the lower side. Balanced phosphorus management, based on lab guidance, can help root development and energy transfer."
            })
        elif p > 60:
            issues.append({
                "name": "Phosphorus (P)",
                "status": "High",
                "detail": "Phosphorus is high. Avoid unnecessary additions to prevent build‑up in the soil."
            })
        else:
            strengths.append("Phosphorus level looks comfortable for many field situations.")

    k = features.get("K")
    if k is not None:
        if k < 120:
            low_count += 1
            issues.append({
                "name": "Potassium (K)",
                "status": "Low",
                "detail": "Potassium is a bit low. Where recommended, improving potassium can help overall plant strength and stress tolerance."
            })
        elif k > 300:
            issues.append({
                "name": "Potassium (K)",
                "status": "High",
                "detail": "Potassium is on the higher side. Further heavy applications are usually not needed."
            })
        else:
            strengths.append("Potassium appears to be in a workable range.")

    # --- Soil reaction and salinity ---
    ph = features.get("pH")
    if ph is not None:
        if ph < 6.0:
            low_count += 1
            issues.append({
                "name": "pH",
                "status": "Acidic",
                "detail": "Soil is moderately acidic. Liming and organic matter management are often used to move towards a near‑neutral pH where nutrients are more available."
            })
        elif ph > 7.8:
            low_count += 1
            issues.append({
                "name": "pH",
                "status": "Alkaline",
                "detail": "Soil is on the alkaline side. Managing salts and adding organic matter can help nutrient availability."
            })
        else:
            strengths.append("pH is close to neutral, which usually supports good nutrient availability.")

    ec = features.get("EC")
    if ec is not None:
        if ec > 2.0:
            issues.append({
                "name": "Electrical Conductivity (EC)",
                "status": "High",
                "detail": "Electrical conductivity is higher than normal. This can indicate salt build‑up; careful water and nutrient management is important."
            })
        else:
            strengths.append("Salinity (EC) is not showing major concern in this quick check.")

    oc = features.get("OC")
    if oc is not None:
        if oc < 0.5:
            low_count += 1
            issues.append({
                "name": "Organic Carbon (OC)",
                "status": "Low",
                "detail": "Organic carbon is low. Building organic matter (through residues, manures, or cover where appropriate) can gradually improve structure, water holding, and nutrient buffering."
            })
        elif oc > 0.9:
            strengths.append("Organic carbon is relatively high, which usually supports good soil structure and life.")
        else:
            strengths.append("Organic carbon is moderate; continuing to add organic inputs will help maintain or improve it.")

    s = features.get("S")
    if s is not None:
        if s < 10:
            low_count += 1
            issues.append({
                "name": "Sulphur (S)",
                "status": "Low",
                "detail": "Sulphur level is slightly low. Where recommended, balanced sulphur inputs can support protein formation and quality."
            })
        else:
            strengths.append("Sulphur is not showing a strong deficiency signal in this check.")

    # --- Micronutrients (only if present in data) ---
    b = features.get("B")
    if b is not None:
        if b < 0.5:
            low_count += 1
            issues.append({
                "name": "Boron (B)",
                "status": "Low",
                "detail": "Boron is on the lower side. Small, carefully managed additions are often used where lab reports confirm deficiency."
            })
        else:
            strengths.append("Boron is not showing strong deficiency in this test.")

    cu = features.get("Cu")
    if cu is not None:
        if cu < 0.2:
            low_count += 1
            issues.append({
                "name": "Copper (Cu)",
                "status": "Low",
                "detail": "Copper is a bit low. It is usually managed with small, well‑controlled doses where required."
            })
        else:
            strengths.append("Copper is within a workable range.")

    fe = features.get("Fe")
    if fe is not None:
        if fe < 4.5:
            low_count += 1
            issues.append({
                "name": "Iron (Fe)",
                "status": "Low",
                "detail": "Iron is low in this test. Iron availability is also strongly affected by pH and organic matter."
            })
        else:
            strengths.append("Iron level looks adequate in this quick view.")

    mn = features.get("Mn")
    if mn is not None:
        if mn < 2.0:
            low_count += 1
            issues.append({
                "name": "Manganese (Mn)",
                "status": "Low",
                "detail": "Manganese is on the lower side. Its availability is sensitive to pH and drainage; management should follow detailed lab recommendations."
            })
        else:
            strengths.append("Manganese does not show a strong deficiency signal.")

    zn = features.get("Zn")
    if zn is not None:
        if zn < 0.6:
            low_count += 1
            issues.append({
                "name": "Zinc (Zn)",
                "status": "Low",
                "detail": "Zinc is low in this test. Where lab reports confirm, small zinc applications are usually recommended."
            })
        else:
            strengths.append("Zinc appears adequate in this sample.")

    # --- Overall message for farmers ---
    if not issues:
        overview = "This sample looks generally well‑balanced in this quick check. Continue current good practices and monitor with periodic soil testing."
    elif low_count <= 2 and len(issues) <= 3:
        overview = "The soil shows mostly healthy conditions with a few areas that can be improved. Focusing on the listed nutrients and organic matter will help maintain good fertility."
    else:
        overview = "The soil shows several factors that may limit performance. Addressing the low nutrients and improving organic matter step by step, with guidance from detailed lab reports, will steadily improve fertility."

    return issues, strengths, overview


@app.route("/", methods=["GET", "POST"])
def index():
    prediction_label = None
    prediction_raw = None
    probability = None
    nutrient_issues = []
    nutrient_strengths = []
    overview_message = None
    input_values = {}
    error_message = None

    if request.method == "POST":
        try:
            # Collect inputs from form and convert to float
            for col in FEATURE_COLUMNS:
                val_str = request.form.get(col)
                if val_str is None or val_str.strip() == "":
                    raise ValueError(f"Missing value for {col}")
                input_values[col] = float(val_str)

            # Prepare data for model
            X = pd.DataFrame([input_values], columns=FEATURE_COLUMNS)

            # Model prediction
            y_pred = model.predict(X)[0]
            prediction_raw = int(y_pred) if hasattr(y_pred, "item") else y_pred
            prediction_label = LABEL_MAPPING.get(prediction_raw, str(prediction_raw))

            # Optional: probability/confidence if classifier supports predict_proba
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(X)[0]
                # Assume binary: probability of the "fertile" class (label 1)
                if 1 in LABEL_MAPPING:
                    fertile_index = list(model.classes_).index(1)
                    probability = float(proba[fertile_index])
                else:
                    probability = float(max(proba))

            # Rule-based analysis of nutrient status
            nutrient_issues, nutrient_strengths, overview_message = analyze_nutrient_status(input_values)

        except Exception as e:
            error_message = f"Error while processing input: {e}"

    return render_template(
        "index.html",
        feature_columns=FEATURE_COLUMNS,
        prediction_label=prediction_label,
        prediction_raw=prediction_raw,
        probability=probability,
        nutrient_issues=nutrient_issues,
        nutrient_strengths=nutrient_strengths,
        overview_message=overview_message,
        input_values=input_values,
        error_message=error_message,
    )


if __name__ == "__main__":
    # For local dev; in production use gunicorn/uwsgi, etc.
    app.run(host="0.0.0.0", port=5001, debug=True)