from PIL import Image
import pytesseract

def extract_text_from_image(image: Image.Image) -> str:
    # Configure Tesseract to use Kurdish language
    custom_config = r'--oem 3 --psm 6 -l kur+ara'
    text = pytesseract.image_to_string(image, config=custom_config)
    return text
