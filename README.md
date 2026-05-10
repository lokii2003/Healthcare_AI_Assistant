# 🏥 Healthcare AI Assistant

A **conversational AI healthcare assistant** that answers medical questions using **Retrieval-Augmented Generation (RAG)** and provides appointment booking support.

> ⚠️ **Disclaimer**: This tool is for informational purposes only, not medical diagnosis. Always consult healthcare professionals for medical decisions.

---

## 📋 Overview

**What does this project do?**

1. **Answer medical questions** using AI trained on real medical data
2. **Search medical knowledge** using semantic similarity (RAG)
3. **Book appointments** with automatic specialist recommendations
4. **Provide safe AI responses** with built-in safeguards against hallucination

**How it works**:
- User asks a healthcare question
- System retrieves relevant medical information from a knowledge base
- AI generates a grounded answer based on retrieved documents
- Response is displayed with source attribution

---

## 🔗 Source Code

- **GitHub Repository**: [Add your repository link here]
- **Google Derive Source Code**: Available upon request

---

## 🚀 Quick Setup

### Prerequisites
- Python 3.11+
- Ollama installed ([ollama.ai](https://ollama.ai))
- Mistral model pulled: `ollama pull mistral`

### Installation Steps

```bash
# 1. Activate conda environment
conda activate health

# 2. Install dependencies
pip install -r requirements.txt

# 3. Convert XML medical data to text (one-time)
python -m app.xml_converter

# 4. Start Ollama server (keep in separate terminal)
ollama serve

# 5. Start FastAPI backend (in another terminal)
python -m uvicorn app.main:app --reload

# 6. Start Streamlit frontend (in another terminal)
streamlit run frontend/streamlit_app.py
```

**What each command does:**
- `app.xml_converter` → Converts medical XML files to text and creates vector embeddings
- `uvicorn` → Starts the backend API server (port 8000)
- `streamlit` → Launches the web interface (port 8501)

**Result**: Open browser to `http://localhost:8501` and start chatting!

---

## 🏗️ System Architecture

```
User Interface (Streamlit)
    ↓
FastAPI Backend
    ↓
Intent Detection (RAG vs Appointment)
    ├─ RAG Path:                    ├─ Appointment Path:
    │  ├─ Embed question            │  ├─ Detect specialization
    │  ├─ Search ChromaDB           │  ├─ Book appointment
    │  ├─ Get medical context       │  └─ Send confirmation email
    │  └─ Call Ollama Mistral       │
    └─ Return answer                └─ Return confirmation

ChromaDB (Vector Store)
Ollama Mistral 7B (LLM)
SQLite (Appointments Database)
---

## 📡 API Examples

### Check API Health

```bash
curl http://localhost:8000/health
```

Response:
```json
{"status": "healthy", "llm_model": "mistral"}

### Ask a Medical Question

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the symptoms of diabetes?"}'
```

Response:
```json
{
  "answer": "Diabetes is a chronic condition characterized by high blood sugar levels...",
  "sources": ["0000015_1.xml", "0000016_1.xml"],
  "intent": "rag"
}
```

---

## 💡 Example Questions & Responses

**Q1: What causes high blood pressure?**  
A: High Blood Pressure, also known as hypertension, is a condition characterized by consistently elevated blood pressure in the arteries....

**Q2: What are the symptoms of a heart attack?**  
A: The symptoms of a heart attack, as described in the provided context, include chest discomfort (pressure, squeezing, or pain),...

**Q3: How is diabetes diagnosed?**  
A: Diabetes is diagnosed through blood tests. The symptoms can include being very thirsty, urinating often, feeling very hungry or tired, losing weight without trying, ...

**Q4: What specialization should I see for back pain?**  
A: In the provided context, no specific healthcare professional specialization for back pain treatment is mentioned. However, it's common to seek help from a primary care physician,...

**Q5: How do I book an appointment?**  
A: Available Specializations: • Cardiologist • Dermatologist • Neurologist • Orthopedic • Ophthalmologist • Dentist • Gastroenterologist • Pulmonologist .....
Please tell me your symptoms so I can recommend the right specialist, or go directly to the Book Appointment page to choose your specialization....

---

## 📚 Dataset & Knowledge Base

**Data Source**: MedQuAD [Dataset](https://github.com/abachaa/MedQuAD)

**Medical Domains** (12 sources):
- Cancer information (cancer.gov)
- Genetic & rare diseases
- General health topics (MedlinePlus)
- Neurological disorders (NINDS)
- Heart & lung diseases (NHLBI)
- CDC disease information
- Kidney & digestive diseases (NIDDK)
- Senior health information
- Drug information
- Herbs & supplements

**Data Processing**:
1. XML files parsed to extract Q&A pairs
2. Converted to plain text with medical context
3. Split into 500-character chunks with overlap
4. Embedded using sentence-transformers model
5. Indexed in ChromaDB for fast semantic search

---

## 🐳 Docker Support

A `Dockerfile` and `docker-compose.yml` are included for containerized deployment.

```bash
docker-compose up --build
```

**Note**: Ollama must run on the host machine (Docker connects via `host.docker.internal`).

---

## 🛠️ Technical Details

### LLM (Language Model)

- **Model**: Ollama Mistral 7B
- **Purpose**: Generate medical answers based on retrieved context
- **Temperature**: 0.1 (factual, deterministic responses)
- **Runs locally** on your machine (no cloud API required)

### Embedding Model

- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Purpose**: Convert text to vectors for semantic search
- **Dimensions**: 384-d vectors
- **Speed**: ~100 embeddings/second

### Vector Database

- **Database**: ChromaDB
- **Purpose**: Store and retrieve medical document embeddings
- **Search**: Cosine similarity for top-4 most relevant documents
- **Persistence**: Local file storage in `./vector_store/`

### Healthcare Safety Prompting

The system includes strict safeguards:
- ✅ Answers only from retrieved documents (no hallucination)
- ✅ Forbids medical diagnosis and drug prescriptions
- ✅ Always includes medical disclaimers
- ✅ Attributes sources to specific documents
- ✅ Recommends consulting healthcare professionals

### Agent Workflow

```
User Question
    ↓
[Intent Classification]
    ├─ If appointment keywords detected → Appointment agent
    └─ If medical keywords detected → RAG agent
    ↓
[RAG Agent Path]
    ├─ Embed question using sentence-transformers
    ├─ Search ChromaDB for 4 most similar documents
    ├─ Build context from retrieved chunks
    ├─ Send to Ollama Mistral with system prompt
    ├─ Extract sources from metadata
    └─ Return answer + sources
```

---

## ⚠️ Limitations

1. **Not Medical Diagnosis**: System cannot diagnose diseases or replace doctors
2. **Knowledge Base Dependent**: Quality depends on medical data available
3. **Local Inference**: Ollama must be running on your machine
4. **Single-User Demo**: Current version doesn't support multiple concurrent users
5. **No Internet Search**: Only uses pre-indexed medical documents
6. **English Only**: Currently supports English language only

---

## 🔮 Future Improvements

- 📄 PDF document upload and analysis
- 🌍 Multi-language support
- 🔐 User authentication and session management
- ☁️ Cloud deployment (Render, Railway, AWS)
- 🎤 Voice-based assistant
- 📱 Mobile app support
- 🏥 Integration with real appointment booking systems
- 📊 Advanced analytics dashboard

---

## 📁 Project Structure

```
Health_agent/
├── app/
│   ├── main.py              # FastAPI endpoints
│   ├── rag.py               # RAG retrieval pipeline
│   ├── llm.py               # Ollama LLM wrapper
│   ├── agent.py             # Intent routing & specialization
│   ├── embeddings.py        # ChromaDB document ingestion
│   ├── xml_converter.py     # XML → TXT conversion
│   ├── database.py          # Appointment database
│   ├── email_service.py     # Email notifications
│   ├── models.py            # Data validation schemas
│   ├── config.py            # Configuration settings
│   └── utils.py             # Logging utilities
├── frontend/
│   └── streamlit_app.py     # Web interface
├── data/                    # Medical XML knowledge base
├── txt_data/                # Converted text files
├── vector_store/            # ChromaDB persistence
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container configuration
├── docker-compose.yml       # Multi-container setup
└── README.md                # This file
```

---

## 👨‍💻 Author

**Lokesh Kumawat** — Mindbowser Hackathon 2025


