"""
PDF OCR Pipeline - Main Entry Point
"""
import os
import google.generativeai as genai
from openai import OpenAI
from anthropic import Anthropic
import PyPDF2
from config import Config
from database import Database


class PDFOCRProcessor:
    """Process PDFs using Gemini API for OCR and OpenAI for formatting"""
    
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Configure OpenAI API
        self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Configure Anthropic API
        self.anthropic_client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        
        self.db = Database()
    
    def format_text_with_openai(self, raw_text):
        """Format extracted text using OpenAI"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a text formatting assistant. Clean up and properly format OCR-extracted text, fixing spacing, line breaks, and structure while preserving all content."},
                    {"role": "user", "content": f"Format this OCR text:\n\n{raw_text}"}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"    Warning: OpenAI formatting failed ({e}), using raw text")
            return raw_text
    
    def summarize_with_claude(self, text):
        """Summarize formatted text using Claude"""
        try:
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": f"Provide a concise summary of this document text:\n\n{text}"}
                ]
            )
            return message.content[0].text
        except Exception as e:
            print(f"    Warning: Claude summarization failed ({e})")
            return None
    
    def process_pdf(self, pdf_path):
        """Extract text from PDF using Gemini OCR"""
        print(f"Processing: {pdf_path}")
        
        # Add document to database
        filename = os.path.basename(pdf_path)
        doc_id = self.db.add_document(filename, pdf_path)
        
        # Extract text from PDF using PyPDF2
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            for page_num in range(num_pages):
                print(f"  Processing page {page_num + 1}/{num_pages}...")
                
                page = pdf_reader.pages[page_num]
                extracted_text = page.extract_text()
                
                if extracted_text.strip():
                    # Use Gemini to analyze and extract structured information
                    print(f"    Analyzing with Gemini...")
                    try:
                        response = self.model.generate_content([
                            f"Extract and clean all text from this PDF page content. Format it properly and return only the text:\n\n{extracted_text}",
                        ])
                        processed_text = response.text
                    except Exception as e:
                        print(f"    Using raw text (Gemini error: {e})")
                        processed_text = extracted_text
                    
                    # Format text with OpenAI
                    formatted_text = self.format_text_with_openai(processed_text)
                    
                    # Save to database
                    self.db.add_ocr_result(doc_id, page_num + 1, formatted_text)
                    print(f"    Extracted {len(formatted_text)} characters")
                else:
                    print(f"    Page {page_num + 1} appears to be empty or unreadable")
        
        # Generate summary of entire document
        print(f"  Generating summary...")
        full_text = self.db.get_document_text(doc_id)
        summary = self.summarize_with_claude(full_text)
        if summary:
            self.db.add_summary(doc_id, summary)
            print(f"  ✓ Summary generated")
        
        # Update document status to completed
        self.db.update_document_status(doc_id, 'completed')
        
        print(f"✓ Completed: {filename}")
        return doc_id


def main():
    """Main function to start the PDF OCR pipeline"""
    print("PDF OCR Pipeline Started (Gemini API)\n")
    
    # Initialize database
    db = Database()
    db.init_db()
    
    # Initialize processor
    processor = PDFOCRProcessor()
    
    # Process PDFs from uploads folder
    uploads_dir = Config.UPLOAD_FOLDER
    if os.path.exists(uploads_dir):
        pdf_files = [f for f in os.listdir(uploads_dir) if f.endswith('.pdf')]
        
        if pdf_files:
            for pdf_file in pdf_files:
                pdf_path = os.path.join(uploads_dir, pdf_file)
                processor.process_pdf(pdf_path)
        else:
            print("No PDF files found in uploads/ folder")
            print("Add PDF files to uploads/ and run again")
    else:
        print("uploads/ folder not found")
    

if __name__ == "__main__":
    main()
