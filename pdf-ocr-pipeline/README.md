# PDF OCR Pipeline

A powerful PDF processing application that extracts text, formats it intelligently, and generates summaries using multiple AI services.

## Features

- 📄 **PDF Text Extraction** - Extracts text from PDF files using PyPDF2
- 🤖 **AI-Powered Processing** - Uses Gemini for text analysis and extraction
- ✨ **Intelligent Formatting** - OpenAI formats and cleans extracted text
- 📝 **Automatic Summarization** - Claude generates document summaries
- 🌐 **Web Interface** - Easy-to-use Streamlit interface
- 💾 **Database Storage** - SQLite stores all results and summaries
- 📊 **Results Management** - View, download, and delete processed documents

## Technologies Used

- **Gemini API** - Text analysis and OCR enhancement
- **OpenAI API** - Text formatting and cleanup
- **Anthropic Claude API** - Document summarization
- **Streamlit** - Web interface
- **PyPDF2** - PDF text extraction
- **SQLite** - Local database storage

## Prerequisites

- Python 3.8 or higher
- API Keys:
  - Google Gemini API key ([Get it here](https://aistudio.google.com/app/apikey))
  - OpenAI API key ([Get it here](https://platform.openai.com/api-keys))
  - Anthropic API key ([Get it here](https://console.anthropic.com/))

## Installation

1. **Clone or download this repository**

2. **Navigate to the project directory**
   ```bash
   cd pdf-ocr-pipeline
   ```

3. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

4. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Mac/Linux:
     ```bash
     source venv/bin/activate
     ```

5. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

6. **Configure API keys**
   
   Edit the `.env` file and add your API keys:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

## Usage

### Running the Web Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Using the Application

1. **Upload & Process**
   - Click "Choose a PDF file" to upload a document
   - Click "🚀 Process PDF" to start processing
   - View recent documents below

2. **View Results**
   - Navigate to "View Results" in the sidebar
   - Click "View" to see document details
   - View summaries and extracted text by page
   - Download results as text file
   - Delete documents using 🗑️ button

### Command Line Usage

You can also process PDFs via command line:

```bash
python main.py
```

Place PDF files in the `uploads/` folder before running.

## Project Structure

```
pdf-ocr-pipeline/
├── venv/                 # Virtual environment
├── uploads/              # PDF storage folder
├── main.py              # Core processing logic
├── app.py               # Streamlit web interface
├── config.py            # Configuration and API keys
├── database.py          # SQLite database operations
├── .env                 # API keys (DO NOT COMMIT)
├── .gitignore           # Git ignore rules
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## How It Works

1. **Upload** - User uploads a PDF file through the web interface
2. **Extract** - PyPDF2 extracts raw text from each page
3. **Analyze** - Gemini processes and cleans the extracted text
4. **Format** - OpenAI formats the text for readability
5. **Summarize** - Claude generates a concise summary of the entire document
6. **Store** - All results are saved in SQLite database
7. **Display** - Results are shown in the web interface with download options

## Database Schema

### pdf_documents
- `id` - Primary key
- `filename` - Original PDF filename
- `upload_date` - Upload timestamp
- `file_path` - Path to PDF file
- `status` - Processing status (pending/completed)

### ocr_results
- `id` - Primary key
- `document_id` - Foreign key to pdf_documents
- `page_number` - Page number
- `extracted_text` - Processed text content
- `created_date` - Creation timestamp

### summaries
- `id` - Primary key
- `document_id` - Foreign key to pdf_documents
- `summary_text` - Generated summary
- `created_date` - Creation timestamp

## Configuration

Edit `config.py` to customize:
- `MAX_FILE_SIZE` - Maximum upload size (default: 10MB)
- `UPLOAD_FOLDER` - PDF storage location
- `DATABASE_PATH` - SQLite database file path

## Troubleshooting

### Module not found errors
Make sure you've activated the virtual environment and installed all dependencies:
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

### API errors
- Verify your API keys are correctly set in `.env`
- Check your API quotas and limits
- Ensure you have active subscriptions for the APIs

### Streamlit not recognized
Install streamlit in the virtual environment:
```bash
venv\Scripts\pip install streamlit
```

## Notes

- The application uses the deprecated `google.generativeai` package. Consider migrating to `google.genai` in the future.
- Processing time varies based on PDF size and API response times
- All data is stored locally in SQLite database
- PDF files are stored in the `uploads/` folder

## Security

⚠️ **Important**: Never commit your `.env` file or expose your API keys. The `.gitignore` file is configured to exclude sensitive files.

## License

This project is open source and available for educational and personal use.

## Support

For issues or questions, please check the troubleshooting section or review the code comments.
