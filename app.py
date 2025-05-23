import streamlit as st
from PIL import Image
import base64
from pdf2image import convert_from_bytes
from google_genai import GoogleGenAI  # hypothetical Python SDK

st.set_page_config("Kurdish Sorani OCR", layout="wide")

st.title("Kurdish Sorani OCR")

# 1. API key from secrets.toml
api_key = st.secrets["API_KEY"]
ai = GoogleGenAI(api_key=api_key, model="gemini-2.5-flash-preview-04-17")

# 2. File uploader
uploaded = st.file_uploader("Upload Image or PDF", type=["png","jpg","webp","pdf"])

if uploaded:
    # handle PDF → first page to image
    if uploaded.type == "application/pdf":
        pages = convert_from_bytes(uploaded.read(), dpi=200, first_page=1, last_page=1)
        img = pages[0]
    else:
        img = Image.open(uploaded)

    st.image(img, caption="Preview", use_column_width=True)

    if st.button("Extract Text"):
        with st.spinner("Extracting…"):
            # encode to base64
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            b64 = base64.b64encode(buffered.getvalue()).decode()

            # call Gemini
            resp = ai.generate_content([
                {"inlineData":{"mimeType":"image/png","data":b64}},
                {"text":"Perform OCR on this image and extract all Kurdish Sorani…"}
            ])
            text = resp.text.strip() or "No Kurdish Sorani text detected."
            st.text_area("Extracted Text", text, height=300)

st.markdown("---")
st.write("Powered by AI. ©2025")
