import streamlit as st
from PIL import Image
import easyocr
import tempfile
import fitz  # PyMuPDF
import numpy as np

st.set_page_config(page_title="Kurdish OCR App", layout="wide")
st.title("📄 Kurdish (Sorani) OCR")
st.markdown("Upload an image or PDF to extract text in Central Kurdish (Sorani).")

uploaded_file = st.file_uploader("Upload Image or PDF", type=["png", "jpg", "jpeg", "pdf"])

reader = easyocr.Reader(['ku', 'en'], gpu=False)  # Load once

def extract_text_from_image(image):
    image_np = np.array(image)
    result = reader.readtext(image_np)
    text = "\n".join([item[1] for item in result])
    return text

def extract_images_from_pdf(pdf_file):
    images = []
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    for page in doc:
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        images = extract_images_from_pdf(uploaded_file)
    else:
        images = [Image.open(uploaded_file)]

    for idx, image in enumerate(images):
        st.image(image, caption=f"Page {idx+1}", use_column_width=True)
        with st.spinner("🔍 Extracting text..."):
            text = extract_text_from_image(image)
        st.text_area(f"📝 Extracted Text (Page {idx+1})", text, height=200)
