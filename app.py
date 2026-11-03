from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image, ImageStat
import os, uuid, math

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")
ALLOWED = {"png", "jpg", "jpeg", "webp"}
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

MATERIAL_RATES = {
    "Residential basic": {"foundation": 900, "structure": 1500, "finishing": 1100, "contingency": .10},
    "Residential premium": {"foundation": 1200, "structure": 2100, "finishing": 1900, "contingency": .12},
    "Commercial": {"foundation": 1400, "structure": 2400, "finishing": 1600, "contingency": .15},
}

def image_assessment(path):
    """Lightweight image feature analysis; not a substitute for a structural engineer."""
    image = Image.open(path).convert("RGB")
    image.thumbnail((500, 500))
    stat = ImageStat.Stat(image)
    r, g, b = stat.mean
    brightness = sum(stat.mean) / 3
    contrast = sum(stat.stddev) / 3
    width, height = Image.open(path).size
    notes = []
    if brightness < 75:
        notes.append("Image is dark; retake in brighter, even lighting for a more reliable visual review.")
    elif brightness > 220:
        notes.append("Image is very bright; reduce glare and retake if surface details are important.")
    else:
        notes.append("Image brightness is broadly suitable for a preliminary visual review.")
    if contrast < 25:
        notes.append("Low contrast may hide cracks, joints, or surface changes.")
    else:
        notes.append("Visible contrast is present; zoom in on any suspicious surface areas.")
    if width < 400 or height < 300:
        notes.append("The image resolution is limited; use a higher-resolution image if available.")
    else:
        notes.append("Image resolution is adequate for a basic overview.")
    if r > g * 1.12 and r > b * 1.12:
        notes.append("Warm/red tones dominate. This can be caused by brick, rust, lighting, or camera white balance.")
    if g > r * 1.12 and g > b * 1.08:
        notes.append("Green tones dominate; check whether vegetation or colored lighting affects the scene.")
    notes.append("This demo does not diagnose structural safety or reliably detect defects. Arrange an on-site professional inspection for cracks, deformation, corrosion, or other concerns.")
    return {
        "dimensions": f"{width} × {height}px",
        "brightness": round(brightness, 1),
        "contrast": round(contrast, 1),
        "summary": "Preliminary image quality and scene-colour review completed.",
        "findings": notes
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze-image", methods=["POST"])
def analyze_image():
    file = request.files.get("image")
    if not file or not file.filename:
        return jsonify({"error": "Choose an image first."}), 400
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED:
        return jsonify({"error": "Please upload a PNG, JPG, JPEG, or WEBP image."}), 400
    filename = secure_filename(f"{uuid.uuid4().hex}.{ext}")
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(path)
    try:
        result = image_assessment(path)
    except Exception:
        os.remove(path)
        return jsonify({"error": "Could not read this image. Try another image file."}), 400
    result["image_url"] = "/" + path.replace("\\", "/")
    return jsonify(result)

@app.route("/estimate", methods=["POST"])
def estimate():
    data = request.get_json(silent=True) or {}
    try:
        area = float(data.get("area", 0))
        floors = int(data.get("floors", 1))
        kind = data.get("kind", "Residential basic")
        if not math.isfinite(area) or area <= 0 or area > 1_000_000:
            raise ValueError
        if floors < 1 or floors > 100:
            raise ValueError
        if kind not in MATERIAL_RATES:
            kind = "Residential basic"
    except (ValueError, TypeError):
        return jsonify({"error": "Enter a valid area and floor count."}), 400
    rates = MATERIAL_RATES[kind]
    total_area = area * floors
    foundation = total_area * rates["foundation"] * 0.18
    structure = total_area * rates["structure"]
    finishing = total_area * rates["finishing"]
    subtotal = foundation + structure + finishing
    contingency = subtotal * rates["contingency"]
    return jsonify({
        "total_area": round(total_area, 2),
        "foundation": round(foundation),
        "structure": round(structure),
        "finishing": round(finishing),
        "contingency": round(contingency),
        "total": round(subtotal + contingency),
        "currency": "INR",
        "note": "Illustrative early-stage estimate only. Local rates, design, soil, labour, taxes, approvals, and site conditions will change the actual cost."
    })

@app.route("/plan", methods=["POST"])
def plan():
    data = request.get_json(silent=True) or {}
    try:
        start = data.get("start") or "2026-11-02"
        duration = max(1, min(730, int(data.get("duration", 90))))
        floors = max(1, min(100, int(data.get("floors", 1))))
    except (ValueError, TypeError):
        return jsonify({"error": "Enter a valid duration and floor count."}), 400
    tasks = [
        ("Requirements, site survey & approvals", 0.10),
        ("Design, drawings & procurement", 0.15),
        ("Site preparation & foundation", 0.18),
        ("Structure and slab work", 0.25 + max(0, floors-1)*0.025),
        ("Electrical, plumbing & services", 0.12),
        ("Finishing and fixtures", 0.14),
        ("Inspection, snag list & handover", 0.06),
    ]
    total = sum(x[1] for x in tasks)
    output = []
    day = 1
    for name, fraction in tasks:
        days = max(1, round(duration * fraction / total))
        output.append({"task": name, "days": days, "start_day": day, "end_day": min(duration, day+days-1)})
        day += days
    output[-1]["end_day"] = duration
    return jsonify({"duration": duration, "tasks": output, "note": "Planning template only. Validate sequencing and durations with the site engineer, permits, weather, and supplier lead times."})

@app.route("/assistant", methods=["POST"])
def assistant():
    data = request.get_json(silent=True) or {}
    q = str(data.get("message", "")).strip()
    if not q:
        return jsonify({"reply": "Ask a construction planning, estimating, materials, or safety question."})
    low = q.lower()
    if any(w in low for w in ["crack", "unsafe", "collapse", "structural"]):
        reply = "For a possible structural defect, keep people away from the affected area and arrange an inspection by a qualified structural engineer. Photos alone cannot establish safety. Record the location, approximate size, date, and whether the condition is changing."
    elif any(w in low for w in ["cost", "budget", "estimate", "valuation"]):
        reply = "Start with built-up area, location-specific rates, structural system, finish grade, services, taxes, approvals, and contingency. Use the estimator as an early planning figure only, then get current local quotations and a quantity take-off."
    elif any(w in low for w in ["schedule", "time", "plan", "duration"]):
        reply = "Build the schedule around approvals, procurement lead times, foundation, structure, services, finishing, and inspections. Add dependencies and buffer time, then review progress weekly against the baseline."
    elif any(w in low for w in ["image", "photo", "picture"]):
        reply = "Upload a clear, well-lit photo in Image Analysis. This demo checks basic image quality and colour statistics; it is not a trained defect-detection model and cannot certify construction quality."
    elif any(w in low for w in ["material", "concrete", "cement", "steel"]):
        reply = "Confirm material specifications from approved drawings and local codes. Track supplier certificates, batch details, storage conditions, delivery quantities, and required tests. Do not substitute materials without the responsible engineer's approval."
    else:
        reply = "For a useful construction review, specify the project type, location, built-up area, stage, and decision you need to make. I can help structure a checklist, preliminary estimate, or project schedule; verify technical and safety decisions with qualified professionals."
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
