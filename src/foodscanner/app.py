from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import os
import requests  # Import this to make a request to your own API
from werkzeug.utils import secure_filename
from calorie import process_image

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/process_image", methods=["POST"])
def process_image_request():
    print("Received request at /process_image")  # Debugging

    # Read JSON data properly
    data = request.get_json()
    print("Received JSON:", data)  # Debugging

    if not data or "filename" not in data:
        print("No filename provided in JSON.")
        return jsonify({"error": "No filename provided"}), 400

    image_filename = data["filename"]
    print("Processing image:", image_filename)  # Debugging

    image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)

    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return jsonify({"error": "File not found"}), 404

    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()

    print("Image successfully read.")  # Debugging

    response_data = process_image(image_bytes)

    print("Final JSON output:", response_data)  # Debugging

    return jsonify(response_data)


@app.route("/")
def index():
    return render_template("index.html")


import requests

@app.route("/upload", methods=["POST"])
def upload():
    print("Received upload request.")  # Debugging

    text_data = request.form.get("mealText")
    file = request.files.get("mealImage")

    if not file:
        print("No image file received.")
        return jsonify({"error": "No file uploaded"}), 400

    uploaded_filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], uploaded_filename)
    file.save(file_path)

    print(f"File saved at: {file_path}")  # Debugging

    # 🟢 Remove session storage
    print("About to call /process_image with filename:", uploaded_filename)

    try:
        response = requests.post("http://127.0.0.1:5000/process_image", json={"filename": uploaded_filename})
        print("Response from /process_image:", response.status_code, response.text)  # Debugging
    except Exception as e:
        print("Error calling /process_image:", e)  # Debugging

    return redirect(url_for("details"))


@app.route("/details")
def details():
    return render_template("details.html")


if __name__ == "__main__":
    app.run(debug=True)
