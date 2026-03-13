# Loan AI Underwriter

A Python application that processes a folder of loan-document PDFs, extracts text from each file, and combines the content into one output file named `loan_documents.txt`.

## Features

- Accepts a folder containing multiple PDF files.
- Extracts text from each PDF using `pypdf`.
- Writes combined output to `loan_documents.txt` in the same input folder.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python app.py /path/to/folder/with/pdfs
```

Example output:

```text
Processed 5 PDF file(s).
Combined text written to: /path/to/folder/with/pdfs/loan_documents.txt
```
