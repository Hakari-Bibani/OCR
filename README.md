# Kurdish OCR Flask App

A simple Flask web application that extracts Kurdish text from uploaded images or PDF files using the Google Cloud Vision API.

## Features

- Upload Kurdish documents as images or PDFs.
- Uses Google Cloud Vision OCR for accurate text extraction.
- Converts PDF pages to images using [PyMuPDF](https://pymupdf.readthedocs.io/).
- Displays detected text on the results page.

## Prerequisites

1. Python 3.10 or later.
2. A Google Cloud Vision API key with the Vision API enabled.
3. Optional but recommended: create and activate a Python virtual environment.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Set the following environment variables before running the application:

- `FLASK_SECRET_KEY` &mdash; secret key used by Flask for session management.
- `GOOGLE_VISION_API_KEY` &mdash; your Google Cloud Vision API key.

You can export them in your shell session:

```bash
export FLASK_SECRET_KEY="change-me"
export GOOGLE_VISION_API_KEY="your_api_key_here"
```

## Running the application

```bash
python app.py
```

The app will start on `http://localhost:5000/`. Navigate there and upload a Kurdish PDF or image to extract text.

## Notes

- Google Cloud Vision OCR works well with Kurdish text without additional configuration.
- Uploaded files are saved to the `uploads/` directory. Make sure this directory is writable in your environment.
- For production deployments you should integrate proper authentication, HTTPS, and persistent storage.
