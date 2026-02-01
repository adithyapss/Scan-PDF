"""
SQLite Database Setup and Operations
"""
import sqlite3
from config import Config


class Database:
    """Database handler for PDF OCR pipeline"""
    
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
    
    def init_db(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pdf_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_path TEXT NOT NULL,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ocr_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                page_number INTEGER,
                extracted_text TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES pdf_documents (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                summary_text TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES pdf_documents (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database initialized successfully")
    
    def add_document(self, filename, file_path):
        """Add a new PDF document to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO pdf_documents (filename, file_path) VALUES (?, ?)',
            (filename, file_path)
        )
        doc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return doc_id
    
    def add_ocr_result(self, document_id, page_number, extracted_text):
        """Add OCR results for a document page"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO ocr_results (document_id, page_number, extracted_text) VALUES (?, ?, ?)',
            (document_id, page_number, extracted_text)
        )
        conn.commit()
        conn.close()
    
    def add_summary(self, document_id, summary_text):
        """Add summary for a document"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO summaries (document_id, summary_text) VALUES (?, ?)',
            (document_id, summary_text)
        )
        conn.commit()
        conn.close()
    
    def get_document_text(self, document_id):
        """Get all extracted text for a document"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT extracted_text FROM ocr_results WHERE document_id = ? ORDER BY page_number',
            (document_id,)
        )
        results = cursor.fetchall()
        conn.close()
        return '\n\n'.join([r[0] for r in results])
    
    def update_document_status(self, document_id, status):
        """Update the status of a document"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE pdf_documents SET status = ? WHERE id = ?',
            (status, document_id)
        )
        conn.commit()
        conn.close()
    
    def delete_document(self, document_id):
        """Delete a document and all related data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete OCR results
        cursor.execute('DELETE FROM ocr_results WHERE document_id = ?', (document_id,))
        
        # Delete summaries
        cursor.execute('DELETE FROM summaries WHERE document_id = ?', (document_id,))
        
        # Delete document
        cursor.execute('DELETE FROM pdf_documents WHERE id = ?', (document_id,))
        
        conn.commit()
        conn.close()
