# Kurdish OCR Streamlit App

A lightweight [Streamlit](https://streamlit.io/) interface for extracting Kurdish text from images or PDF documents with the help of the Google Gemini API.

## Features

- Upload Kurdish documents as images or PDFs (PNG, JPG, JPEG, GIF, BMP, TIFF, PDF).
- Converts PDF pages to images using [PyMuPDF](https://pymupdf.readthedocs.io/).
- Displays the detected text directly in the browser and allows downloading the original file.

## Prerequisites

1. Python 3.10 or later.
2. A Google Gemini API key with the Generative Language API enabled.
3. Optional but recommended: create and activate a Python virtual environment.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Before running the application you must provide an API key for the Google Gemini Generative Language API. The app will fail fast if it cannot find the key.

- **API key** &mdash; set the following environment variable or add it to Streamlit's secrets file:
  - `GEMINI_API_KEY` &mdash; your Google Gemini API key.

  Example shell configuration:

  ```bash
  export GEMINI_API_KEY="your_api_key_here"
  ```

  Or create `.streamlit/secrets.toml` next to `app.py` with:

  ```toml
  GEMINI_API_KEY = "your_api_key_here"
  ```

## Running the application

```bash
streamlit run app.py
```

Streamlit will print a local URL (e.g., `http://localhost:8501/`). Open it in a browser, upload a Kurdish PDF or image, and click **Extract text** to see the detected text blocks.

## Notes

- Google Gemini handles OCR-style extraction directly from the uploaded files.
- Uploaded files are processed in-memory and stored temporarily only for OCR extraction.
- For production deployments you should configure secure storage of secrets (for example Streamlit secrets or a secrets manager) and evaluate Google Cloud costs.
