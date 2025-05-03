import streamlit as st
import pytesseract
from PIL import Image
import io
import pdf2image
import tempfile
import os
import numpy as np
import cv2
from kurdish_nltk import KurdishTokenizer

# Set page configuration
st.set_page_config(
    page_title="Kurdish Text Extractor",
    page_icon="📝",
    layout="wide"
)

# Define CSS for RTL text
st.markdown("""
<style>
.kurdish-text {
    direction: rtl;
    text-align: right;
    font-family: 'Noto Sans Arabic', 'Unikurd Web', sans-serif;
    font-size: 18px;
    line-height: 1.6;
    padding: 15px;
    background-color: #f5f5f5;
    border-radius: 5px;
}
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("Kurdish (Sorani) Text Extractor")
st.markdown("Upload an image or PDF file to extract Central Kurdish (Sorani) text.")

# Initialize Kurdish tokenizer
tokenizer = KurdishTokenizer()

def preprocess_image(image):
    """Preprocess image to improve OCR accuracy"""
    # Convert to grayscale
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    
    # Apply thresholding
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
    
    return Image.fromarray(denoised)

@st.cache_data
def ocr_kurdish(image):
    """Perform OCR on the image specifically for Kurdish Sorani"""
    # Preprocess the image
    processed_image = preprocess_image(image)
    
    # Use Tesseract with Kurdish language
    try:
        text = pytesseract.image_to_string(processed_image, lang='ckb')
        return text
    except Exception as e:
        st.error(f"OCR Error: {e}")
        return ""

def process_pdf(pdf_file):
    """Process PDF and extract text from each page"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(pdf_file.getvalue())
        tmp_path = tmp.name
    
    # Convert PDF to images
    try:
        images = pdf2image.convert_from_path(tmp_path, dpi=300)
        os.unlink(tmp_path)  # Delete the temporary file
        
        # Process each page
        all_text = []
        progress_bar = st.progress(0)
        for i, img in enumerate(images):
            text = ocr_kurdish(img)
            all_text.append(text)
            progress_bar.progress((i + 1) / len(images))
        
        return "\n\n--- Page Break ---\n\n".join(all_text)
    except Exception as e:
        os.unlink(tmp_path)  # Delete the temporary file
        st.error(f"PDF Processing Error: {e}")
        return ""

# File upload section
uploaded_file = st.file_uploader("Upload an image or PDF file", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file is not None:
    # Show the uploaded file
    file_type = uploaded_file.type
    
    if "image" in file_type:
        # Display image
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Uploaded Image")
            image = Image.open(uploaded_file)
            st.image(image, use_column_width=True)
        
        # Process image
        with st.spinner("Extracting text..."):
            extracted_text = ocr_kurdish(image)
        
        # Display extracted text
        with col2:
            st.subheader("Extracted Text")
            if extracted_text:
                st.markdown(f'<div class="kurdish-text">{extracted_text}</div>', unsafe_allow_html=True)
                
                # Text analysis
                if extracted_text.strip():
                    st.subheader("Text Analysis")
                    tokens = tokenizer.tokenize(extracted_text)
                    st.write(f"Word count: {len(tokens)}")
                    
                    # Download button for extracted text
                    text_bytes = extracted_text.encode('utf-8')
                    st.download_button(
                        label="Download Extracted Text",
                        data=text_bytes,
                        file_name="extracted_text.txt",
                        mime="text/plain"
                    )
            else:
                st.info("No text was extracted. The image might not contain Kurdish text or the text is not clear enough.")
    
    elif "pdf" in file_type:
        st.subheader("Processing PDF")
        
        # Process PDF
        with st.spinner("Extracting text from PDF (this may take a while)..."):
            extracted_text = process_pdf(uploaded_file)
        
        # Display extracted text
        st.subheader("Extracted Text")
        if extracted_text:
            st.markdown(f'<div class="kurdish-text">{extracted_text}</div>', unsafe_allow_html=True)
            
            # Text analysis
            if extracted_text.strip():
                st.subheader("Text Analysis")
                tokens = tokenizer.tokenize(extracted_text)
                st.write(f"Word count: {len(tokens)}")
                
                # Download button for extracted text
                text_bytes = extracted_text.encode('utf-8')
                st.download_button(
                    label="Download Extracted Text",
                    data=text_bytes,
                    file_name="extracted_text.txt",
                    mime="text/plain"
                )
        else:
            st.info("No text was extracted from the PDF.")

# Add information about language support
st.sidebar.header("About")
st.sidebar.info("""
This app extracts text from images and PDFs in Kurdish (Sorani) language.
It uses Tesseract OCR engine with Kurdish language support.
""")

# Settings section
st.sidebar.header("Settings")
st.sidebar.markdown("Tesseract must be configured with Kurdish language support.")

# Instructions
st.sidebar.header("Instructions")
st.sidebar.markdown("""
1. Upload an image or PDF containing Kurdish (Sorani) text
2. Wait for the text to be extracted
3. View or download the extracted text
""")

# Credits
st.sidebar.header("Credits")
st.sidebar.markdown("""
- [AsoSoft Kurdish NLP Tools](https://github.com/AsoSoft)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
""")
