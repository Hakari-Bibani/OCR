"""Streamlit app for extracting Kurdish text using Google Cloud Vision."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import List

import streamlit as st
from google.api_core.client_options import ClientOptions
from google.cloud import vision

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "tiff", "pdf"}


def _vision_client() -> vision.ImageAnnotatorClient:
    api_key = os.environ.get("GOOGLE_VISION_API_KEY")
    client_options = ClientOptions(api_key=api_key) if api_key else None
    return vision.ImageAnnotatorClient(client_options=client_options)


def _process_document(path: Path) -> List[str]:
    ext = path.suffix.lower()
    client = _vision_client()

    if ext == ".pdf":
        return _extract_pdf_text(client, path)
    return _extract_image_text(client, path)


def _extract_image_text(client: vision.ImageAnnotatorClient, path: Path) -> List[str]:
    with path.open("rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)

    if response.error.message:
        raise RuntimeError(response.error.message)

    annotations = response.text_annotations
    if not annotations:
        return []

    # The first annotation contains the full text, subsequent entries are word-level.
    full_text = annotations[0].description
    return [full_text.strip()]


def _extract_pdf_text(client: vision.ImageAnnotatorClient, path: Path) -> List[str]:
    import fitz  # PyMuPDF

    document = fitz.open(path)
    blocks: List[str] = []
    try:
        for page_number in range(document.page_count):
            page = document.load_page(page_number)
            pix = page.get_pixmap(dpi=300)
            image = vision.Image(content=pix.tobytes())
            response = client.text_detection(image=image)

            if response.error.message:
                raise RuntimeError(response.error.message)

            annotations = response.text_annotations
            if annotations:
                blocks.append(annotations[0].description.strip())
    finally:
        document.close()

    return blocks


def _save_to_temp_file(data: bytes, filename: str | None) -> Path:
    suffix = Path(filename).suffix if filename else ""
    suffix = suffix if suffix else ".tmp"
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        tmp_file.write(data)
        tmp_file.flush()
    finally:
        tmp_file.close()
    return Path(tmp_file.name)


def main() -> None:
    st.set_page_config(page_title="Kurdish OCR", page_icon="📝", layout="centered")
    st.title("Kurdish OCR")
    st.write(
        "Upload a Kurdish document as an image or PDF and extract the detected text using "
        "Google Cloud Vision."
    )

    with st.form("ocr_form"):
        uploaded_file = st.file_uploader(
            "Upload Kurdish image or PDF",
            type=sorted(ALLOWED_EXTENSIONS),
        )
        submitted = st.form_submit_button("Extract text")

    if not submitted:
        return

    if not uploaded_file:
        st.warning("Please upload a file before submitting the form.")
        return

    file_data = uploaded_file.getvalue()
    if not file_data:
        st.warning("The uploaded file is empty. Please try again with a different file.")
        return

    tmp_path = _save_to_temp_file(file_data, uploaded_file.name)
    try:
        try:
            text_blocks = _process_document(tmp_path)
        except Exception as exc:  # pragma: no cover - surfaced to the UI
            st.error(f"Failed to process the document: {exc}")
            return

        if not text_blocks:
            st.info("No text detected in the document.")
            return

        st.success("Text extracted successfully.")
        for index, block in enumerate(text_blocks, start=1):
            st.text_area(
                label=f"Extracted text block {index}",
                value=block,
                height=200,
                key=f"text_block_{index}",
            )

        st.download_button(
            label="Download original file",
            data=file_data,
            file_name=uploaded_file.name or f"document{tmp_path.suffix}",
            mime=uploaded_file.type or "application/octet-stream",
        )
    finally:
        tmp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
