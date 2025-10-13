import os
from pathlib import Path
from typing import List

from flask import Flask, flash, redirect, render_template, request, send_from_directory, url_for
from google.api_core.client_options import ClientOptions
from google.cloud import vision
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "tiff", "pdf"}
UPLOAD_FOLDER = Path("uploads")


def create_app() -> Flask:
    """Application factory for the OCR Flask app."""
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.post("/extract")
    def extract_text():
        if "document" not in request.files:
            flash("No file part in the request.")
            return redirect(url_for("index"))

        file = request.files["document"]
        if file.filename == "":
            flash("No file selected.")
            return redirect(url_for("index"))

        if not _allowed_file(file.filename):
            flash("Unsupported file type. Please upload an image or PDF.")
            return redirect(url_for("index"))

        filename = secure_filename(file.filename)
        saved_path = UPLOAD_FOLDER / filename
        file.save(saved_path)

        try:
            text_blocks = _process_document(saved_path)
        except Exception as exc:  # pragma: no cover - surface as flash message
            flash(f"Failed to process the document: {exc}")
            return redirect(url_for("index"))

        if not text_blocks:
            flash("No text detected in the document.")
            return redirect(url_for("index"))

        return render_template(
            "result.html",
            filename=filename,
            text_blocks=text_blocks,
        )

    @app.get("/uploads/<path:filename>")
    def uploaded_file(filename: str):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    return app


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


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


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
