import os
import requests
import tarfile
import shutil
import subprocess
import sys
import platform

def check_tesseract_installed():
    """Check if tesseract is installed"""
    try:
        result = subprocess.run(['tesseract', '--version'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True)
        if result.returncode == 0:
            print("✓ Tesseract is installed")
            print(result.stdout.split('\n')[0])
            return True
        else:
            print("✗ Tesseract is not installed or not in PATH")
            return False
    except FileNotFoundError:
        print("✗ Tesseract is not installed or not in PATH")
        return False

def get_tessdata_prefix():
    """Get the TESSDATA_PREFIX environment variable or try to find it"""
    tessdata_prefix = os.environ.get('TESSDATA_PREFIX')
    
    if tessdata_prefix:
        print(f"TESSDATA_PREFIX found: {tessdata_prefix}")
        return tessdata_prefix
    
    # Try to find tessdata directory based on platform
    if platform.system() == 'Linux':
        possible_paths = [
            '/usr/share/tesseract-ocr/4.00/tessdata',
            '/usr/share/tesseract-ocr/tessdata',
            '/usr/local/share/tessdata',
        ]
    elif platform.system() == 'Darwin':  # macOS
        possible_paths = [
            '/usr/local/share/tessdata',
            '/opt/homebrew/share/tessdata',
        ]
    elif platform.system() == 'Windows':
        possible_paths = [
            'C:\\Program Files\\Tesseract-OCR\\tessdata',
            'C:\\Program Files (x86)\\Tesseract-OCR\\tessdata',
        ]
    else:
        possible_paths = []
    
    for path in possible_paths:
        if os.path.isdir(path):
            print(f"Found tessdata directory: {path}")
            return path
    
    # Ask user for tessdata path
    print("Could not automatically find tessdata directory.")
    user_path = input("Please enter the path to your tessdata directory: ")
    if os.path.isdir(user_path):
        return user_path
    else:
        print(f"The path {user_path} does not exist or is not a directory.")
        sys.exit(1)

def download_kurdish_model():
    """Download Kurdish language model for Tesseract"""
    print("Checking for Kurdish (Sorani) language model...")
    
    # Get tessdata directory
    tessdata_prefix = get_tessdata_prefix()
    
    # Check if Kurdish model already exists
    kurdish_model_path = os.path.join(tessdata_prefix, 'ckb.traineddata')
    if os.path.exists(kurdish_model_path):
        print("✓ Kurdish (Sorani) language model already installed")
        return
    
    print("Downloading Kurdish (Sorani) language model...")
    
    # Create a temporary directory
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Try to download directly from GitHub
    model_url = "https://github.com/AsoSoft/Kurdish-Tesseract-Model/raw/master/Model-Files/Kurdish-Latin.traineddata"
    ckb_traineddata_path = os.path.join(temp_dir, 'ckb.traineddata')
    
    try:
        response = requests.get(model_url, stream=True)
        response.raise_for_status()
        
        with open(ckb_traineddata_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        # Copy the file to tessdata directory
        try:
            shutil.copy(ckb_traineddata_path, tessdata_prefix)
            print(f"✓ Successfully installed Kurdish model to {tessdata_prefix}")
        except PermissionError:
            print(f"✗ Permission denied when copying to {tessdata_prefix}")
            print(f"Please run this script with administrator privileges or manually copy")
            print(f"the file from {ckb_traineddata_path} to {tessdata_prefix}")
    except Exception as e:
        print(f"✗ Error downloading Kurdish model: {e}")
        print("Please download it manually from https://github.com/AsoSoft/Kurdish-Tesseract-Model")
        print(f"and place it in {tessdata_prefix} as 'ckb.traineddata'")
    
    # Clean up
    try:
        shutil.rmtree(temp_dir)
    except:
        pass

if __name__ == "__main__":
    print("Kurdish Tesseract Model Installer")
    print("=================================")
    
    if check_tesseract_installed():
        download_kurdish_model()
    else:
        print("Please install Tesseract OCR before continuing.")
        print("Visit https://github.com/tesseract-ocr/tesseract for installation instructions.")
