import json
import os
import uuid
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# ==========================================================
# BUAT FILE HOSING OTOMATIS (requirements.txt & Procfile)
# ==========================================================
if not os.path.exists("requirements.txt"):
    with open("requirements.txt", "w") as f:
        f.write("Flask==3.0.0\ngunicorn==21.2.0\n")

if not os.path.exists("Procfile"):
    with open("Procfile", "w") as f:
        f.write("web: gunicorn app:app\n")

# ==========================================================
# KONFIGURASI FOLDER & DATABASE
# ==========================================================
UPLOAD_FOLDER = os.path.join("static", "uploads")
DATA_FILE = "notes.json"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/notes", methods=["GET"])
def get_notes():
    with open(DATA_FILE, "r") as f:
        notes = json.load(f)
    return jsonify(notes)


@app.route("/api/notes", methods=["POST"])
def add_note():
    sender = request.form.get("sender", "Anonim")
    message = request.form.get("message", "")
    color = request.form.get("color", "#FFF2F2")

    image_path = None
    if "photo" in request.files:
        file = request.files["photo"]
        if file and file.filename != "" and allowed_file(file.filename):
            ext = file.filename.rsplit(".", 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            image_path = f"/static/uploads/{filename}"

    new_note = {
        "id": uuid.uuid4().hex,
        "sender": sender,
        "message": message,
        "image_path": image_path,
        "color": color,
    }

    with open(DATA_FILE, "r+") as f:
        notes = json.load(f)
        notes.append(new_note)
        f.seek(0)
        json.dump(notes, f, indent=4)

    return jsonify({"success": True, "note": new_note})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)