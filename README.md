# 🌾 Samarth RAG Chatbot

A beautiful, animated Q&A chatbot application using Retrieval-Augmented Generation (RAG) for agricultural and climate-related queries.

## ✨ Features

- **Beautiful UI**: Animated welcome screen with typing effects and smooth transitions
- **No Authentication**: Simple, user-friendly interface without login requirements
- **Gemini AI Integration**: Powered by Google Gemini for intelligent responses
- **Local Vector Storage**: FAISS-based vector store with local file storage
- **Synchronous Processing**: No external dependencies like Redis or Celery
- **Export Chat History**: Save conversations as CSV files

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Gemini API

```bash
# Get API key from https://aistudio.google.com/app/apikey
# Edit .env file:
GEMINI_API_KEY=your-actual-gemini-api-key-here
```

### 3. Prepare Data (Optional)

Place your CSV files in `data/raw/` directory. The application will automatically build a vector store from these files.

### 4. Run the Application

**Terminal 1 - Start the API:**
```bash
python src/main.py
```

**Terminal 2 - Start the UI:**
```bash
streamlit run src/ui/app.py
```

### 5. Use the Application

1. Open your browser to the Streamlit URL (usually `http://localhost:8501`)
2. Enjoy the animated welcome screen!
3. Click "🚀 Start Chat" to begin
4. Ask questions about agriculture and climate
5. Export your chat history using the sidebar

## 📁 Project Structure

```
├── src/
│   ├── main.py              # API entry point
│   ├── api/app.py           # FastAPI backend
│   ├── ui/app.py            # Streamlit frontend with animations
│   ├── core/
│   │   ├── vector_store.py  # FAISS vector storage
│   │   ├── rag_pipeline.py  # RAG logic
│   │   └── data_loader.py   # Data processing
│   ├── config/
│   │   └── settings.py      # Configuration management
│   └── utils/
│       ├── logger.py        # Logging utilities
│       └── security.py      # Input sanitization
├── scripts/
│   └── refresh_data.py      # Synchronous data refresh
├── data/
│   ├── raw/                 # CSV files go here
│   └── processed/           # Vector store files
├── requirements.txt         # Python dependencies
└── .env                    # Environment variables
```

## 🎨 UI Features

- **Animated Welcome Screen**: Beautiful gradient background with typing animation
- **Smooth Transitions**: Fade-in effects and slide animations
- **Responsive Design**: Works on desktop and mobile
- **Chat Export**: Download conversation history as CSV
- **LLM Indicator**: Shows which model is being used

## 🔧 Configuration

All settings are in `.env`:

```bash
# Gemini API
GEMINI_API_KEY=your-key-here  # Gemini API key

# Vector Store
MAX_CHUNK_SIZE=1000           # Text chunk size for processing
EMBEDDING_MODEL=all-MiniLM-L6-v2  # Embedding model
```

## 🛠 Troubleshooting

**Import Error**: Make sure you're running from the project root directory.

**No Vector Store**: Place CSV files in `data/raw/` and restart the API.

**LLM Connection Issues**: Check your API keys or Ollama installation.

## 📝 License

MIT License - feel free to use for your projects!