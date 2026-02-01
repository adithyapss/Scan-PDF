"""
Configuration and API Keys
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for API keys and settings"""
    
    # API Keys (loaded from environment variables)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    
    # Database settings
    DATABASE_PATH = 'pdf_ocr.db'
    
    # Upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'.pdf'}
