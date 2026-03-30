"""File upload and processing utilities"""

import os
import base64
from pathlib import Path
from typing import Optional, Tuple
import docx
from config import ALLOWED_FILE_TYPES, UPLOAD_FOLDER, MAX_FILE_SIZE, IMAGE_FILE_TYPES

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: PyPDF2 not installed. PDF support disabled.")

def ensure_upload_folder():
    """Create uploads folder if it doesn't exist"""
    Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

def validate_file(file_name: str, file_size: int) -> tuple[bool, str]:
    """Validate uploaded file"""
    # Check file extension
    file_ext = Path(file_name).suffix.lower()
    if file_ext not in ALLOWED_FILE_TYPES:
        return False, f"File type {file_ext} not allowed. Allowed: {ALLOWED_FILE_TYPES}"
    
    # Check file size
    if file_size > MAX_FILE_SIZE:
        return False, f"File size exceeds {MAX_FILE_SIZE / (1024*1024):.0f} MB limit"
    
    return True, "OK"

def read_text_file(file_path: str) -> str:
    """Read content from text file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def read_docx_file(file_path: str) -> str:
    """Read content from DOCX file"""
    try:
        doc = docx.Document(file_path)
        return '\n'.join(paragraph.text for paragraph in doc.paragraphs)
    except Exception as e:
        return f"Error reading DOCX file: {str(e)}"

def read_pdf_file(file_path: str) -> str:
    """Read content from PDF file"""
    if not PDF_AVAILABLE:
        return "Error: PyPDF2 not installed. Install with: pip install PyPDF2"
    
    try:
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
    except Exception as e:
        return f"Error reading PDF file: {str(e)}"

def is_image_file(file_path: str) -> bool:
    """Check if file is an image"""
    file_ext = Path(file_path).suffix.lower()
    return file_ext in IMAGE_FILE_TYPES

def encode_image_to_base64(file_path: str) -> str:
    """Encode image to base64 for vision model API"""
    try:
        with open(file_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        return f"Error encoding image: {str(e)}"

def extract_file_content(file_path: str) -> str:
    """Extract content based on file type"""
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext == ".txt":
        return read_text_file(file_path)
    elif file_ext == ".docx":
        return read_docx_file(file_path)
    elif file_ext == ".pdf":
        return read_pdf_file(file_path)
    elif is_image_file(file_path):
        return f"[IMAGE FILE: {Path(file_path).name}]"
    else:
        return "Unsupported file type"

def get_file_metadata(file_path: str) -> dict:
    """Get metadata about uploaded file"""
    path = Path(file_path)
    return {
        "name": path.name,
        "extension": path.suffix.lower(),
        "size_bytes": path.stat().st_size,
        "size_readable": f"{path.stat().st_size / 1024:.2f} KB",
        "is_image": is_image_file(file_path)
    }

def save_uploaded_file(uploaded_file) -> Optional[str]:
    """Save uploaded file and return path"""
    ensure_upload_folder()
    
    try:
        # Validate
        is_valid, msg = validate_file(uploaded_file.name, uploaded_file.size)
        if not is_valid:
            return None
        
        # Save
        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        return file_path
    except Exception as e:
        print(f"Error saving file: {e}")
        return None
