import streamlit as st
import requests
import base64
import fitz  # PyMuPDF
from PIL import Image
import io
import os

st.set_page_config(page_title="Kurdish Sorani OCR", layout="wide")

# Load Gemini API key from secrets
API_KEY = st.secrets["API_KEY"]
OCR_MODEL = "gemini-2.5-flash-preview-04-17"

def convert_pdf_to_image(file: bytes) -> Image.Image:
    pdf_document = fitz.open(stream=file, filetype="pdf")
    page = pdf_document.load_page(0)  # First page
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Zoom for better OCR
    img_data = pix.tobytes("png")
    return Image.open(io.BytesIO(img_data))

def perform_ocr(base64_image: str, mime_type: str) -> str:
    url = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent?key={}".format(OCR_MODEL, API_KEY)

    payload = {
        "contents": {
            "parts": [
                {
                    "inlineData": {
                        "mimeType": mime_type,
                        "data": base64_image
                    }
                },
                {
                    "text": "Perform OCR on this image and extract all Kurdish Sorani (Central Kurdish) text. If none is found, reply with 'No Kurdish Sorani text detected.'"
                }
            ]
        }
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    try:
        return data['candidates'][0]['content']['parts'][0]['text'].strip()
    except:
        return "No Kurdish Sorani text detected."

st.title("📜 Kurdish Sorani OCR")
st.markdown("Upload an image or PDF to extract Kurdish Sorani text using Gemini AI.")

uploaded_file = st.file_uploader("Choose an image or PDF", type=["png", "jpg", "jpeg", "webp", "pdf"])

if uploaded_file:
    file_bytes = uploaded_file.read()
    file_type = uploaded_file.type

    if file_type == "application/pdf":
        try:
            image = convert_pdf_to_image(file_bytes)
            st.image(image, caption="PDF Page Preview", use_column_width=True)
        except Exception as e:
            st.error("Failed to convert PDF: {}".format(e))
            st.stop()
    else:
        image = Image.open(io.BytesIO(file_bytes))
        st.image(image, caption="Uploaded Image", use_column_width=True)

    if st.button("🔍 Extract Text"):
        with st.spinner("Processing..."):
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            extracted_text = perform_ocr(img_str, "image/png")

        st.subheader("📝 Extracted Text:")
        st.text_area("Text", extracted_text, height=300)

        if st.button("📋 Copy Text"):
            st.success("Use keyboard shortcut Ctrl+C (or Cmd+C on Mac) to copy the text above.")

