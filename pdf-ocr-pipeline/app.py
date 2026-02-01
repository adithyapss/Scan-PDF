"""
Streamlit Web Interface for PDF OCR Pipeline
"""
import streamlit as st
import os
import sqlite3
from main import PDFOCRProcessor
from database import Database
from config import Config


def init_database():
    """Initialize database on app start"""
    db = Database()
    db.init_db()


def get_all_documents():
    """Fetch all documents from database"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, filename, upload_date, status FROM pdf_documents
        ORDER BY upload_date DESC
    ''')
    documents = cursor.fetchall()
    conn.close()
    return documents


def get_document_details(doc_id):
    """Get OCR results and summary for a document"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get document info
    cursor.execute('SELECT filename FROM pdf_documents WHERE id = ?', (doc_id,))
    filename = cursor.fetchone()[0]
    
    # Get OCR results
    cursor.execute('''
        SELECT page_number, extracted_text FROM ocr_results
        WHERE document_id = ? ORDER BY page_number
    ''', (doc_id,))
    ocr_results = cursor.fetchall()
    
    # Get summary
    cursor.execute('SELECT summary_text FROM summaries WHERE document_id = ?', (doc_id,))
    summary_result = cursor.fetchone()
    summary = summary_result[0] if summary_result else None
    
    conn.close()
    return filename, ocr_results, summary


def main():
    st.set_page_config(page_title="PDF OCR Pipeline", layout="wide")
    st.title("📄 PDF OCR Pipeline")
    
    # Initialize database
    init_database()
    
    # Sidebar navigation
    page = st.sidebar.radio("Navigation", ["Upload & Process", "View Results"])
    
    if page == "Upload & Process":
        st.header("Upload & Process PDFs")
        
        # File uploader
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        
        if uploaded_file:
            # Save uploaded file
            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
            file_path = os.path.join(Config.UPLOAD_FOLDER, uploaded_file.name)
            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.success(f"✓ File uploaded: {uploaded_file.name}")
            
            # Process button
            if st.button("🚀 Process PDF"):
                with st.spinner("Processing... This may take a minute..."):
                    try:
                        processor = PDFOCRProcessor()
                        doc_id = processor.process_pdf(file_path)
                        st.success(f"✓ PDF processed successfully! Document ID: {doc_id}")
                        st.session_state.last_processed = doc_id
                    except Exception as e:
                        st.error(f"Error processing PDF: {str(e)}")
        
        # View results section
        st.divider()
        st.subheader("📊 Recent Documents")
        
        documents = get_all_documents()
        
        if not documents:
            st.info("No documents found. Upload and process a PDF to get started!")
        else:
            for doc_id, filename, upload_date, status in documents[:5]:  # Show last 5
                with st.expander(f"📁 {filename} - {upload_date}"):
                    if st.button("View Full Details", key=f"view_{doc_id}"):
                        st.session_state.selected_doc = doc_id
                        st.session_state.show_details = True
            
            # Show document details if selected
            if st.session_state.get("show_details") and "selected_doc" in st.session_state:
                st.divider()
                doc_id = st.session_state.selected_doc
                filename, ocr_results, summary = get_document_details(doc_id)
                
                st.subheader(f"📄 {filename}")
                
                # Show summary if available
                if summary:
                    st.markdown("### 📝 Summary")
                    st.write(summary)
                    st.divider()
                
                # Show OCR results by page
                st.markdown("### 📄 Extracted Text by Page")
                
                if ocr_results:
                    tabs = st.tabs([f"Page {page_num}" for page_num, _ in ocr_results])
                    
                    for tab, (page_num, text) in zip(tabs, ocr_results):
                        with tab:
                            st.text_area(
                                f"Text from page {page_num}",
                                value=text,
                                height=300,
                                disabled=True,
                                key=f"page_{doc_id}_{page_num}"
                            )
                
                # Download button
                if ocr_results and st.button("⬇️ Download Results as Text"):
                    all_text = "\n\n".join([f"--- Page {page_num} ---\n{text}" for page_num, text in ocr_results])
                    st.download_button(
                        label="Download",
                        data=all_text,
                        file_name=f"{filename.replace('.pdf', '')}_ocr_results.txt",
                        mime="text/plain"
                    )
    
    elif page == "View Results":
        st.header("📊 View Results")
        
        # Get all documents
        documents = get_all_documents()
        
        if not documents:
            st.info("No documents found. Upload and process a PDF first!")
        else:
            # Display documents as list
            for doc_id, filename, upload_date, status in documents:
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.subheader(f"📁 {filename}")
                    st.caption(f"Uploaded: {upload_date}")
                
                with col2:
                    if status == 'completed':
                        st.write("🟢 COMPLETED")
                    else:
                        st.write("🟡 PENDING")
                
                with col3:
                    if st.button("View", key=f"btn_{doc_id}"):
                        st.session_state.selected_doc = doc_id
                
                with col4:
                    if st.button("🗑️ Delete", key=f"del_{doc_id}"):
                        db = Database()
                        db.delete_document(doc_id)
                        st.success(f"Deleted {filename}")
                        st.rerun()
            
            # Show document details if selected
            if "selected_doc" in st.session_state:
                st.divider()
                doc_id = st.session_state.selected_doc
                filename, ocr_results, summary = get_document_details(doc_id)
                
                st.subheader(f"Details: {filename}")
                
                # Show summary if available
                if summary:
                    st.markdown("### 📝 Summary")
                    st.write(summary)
                    st.divider()
                
                # Show OCR results by page
                st.markdown("### 📄 Extracted Text by Page")
                
                if ocr_results:
                    # Create tabs for each page
                    tabs = st.tabs([f"Page {page_num}" for page_num, _ in ocr_results])
                    
                    for tab, (page_num, text) in zip(tabs, ocr_results):
                        with tab:
                            st.text_area(
                                f"Text from page {page_num}",
                                value=text,
                                height=300,
                                disabled=True,
                                key=f"page_{doc_id}_{page_num}"
                            )
                else:
                    st.info("No OCR results found for this document.")
                
                # Download results
                if st.button("⬇️ Download Results as Text"):
                    all_text = "\n\n".join([f"--- Page {page_num} ---\n{text}" for page_num, text in ocr_results])
                    st.download_button(
                        label="Download",
                        data=all_text,
                        file_name=f"{filename.replace('.pdf', '')}_ocr_results.txt",
                        mime="text/plain"
                    )


if __name__ == "__main__":
    main()
