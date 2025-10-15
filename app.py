"""Streamlit app for extracting Kurdish text using Google Gemini."""

from __future__ import annotations

import base64
import mimetypes
import os
import tempfile
from pathlib import Path
from typing import List

import requests
import streamlit as st

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "tiff", "pdf"}

def _get_api_key() -> str | None:
    """Return the Gemini API key from env vars or Streamlit secrets."""

    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return api_key

    try:
        secrets_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:  # pragma: no cover - defensive for local runs
        secrets_key = None

    return secrets_key


def _process_document(path: Path) -> List[str]:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return _extract_pdf_text(path)
    return _extract_image_text(path)


def _extract_image_text(path: Path) -> List[str]:
    with path.open("rb") as image_file:
        content = image_file.read()

    mime_type, _ = mimetypes.guess_type(str(path))
    mime_type = mime_type or "application/octet-stream"

    text = _extract_text_from_bytes(content, mime_type)
    return [text] if text else []


def _extract_pdf_text(path: Path) -> List[str]:
    import fitz  # PyMuPDF

    document = fitz.open(path)
    blocks: List[str] = []
    try:
        for page_number in range(document.page_count):
            page = document.load_page(page_number)
            pix = page.get_pixmap(dpi=300)
            image_bytes = pix.tobytes("png")
            text = _extract_text_from_bytes(image_bytes, "image/png")
            if text:
                blocks.append(text)
    finally:
        document.close()

    return blocks


def _extract_text_from_bytes(data: bytes, mime_type: str) -> str:
    api_key = _get_api_key()
    if not api_key:
        raise RuntimeError(
            "Gemini API key is not configured. Set the GEMINI_API_KEY environment variable "
            "or add it to Streamlit secrets."
        )

    endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "Extract the text from this document image. Return only the text and "
                            "preserve line breaks when possible."
                        )
                    },
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": base64.b64encode(data).decode("utf-8"),
                        }
                    },
                ]
            }
        ]
    }

    try:
        response = requests.post(
            endpoint,
            params={"key": api_key},
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60,
        )
    except requests.RequestException as exc:  # pragma: no cover - network failure
        raise RuntimeError("Failed to connect to the Gemini API.") from exc

    if response.status_code != 200:
        message = response.text
        try:
            error_payload = response.json()
        except ValueError:
            error_payload = None
        if error_payload and "error" in error_payload:
            message = error_payload["error"].get("message", message)
        raise RuntimeError(f"Gemini API error: {message}")

    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError("Invalid response from the Gemini API.") from exc

    candidates = payload.get("candidates") or []
    if not candidates:
        return ""

    parts = candidates[0].get("content", {}).get("parts", [])
    texts = [part.get("text", "").strip() for part in parts if isinstance(part, dict)]
    text = "\n".join(filter(None, texts)).strip()
    return text


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
        "Google Gemini."
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
