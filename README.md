# Kurdish OCR Streamlit App

A lightweight [Streamlit](https://streamlit.io/) interface for extracting Kurdish text from images or PDF documents with the help of the Google Cloud Vision API.

## Features

- Upload Kurdish documents as images or PDFs (PNG, JPG, JPEG, GIF, BMP, TIFF, PDF).
- Converts PDF pages to images using [PyMuPDF](https://pymupdf.readthedocs.io/).
- Displays the detected text directly in the browser and allows downloading the original file.

## Prerequisites

1. Python 3.10 or later.
2. A Google Cloud Vision API key with the Vision API enabled.
3. Optional but recommended: create and activate a Python virtual environment.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Before running the application you must provide credentials for the Google Cloud Vision API. There are two supported options:

1. **API key** &mdash; set the following environment variable or add it to Streamlit's secrets file:
   - `GOOGLE_VISION_API_KEY` &mdash; your Google Cloud Vision API key.

   Example shell configuration:

   ```bash
   export GOOGLE_VISION_API_KEY="your_api_key_here"
   ```

   Or create `.streamlit/secrets.toml` next to `app.py` with:

   ```toml
   GOOGLE_VISION_API_KEY = "your_api_key_here"
   ```

2. **Service account** &mdash; supply the JSON credentials via the `GOOGLE_APPLICATION_CREDENTIALS_JSON` environment variable. This enables OAuth-based access instead of an API key.

## Running the application

```bash
streamlit run app.py
```

Streamlit will print a local URL (e.g., `http://localhost:8501/`). Open it in a browser, upload a Kurdish PDF or image, and click **Extract text** to see the detected text blocks.

## Notes

- Google Cloud Vision OCR works well with Kurdish text without additional configuration.
- Uploaded files are processed in-memory and stored temporarily only for OCR extraction.
- For production deployments you should configure secure storage of secrets (for example Streamlit secrets or a secrets manager) and evaluate Google Cloud costs.
