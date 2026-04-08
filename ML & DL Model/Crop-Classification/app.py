




# """
# CropMD – Crop Disease Detection  (app.py)
# ==========================================
# Architecture
# ------------
#   Primary  : VGG16-based deep model  (vgg16_crop_model.h5)
#   Secondary : Pixel-feature engine   (colour, texture, spot-detection)
#   Validation: Human/object guard      (MobileNetV2 top-5)

# If the deep model returns confidence < MIN_DL_CONFIDENCE the pixel engine
# takes over, so every image gets a *distinct*, evidence-based diagnosis.
# """

# import os
# import math
# from uuid import uuid4
# import gdown

# import cv2
# import numpy as np
# from PIL import Image

# from flask import Flask, render_template, request, redirect, url_for, flash


# os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# # import tensorflow as tf
# # from tensorflow.keras.models import load_model
# # from tensorflow.keras.applications.mobilenet_v2 import (
# #     MobileNetV2,
# #     preprocess_input as mobilenet_preprocess,
# #     decode_predictions,
# # )



# # # ═══════════════════════════════════════════════════
# # #  CONFIGURATION
# # # ═══════════════════════════════════════════════════
# # BASE_DIR      = os.path.abspath(os.path.dirname(__file__))
# # MODEL_PATH    = os.path.join(BASE_DIR, "vgg16_crop_model.h5")
# # UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
# # ALLOWED_EXT   = {"png", "jpg", "jpeg", "JPG", "PNG", "JPEG"}


# # ═══════════════════════════════════════════════════
# # CONFIGURATION
# # ═══════════════════════════════════════════════════
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# MODEL_PATH = os.path.join(BASE_DIR, "vgg16_crop_model.h5")

# UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
# ALLOWED_EXT = {"png", "jpg", "jpeg", "JPG", "PNG", "JPEG"}

# # Google Drive model link
# MODEL_URL = "https://drive.google.com/uc?id=1pfJ0FnBK4jcWIeHYs1u0JxpIRGGbzUCq"

# # ✅ Download model if not exists
# if not os.path.exists(MODEL_PATH):
#     print("[CropMD] Downloading model from Google Drive...")
#     gdown.download(MODEL_URL, MODEL_PATH, quiet=False)


# # Below this confidence the pixel engine is used instead of the deep model
# MIN_DL_CONFIDENCE = 45.0   # percent

# app = Flask(__name__)
# app.config["SECRET_KEY"]    = "cropmd_2024_secret"
# app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# # ═══════════════════════════════════════════════════
# #  LOAD MODELS ONCE AT STARTUP
# # ═══════════════════════════════════════════════════
# print("[CropMD] Loading crop-disease model ...")
# try:
#     crop_model = load_model(MODEL_PATH, compile=False)
#     print("[CropMD] Crop-disease model loaded OK")
#     DEEP_MODEL_AVAILABLE = True
# except Exception as e:
#     print(f"[CropMD] WARNING – could not load crop model: {e}")
#     crop_model = None
#     DEEP_MODEL_AVAILABLE = False

# print("[CropMD] Loading MobileNetV2 scene detector ...")
# detector = MobileNetV2(weights="imagenet")
# print("[CropMD] MobileNetV2 loaded OK")

# # ═══════════════════════════════════════════════════
# #  CLASS NAMES  (must match training label order)
# # ═══════════════════════════════════════════════════
# CLASS_NAMES = [
#     "Apple Black Rot",        "Apple Healthy",         "Apple Cedar Rust",    "Apple Scab",
#     "Blueberry Healthy",
#     "Cherry Powdery Mildew",  "Cherry Healthy",
#     "Corn Cercospora",        "Corn Rust",              "Corn Healthy",
#     "Grape Black Rot",        "Grape Esca",             "Grape Leaf Blight",   "Grape Healthy",
#     "Orange Citrus Greening",
#     "Peach Bacterial Spot",   "Peach Healthy",
#     "Pepper Bacterial Spot",  "Pepper Healthy",
#     "Potato Early Blight",    "Potato Late Blight",     "Potato Healthy",
#     "Raspberry Healthy",
#     "Soybean Healthy",
#     "Squash Powdery Mildew",
#     "Strawberry Leaf Scorch", "Strawberry Healthy",
#     "Tomato Bacterial Spot",  "Tomato Early Blight",    "Tomato Late Blight",
#     "Tomato Leaf Mold",       "Tomato Septoria",        "Tomato Spider Mites",
#     "Tomato Target Spot",     "Tomato Mosaic Virus",    "Tomato Yellow Curl Virus",
#     "Tomato Healthy",
# ]

# # ═══════════════════════════════════════════════════
# #  TREATMENT DATABASE
# # ═══════════════════════════════════════════════════
# TREATMENT = {
#     "Black Rot":
#         "Remove and destroy infected leaves/fruit immediately. "
#         "Apply mancozeb or copper-based fungicide every 7–10 days. "
#         "Prune to improve air circulation.",
#     "Cedar Rust":
#         "Apply myclobutanil or propiconazole at bud break. "
#         "Remove nearby juniper/cedar host trees where possible.",
#     "Scab":
#         "Apply captan, myclobutanil, or sulfur at first sign. "
#         "Avoid overhead irrigation. Rake and destroy fallen leaves.",
#     "Powdery Mildew":
#         "Spray potassium bicarbonate, sulfur, or neem oil. "
#         "Improve canopy airflow. Avoid excessive nitrogen fertiliser.",
#     "Cercospora":
#         "Apply chlorothalonil, azoxystrobin, or propiconazole. "
#         "Rotate crops every 2–3 years. Remove all crop debris after harvest.",
#     "Rust":
#         "Use mancozeb, propiconazole, or tebuconazole. "
#         "Scout fields regularly. Plant resistant varieties where available.",
#     "Esca":
#         "No chemical cure. Prune infected wood during dry weather "
#         "and seal pruning wounds. Avoid water stress.",
#     "Leaf Blight":
#         "Remove infected leaves. Apply copper fungicide preventively "
#         "before wet weather. Improve field drainage.",
#     "Citrus Greening":
#         "No cure – remove and destroy infected trees immediately. "
#         "Apply systemic insecticide to control Asian citrus psyllid vector.",
#     "Bacterial Spot":
#         "Apply copper hydroxide or copper oxychloride bactericide. "
#         "Avoid overhead irrigation. Do not work in wet fields.",
#     "Early Blight":
#         "Apply chlorothalonil or mancozeb at first symptom. "
#         "Mulch around plant base. Remove lower infected leaves.",
#     "Late Blight":
#         "Apply metalaxyl + mancozeb or cymoxanil immediately. "
#         "Destroy infected plants; do NOT compost. Increase plant spacing.",
#     "Leaf Mold":
#         "Improve greenhouse ventilation; reduce humidity below 85%. "
#         "Apply copper or chlorothalonil fungicide.",
#     "Septoria":
#         "Apply chlorothalonil, copper fungicide, or azoxystrobin. "
#         "Remove infected lower leaves. Avoid prolonged leaf wetness.",
#     "Spider Mites":
#         "Apply neem oil, abamectin, or bifenazate miticide. "
#         "Keep plants well-watered. Introduce predatory mites (Phytoseiidae).",
#     "Mosaic Virus":
#         "No cure – remove and destroy infected plants immediately. "
#         "Control aphid vectors with insecticides or reflective mulches.",
#     "Target Spot":
#         "Apply azoxystrobin, fluxapyroxad, or chlorothalonil at first sign. "
#         "Improve air circulation between plants.",
#     "Yellow Curl Virus":
#         "No cure – remove infected plants promptly. "
#         "Control whitefly vectors with imidacloprid or reflective mulches.",
#     "Leaf Scorch":
#         "Improve soil drainage and irrigation consistency. "
#         "Apply balanced NPK fertiliser. Remove and destroy scorched leaves.",
# }

# # ═══════════════════════════════════════════════════
# #  SCENE DETECTION  (human / object guard)
# # ═══════════════════════════════════════════════════
# HUMAN_LABELS = {
#     "person","man","woman","boy","girl","face","head",
#     "suit","jersey","groom","bridegroom","people",
# }
# OBJECT_LABELS = {
#     "car","truck","bus","airplane","bicycle","motorcycle",
#     "phone","laptop","keyboard","mouse","remote","television","monitor",
#     "chair","table","sofa","bed","desk","shelf",
#     "bottle","cup","fork","knife","spoon","bowl",
#     "dog","cat","bird","horse","cow","sheep",
#     "backpack","umbrella","handbag","tie","book","clock",
# }


# def detect_scene(image):
#     """Returns 'human' | 'object' | 'plant' | 'unknown'."""
#     img = image.resize((224, 224)).convert("RGB")
#     arr = mobilenet_preprocess(
#         np.expand_dims(np.array(img, dtype=np.float32), 0)
#     )
#     preds   = detector.predict(arr, verbose=0)
#     decoded = decode_predictions(preds, top=5)[0]
#     print("[CropMD] MobileNet top-5:", [(d[1], round(float(d[2]), 3)) for d in decoded])

#     for _, label, conf in decoded:
#         if any(h in label.lower() for h in HUMAN_LABELS) and conf > 0.20:
#             return "human"
#     for _, label, conf in decoded:
#         if any(o in label.lower() for o in OBJECT_LABELS) and conf > 0.20:
#             return "object"

#     plant_kw = [
#         "leaf","plant","flower","grass","herb","tree","corn","cabbage",
#         "strawberry","mushroom","vegetable","broccoli","artichoke",
#         "cauliflower","fig","banana","mango","guava",
#     ]
#     for _, label, conf in decoded:
#         if any(p in label.lower() for p in plant_kw) and conf > 0.08:
#             return "plant"

#     return "unknown"


# # ═══════════════════════════════════════════════════
# #  PIXEL-FEATURE ENGINE
# # ═══════════════════════════════════════════════════

# def _count_circular_spots(img_bgr, hsv, min_area=30, max_area=2000):
#     """Count circular brown/dark lesions (Black Rot, Blight, etc.)."""
#     mask = cv2.inRange(hsv, np.array([0, 30, 20]), np.array([30, 255, 180]))
#     k    = np.ones((3, 3), np.uint8)
#     mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)
#     mask = cv2.dilate(mask, k, iterations=1)
#     cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     count = 0
#     for c in cnts:
#         area  = cv2.contourArea(c)
#         perim = cv2.arcLength(c, True)
#         if min_area < area < max_area and perim > 0:
#             if 4 * math.pi * area / perim ** 2 > 0.28:
#                 count += 1
#     return count


# def extract_pixel_features(image):
#     """Return a dict of colour, texture, morphology features."""
#     img_np  = np.array(image.convert("RGB"))
#     img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
#     hsv     = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
#     gray    = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

#     h_ch, s_ch = hsv[:, :, 0].astype(float), hsv[:, :, 1].astype(float)
#     R, G, B     = (img_np[:, :, i].astype(float) for i in range(3))
#     total       = float(R.size)

#     green_dom  = np.sum((G > R) & (G > B) & (G > 40)) / total
#     green_hue  = np.sum((h_ch >= 35) & (h_ch <= 85)) / total
#     yellow_hue = np.sum((h_ch >= 20) & (h_ch <  35)) / total
#     brown_hue  = np.sum((h_ch >= 5)  & (h_ch <  20) & (s_ch > 40)) / total
#     mean_sat   = s_ch.mean()

#     lesion_mask  = cv2.inRange(hsv, np.array([5, 40, 40]), np.array([22, 255, 220]))
#     lesion_ratio = lesion_mask.sum() / (255.0 * total)

#     dark_ratio   = np.sum((R < 80) & (G < 80) & (B < 80)) / total
#     lap_var      = cv2.Laplacian(gray, cv2.CV_64F).var()

#     edges = cv2.Canny(gray, 30, 100)
#     lines = cv2.HoughLinesP(edges, 1, np.pi / 180,
#                              threshold=20, minLineLength=30, maxLineGap=10)
#     streak_count   = len(lines) if lines is not None else 0
#     circular_spots = _count_circular_spots(img_bgr, hsv)

#     return {
#         "green_dom":      green_dom,
#         "green_hue":      green_hue,
#         "yellow_hue":     yellow_hue,
#         "brown_hue":      brown_hue,
#         "lesion_ratio":   lesion_ratio,
#         "dark_ratio":     dark_ratio,
#         "mean_sat":       mean_sat,
#         "lap_var":        lap_var,
#         "streak_count":   streak_count,
#         "circular_spots": circular_spots,
#     }


# def classify_by_pixels(f):
#     """
#     Rule-based classification from pixel features.
#     Returns (status, label, confidence_percent).
#     status in {"invalid","diseased","healthy","uncertain"}
#     """
#     # ── Invalid / non-leaf ───────────────────────────────────────
#     if f["yellow_hue"] > 0.50 and f["mean_sat"] > 140:
#         return "invalid", "Not a crop leaf — grain, flower, or other non-leaf material detected", 95.0
#     if f["green_dom"] < 0.05 and f["mean_sat"] < 40:
#         return "invalid", "No leaf detected — please upload a clear photograph of a single crop leaf", 90.0

#     # ── Disease rules  (most-specific first) ────────────────────

#     # Citrus Greening / HLB
#     if f["brown_hue"] > 0.50 and f["lesion_ratio"] > 0.60 and f["green_dom"] < 0.15:
#         return "diseased", "Orange Citrus Greening", 88.0

#     # Potato Late Blight: extensive necrosis, brown+yellow
#     if f["lesion_ratio"] > 0.25 and f["brown_hue"] > 0.15 and f["yellow_hue"] > 0.15:
#         return "diseased", "Potato Late Blight", 85.0

#     # Corn Cercospora: elongated parallel streaks
#     if f["streak_count"] > 15 and f["green_hue"] > 0.45 and f["yellow_hue"] > 0.15:
#         return "diseased", "Corn Cercospora", 82.0

#     # Cherry Powdery Mildew: low Laplacian var (coating), dark leaf base
#     if f["lap_var"] < 600 and f["dark_ratio"] > 0.15 and f["green_dom"] > 0.30:
#         return "diseased", "Cherry Powdery Mildew", 80.0

#     # Grape Black Rot: many small circular spots on green leaf
#     if f["circular_spots"] >= 6 and f["green_dom"] > 0.35:
#         return "diseased", "Grape Black Rot", 81.0

#     # Tomato Yellow Leaf Curl Virus: low green, low saturation, no brown
#     if f["green_dom"] < 0.30 and f["mean_sat"] < 60 and \
#        f["lesion_ratio"] < 0.05 and f["brown_hue"] < 0.05:
#         return "diseased", "Tomato Yellow Curl Virus", 78.0

#     # Strawberry Leaf Scorch: lesions on predominantly green leaf
#     if f["lesion_ratio"] > 0.06 and f["green_dom"] > 0.60:
#         return "diseased", "Strawberry Leaf Scorch", 75.0

#     # ── Healthy ─────────────────────────────────────────────────
#     if (f["green_dom"] > 0.25 and f["lesion_ratio"] < 0.08 and
#             f["brown_hue"] < 0.05 and f["circular_spots"] < 6):
#         return "healthy", "Healthy Leaf", 85.0

#     # ── Uncertain ───────────────────────────────────────────────
#     return "uncertain", "Cannot determine with confidence — consult an agricultural expert", 30.0


# # ═══════════════════════════════════════════════════
# #  DEEP-MODEL PREPROCESSING
# # ═══════════════════════════════════════════════════
# def preprocess_for_dl(image):
#     img = image.convert("RGB").resize((224, 224))
#     arr = np.array(img, dtype=np.float32) / 255.0
#     return np.expand_dims(arr, 0)


# # ═══════════════════════════════════════════════════
# #  RESULT BUILDER  →  dict consumed by template
# # ═══════════════════════════════════════════════════
# def build_result(status, label, confidence, source="model"):
#     """Build the interpretation dict passed to the Jinja template."""

#     if status == "invalid":
#         return {
#             "headline":   "Invalid Image",
#             "status":     "invalid",
#             "disease":    None,
#             "advice":     label,
#             "confidence": round(confidence, 1),
#             "source":     source,
#         }

#     if status == "uncertain":
#         return {
#             "headline":   "Low Confidence — Cannot Determine",
#             "status":     "uncertain",
#             "disease":    None,
#             "advice":     (
#                 f"Model confidence is only {confidence:.1f}% "
#                 f"(threshold {MIN_DL_CONFIDENCE:.0f}%). "
#                 "Please upload a clearer, well-lit photograph of a single leaf "
#                 "against a plain background, or consult an agricultural expert."
#             ),
#             "confidence": round(confidence, 1),
#             "source":     source,
#         }

#     if status == "healthy":
#         crop = label.replace(" Healthy", "").replace("Healthy Leaf", "Crop")
#         return {
#             "headline":   f"{crop} — Healthy",
#             "status":     "healthy",
#             "disease":    None,
#             "advice":     (
#                 "No disease detected. "
#                 "Maintain proper irrigation, balanced nutrition, and regular scouting."
#             ),
#             "confidence": round(confidence, 1),
#             "source":     source,
#         }

#     # Diseased
#     parts   = label.split(" ", 1)
#     crop    = parts[0]
#     disease = parts[1] if len(parts) > 1 else label
#     advice  = "Consult an agricultural extension officer for localised treatment advice."
#     for key, treatment in TREATMENT.items():
#         if key.lower() in disease.lower():
#             advice = treatment
#             break

#     return {
#         "headline":   f"{crop} — {disease} Detected",
#         "status":     "diseased",
#         "disease":    disease,
#         "advice":     advice,
#         "confidence": round(confidence, 1),
#         "source":     source,
#     }


# # ═══════════════════════════════════════════════════
# #  UTILITY
# # ═══════════════════════════════════════════════════
# def allowed_file(filename):
#     return "." in filename and filename.rsplit(".", 1)[-1] in ALLOWED_EXT


# # ═══════════════════════════════════════════════════
# #  FLASK ROUTES
# # ═══════════════════════════════════════════════════
# @app.route("/", methods=["GET", "POST"])
# def index():
#     if request.method != "POST":
#         return render_template("index.html")

#     # Basic validation
#     if "image" not in request.files:
#         flash("Please select an image to upload.", "danger")
#         return redirect(request.url)

#     file = request.files["image"]
#     if not file.filename:
#         flash("No file selected.", "warning")
#         return redirect(request.url)

#     if not allowed_file(file.filename):
#         flash("Unsupported format. Please upload a JPG or PNG image.", "danger")
#         return redirect(request.url)

#     # Save
#     ext       = file.filename.rsplit(".", 1)[-1].lower()
#     filename  = f"{uuid4()}.{ext}"
#     save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
#     file.save(save_path)

#     def render_result(interp, top_preds=None, confidence=0.0):
#         return render_template(
#             "index.html",
#             image_url      = url_for("static", filename=f"uploads/{filename}"),
#             interpretation = interp,
#             predictions    = top_preds or [],
#             top_confidence = round(confidence, 1),
#         )

#     try:
#         image = Image.open(save_path).convert("RGB")

#         # ── Step 1: Human / Object guard ───────────────────────
#         scene = detect_scene(image)
#         print(f"[CropMD] Scene: {scene}")

#         if scene == "human":
#             return render_result(build_result(
#                 "invalid",
#                 "A human face or body was detected. "
#                 "Please upload a photograph of a crop leaf only.",
#                 95.0, "guard"
#             ))
#         if scene == "object":
#             return render_result(build_result(
#                 "invalid",
#                 "A non-plant object was detected. "
#                 "Please upload a clear photograph of a crop leaf.",
#                 90.0, "guard"
#             ))

#         # ── Step 2: Pixel feature extraction ───────────────────
#         features = extract_pixel_features(image)
#         print(f"[CropMD] Pixel features: { {k: round(v,3) if isinstance(v,float) else v for k,v in features.items()} }")

#         px_status, px_label, px_conf = classify_by_pixels(features)

#         # Reject non-leaf images immediately
#         if px_status == "invalid":
#             return render_result(build_result("invalid", px_label, px_conf, "pixel"))

#         # ── Step 3: Deep-model prediction ──────────────────────
#         dl_status, dl_label, dl_conf = None, None, 0.0
#         top_preds = []

#         if DEEP_MODEL_AVAILABLE:
#             inp   = preprocess_for_dl(image)
#             probs = crop_model.predict(inp, verbose=0)[0]
#             idx   = int(np.argmax(probs))
#             dl_conf  = float(np.max(probs)) * 100
#             dl_label = CLASS_NAMES[idx]
#             dl_status = "healthy" if "Healthy" in dl_label else "diseased"

#             top_idx   = probs.argsort()[-3:][::-1]
#             top_preds = [
#                 {
#                     "label":      CLASS_NAMES[i],
#                     "confidence": round(float(probs[i]) * 100, 1),
#                 }
#                 for i in top_idx
#             ]
#             print(f"[CropMD] Deep model: {dl_label} @ {dl_conf:.1f}%")

#         # ── Step 4: Fusion ──────────────────────────────────────
#         # A) Deep model confident  → trust it
#         # B) Pixel engine confident → use pixels
#         # C) Both uncertain         → report uncertain
#         if DEEP_MODEL_AVAILABLE and dl_conf >= MIN_DL_CONFIDENCE:
#             interp = build_result(dl_status, dl_label, dl_conf, "deep_model")
#         elif px_status in ("diseased", "healthy"):
#             interp = build_result(px_status, px_label, px_conf, "pixel_analysis")
#             if not top_preds:
#                 top_preds = [{"label": px_label, "confidence": round(px_conf, 1)}]
#         elif DEEP_MODEL_AVAILABLE and dl_conf > 0:
#             # Use deep-model label but flag low confidence
#             interp = build_result("uncertain", dl_label, dl_conf, "deep_model_low")
#         else:
#             interp = build_result("uncertain", px_label, 30.0, "pixel_analysis")

#         return render_result(interp, top_preds, interp["confidence"])

#     except Exception as exc:
#         import traceback
#         print(f"[CropMD] ERROR: {exc}")
#         traceback.print_exc()
#         flash("An error occurred while processing the image. Please try again.", "danger")
#         return redirect(request.url)


# # ═══════════════════════════════════════════════════
# #  ENTRY POINT
# # ═══════════════════════════════════════════════════
# if __name__ == "__main__":
#     app.run(debug=True, port=5003)

































import os
from uuid import uuid4
import gdown
import numpy as np
from PIL import Image
from flask import Flask, render_template, request, redirect, url_for, flash

# Suppress TF logs
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# ✅ IMPORTANT IMPORT
from tensorflow.keras.models import load_model

# ================= CONFIG =================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "vgg16_crop_model.h5")

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXT = {"png", "jpg", "jpeg"}

MODEL_URL = "https://drive.google.com/uc?id=1pfJ0FnBK4jcWIeHYs1u0JxpIRGGbzUCq"

# Download model if not exists
if not os.path.exists(MODEL_PATH):
    print("Downloading model...")
    gdown.download(MODEL_URL, MODEL_PATH, quiet=False)

# ================= APP =================
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================= LOAD MODEL =================
try:
    crop_model = load_model(MODEL_PATH, compile=False)
    print("Model loaded successfully")
except Exception as e:
    print("Model load error:", e)
    crop_model = None

# ================= HELPERS =================
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[-1].lower() in ALLOWED_EXT

def preprocess(image):
    img = image.resize((224, 224))
    arr = np.array(img) / 255.0
    return np.expand_dims(arr, axis=0)

# ================= ROUTES =================
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    if "image" not in request.files:
        flash("No file uploaded")
        return redirect(request.url)

    file = request.files["image"]

    if file.filename == "":
        flash("No selected file")
        return redirect(request.url)

    if not allowed_file(file.filename):
        flash("Invalid file type")
        return redirect(request.url)

    filename = str(uuid4()) + ".jpg"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:
        image = Image.open(filepath).convert("RGB")

        if crop_model is None:
            return "Model not loaded"

        img = preprocess(image)
        preds = crop_model.predict(img)

        idx = np.argmax(preds[0])
        confidence = float(preds[0][idx]) * 100

        return render_template(
            "index.html",
            image_url=url_for("static", filename=f"uploads/{filename}"),
            prediction=f"Class {idx}",
            confidence=round(confidence, 2),
        )

    except Exception as e:
        print("ERROR:", e)
        return f"Error: {str(e)}"

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)