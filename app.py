#!/usr/bin/env python3
"""Loan AI Underwriter: extract text from PDF loan documents."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader

OUTPUT_FILENAME = "loan_documents.txt"


def find_pdf_files(folder: Path) -> list[Path]:
    """Return all PDF files inside folder (non-recursive), sorted by name."""
    return sorted(
        [path for path in folder.iterdir() if path.is_file() and path.suffix.lower() == ".pdf"]
    )


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text from one PDF file."""
    reader = PdfReader(str(pdf_path))
    pages: Iterable[str] = (page.extract_text() or "" for page in reader.pages)
    return "\n".join(pages).strip()


def combine_pdf_texts(input_folder: Path, output_file: Path) -> int:
    """Extract text from all PDFs and write into one text file.

    Returns the number of processed PDFs.
    """
    pdf_files = find_pdf_files(input_folder)
    if not pdf_files:
        raise ValueError(f"No PDF files found in folder: {input_folder}")

    sections: list[str] = []

    for pdf_file in pdf_files:
        extracted_text = extract_text_from_pdf(pdf_file)
        section = (
            f"{'=' * 80}\n"
            f"SOURCE FILE: {pdf_file.name}\n"
            f"{'=' * 80}\n"
            f"{extracted_text}\n"
        )
        sections.append(section)

    output_file.write_text("\n\n".join(sections), encoding="utf-8")
    return len(pdf_files)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="Loan AI Underwriter",
        description=(
            "Extract text from every PDF in a folder and combine all text into "
            f"a single {OUTPUT_FILENAME} file."
        ),
    )
    parser.add_argument(
        "input_folder",
        type=Path,
        help="Path to a folder containing PDF loan documents.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_folder: Path = args.input_folder.expanduser().resolve()

    if not input_folder.exists() or not input_folder.is_dir():
        raise SystemExit(f"Input folder does not exist or is not a directory: {input_folder}")

    output_file = input_folder / OUTPUT_FILENAME
    processed_count = combine_pdf_texts(input_folder, output_file)

    print(f"Processed {processed_count} PDF file(s).")
    print(f"Combined text written to: {output_file}")


if __name__ == "__main__":
    main()
