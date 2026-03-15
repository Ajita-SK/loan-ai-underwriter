from flask import Flask, render_template, request, send_file
from pathlib import Path
from pypdf import PdfReader
import requests
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FILENAME = "loan_documents.txt"
OCR_API_KEY = "K81340368688957"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def run_ocr_space(pdf_path):
    url = "https://api.ocr.space/parse/image"

    with open(pdf_path, "rb") as f:
        payload = {
            "apikey": OCR_API_KEY,
            "language": "eng"
        }

        files = {"file": f}

        response = requests.post(url, data=payload, files=files)

    result = response.json()

    return result["ParsedResults"][0]["ParsedText"]


def extract_text_from_pdf(pdf_path):

    reader = PdfReader(str(pdf_path))
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text

    if len(text.strip()) < 100:
        try:
            text = run_ocr_space(pdf_path)
        except Exception as e:
            print("OCR failed:", e)

    return text


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    files = request.files.getlist("files")

    combined_text = ""

    for file in files:

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        text = extract_text_from_pdf(filepath)

        combined_text += f"\n\n===== {file.filename} =====\n\n"
        combined_text += text

    output_path = os.path.join(UPLOAD_FOLDER, OUTPUT_FILENAME)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(combined_text)

    return send_file(output_path, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
