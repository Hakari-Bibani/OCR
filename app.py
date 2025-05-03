import streamlit as st
from utils.ocr import extract_text_from_image
from utils.pdf_utils import extract_images_from_pdf
from PIL import Image
import tempfile
import os

st.set_page_config(page_title="Kurdish OCR App", layout="wide")

st.title("🧾 Kurdish OCR Web App")
st.markdown("Upload an image or PDF to extract text in Central Kurdish (Sorani).")

uploaded_file = st.file_uploader("Choose an image or PDF file", type=["png", "jpg", "jpeg", "pdf"])

if uploaded_file:
    file_type = uploaded_file.type
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    if file_type == "application/pdf":
        images = extract_images_from_pdf(tmp_path)
    else:
        images = [Image.open(tmp_path)]

    for idx, image in enumerate(images):
        st.image(image, caption=f"Page {idx+1}", use_column_width=True)
        with st.spinner("Extracting text..."):
            text = extract_text_from_image(image)
        st.text_area(f"Extracted Text from Page {idx+1}", text, height=200)
