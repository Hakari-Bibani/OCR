from pdf2image import convert_from_path
from typing import List
from PIL import Image

def extract_images_from_pdf(pdf_path: str) -> List[Image.Image]:
    images = convert_from_path(pdf_path)
    return images
