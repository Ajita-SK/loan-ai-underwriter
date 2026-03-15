#!/usr/bin/env python3
"""Loan AI Underwriter: extract text from PDF loan documents and show results on webpage."""

from flask import Flask, render_template, request
from pathlib import Path
from typing import Iterable
import os
import requests
from pypdf import PdfReader

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FILENAME = "loan_documents.txt"
OCR_API_KEY = "K81340368688957"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def run_ocr_space(pdf_path: Path) -> str:
    """Run OCR using OCR.space for scanned PDFs."""

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


def find_pdf_files(folder: Path) -> list[Path]:
    """Return all PDF files inside folder."""

    return sorted(
        [
            path for path in folder.iterdir()
            if path.is_file() and path.suffix.lower() == ".pdf"
        ]
    )


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text from a single PDF."""

    reader = PdfReader(str(pdf_path))
    pages: Iterable[str] = (page.extract_text() or "" for page in reader.pages)

    text = "\n".join(pages).strip()

    if len(text) < 100:
        try:
            print(f"OCR processing for scanned PDF: {pdf_path.name}")
            text = run_ocr_space(pdf_path)
        except Exception as e:
            print(f"OCR failed for {pdf_path.name}: {e}")

    return text


def combine_pdf_texts(input_folder: Path, output_file: Path) -> int:
    """Extract text from all PDFs and combine into one file."""

    pdf_files = find_pdf_files(input_folder)

    if not pdf_files:
        raise ValueError("No PDF files found.")

    sections = []

    for pdf_file in pdf_files:
        extracted_text = extract_text_from_pdf(pdf_file)

        section = (
            f"{'='*80}\n"
            f"SOURCE FILE: {pdf_file.name}\n"
            f"{'='*80}\n"
            f"{extracted_text}\n"
        )

        sections.append(section)

    output_file.write_text("\n\n".join(sections), encoding="utf-8")

    return len(pdf_files)


@app.route("/", methods=["GET", "POST"])
def index():

    result_text = ""

    if request.method == "POST":

        files = request.files.getlist("pdfs")

        for file in files:

            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

        output_file = Path(UPLOAD_FOLDER) / OUTPUT_FILENAME

        combine_pdf_texts(Path(UPLOAD_FOLDER), output_file)

        with open(output_file, "r", encoding="utf-8") as f:
            result_text = f.read()

    return render_template("index.html", result=result_text)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
