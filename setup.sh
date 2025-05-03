#!/bin/bash

# Setup script for Kurdish Text Extractor

echo "Setting up Kurdish Text Extractor..."

# Install pip requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check if tesseract is installed
if command -v tesseract > /dev/null 2>&1; then
    echo "✓ Tesseract OCR is installed"
else
    echo "✗ Tesseract OCR is not installed"
    
    # Check operating system
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Installing Tesseract OCR for Linux..."
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr libtesseract-dev poppler-utils
        
        # Try to install Kurdish language pack
        if apt-cache search tesseract-ocr-ckb | grep -q tesseract-ocr-ckb; then
            sudo apt-get install -y tesseract-ocr-ckb
        else
            echo "Kurdish language pack not found in repositories."
            echo "Will download it separately."
        fi
    
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Installing Tesseract OCR for macOS..."
        if command -v brew > /dev/null 2>&1; then
            brew install tesseract poppler
        else
            echo "Homebrew not found. Please install Homebrew first:"
            echo "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
    
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "On Windows, please install Tesseract OCR manually:"
        echo "1. Download from https://github.com/UB-Mannheim/tesseract/wiki"
        echo "2. Add Tesseract to your PATH"
        exit 1
    
    else
        echo "Unsupported operating system. Please install Tesseract OCR manually."
        exit 1
    fi
fi

# Download Kurdish language model
echo "Setting up Kurdish language support..."
python download_kurdish_model.py

echo "Setup complete!"
echo "Run 'streamlit run app.py' to start the application"
