<div align="center">

# 🤖 Mini RAG App

### *Your Documents, Supercharged with AI* ✨

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

**Upload. Process. Ask. Get Answers.** 🚀

Transform your documents into an intelligent Q&A system powered by RAG (Retrieval Augmented Generation)

[Quick Start](#-quick-start) • [What is RAG?](#-understanding-rag-retrieval-augmented-generation) • [API Docs](#-api-playground) • [Examples](#-real-examples)

</div>

---

## 📖 What is Mini RAG App?

**Mini RAG App** is a production-ready, **scalable** implementation of a **Retrieval Augmented Generation (RAG)** system built with modern Python technologies. It transforms your documents into an intelligent knowledge base that can answer questions with accuracy and context.

### 🎯 The Problem It Solves

Traditional chatbots and LLMs have a critical limitation: they can only answer based on their training data, which means:
- ❌ No knowledge of YOUR specific documents
- ❌ Can't access proprietary or recent information
- ❌ Prone to "hallucinations" (making up answers)

**Mini RAG App solves this** by grounding AI responses in your actual documents, ensuring accurate, verifiable answers.

### 🔌 Scalable Multi-Provider Architecture

This project is built with **flexibility and scalability** in mind. Thanks to the **Factory Pattern** design, you can seamlessly switch between multiple LLM providers without changing your code:

<table>
<tr>
<td align="center" width="33%">

### ☁️ **OpenAI**
**Cloud-based, powerful**

- GPT-3.5/GPT-4 for generation
- text-embedding-ada-002
- Best for production
- Pay-per-use pricing

</td>
<td align="center" width="33%">

### 🔮 **Cohere**
**Alternative cloud option**

- Command models
- Cohere embeddings
- Competitive pricing
- Great multilingual support

</td>
<td align="center" width="33%">

### 🦙 **Ollama**
**100% Local & Free**

- Runs on your machine
- No API costs
- Complete privacy
- Perfect for development

</td>
</tr>
</table>

**Switching providers?** Just change a few lines in your `.env` file. The application automatically adapts! 🎉

```env
# Switch from OpenAI to Ollama? Just update these:
GENERATION_BACKEND="OPENAI"  # or "COHERE"
EMBEDDING_BACKEND="OPENAI"   # or "COHERE"
```

The **Factory Pattern** implementation means:
- ✅ **Zero code changes** when switching providers
- ✅ **Easy to add new providers** (just implement the interface)
- ✅ **Test with Ollama locally**, deploy with OpenAI in production
- ✅ **Mix and match**: Use OpenAI for generation, Cohere for embeddings

---

## 🧠 Understanding RAG (Retrieval Augmented Generation)

### What is RAG?

**RAG** combines the power of **information retrieval** with **generative AI** to create a system that:
1. **Retrieves** relevant information from your documents
2. **Augments** the AI prompt with this context
3. **Generates** accurate answers based on retrieved facts

### The RAG Pipeline Explained

```
┌─────────────────────────────────────────────────────────────────┐
│                         RAG WORKFLOW                            │
└─────────────────────────────────────────────────────────────────┘

� STEP 1: DOCUMENT INGESTION
   ┌──────────────┐
   │ Your Document│  (PDF, TXT)
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Text Splitter│  Split into chunks (e.g., 500 chars with 50 overlap)
   └──────┬───────┘
          │
          ▼
   ┌──────────────────────────────────┐
   │ Chunks: ["chunk1", "chunk2", ...] │
   └──────────────────────────────────┘

🧮 STEP 2: EMBEDDING & INDEXING
   ┌──────────────┐
   │ Each Chunk   │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ LLM Embedding│  Convert text → vector (e.g., [0.23, -0.45, ...])
   │   Model      │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Qdrant Vector│  Store vectors for fast similarity search
   │   Database   │
   └──────────────┘

🔍 STEP 3: QUERY & RETRIEVAL (When user asks a question)
   ┌──────────────────────┐
   │ User Question:       │
   │ "What is the main    │
   │  topic?"             │
   └──────┬───────────────┘
          │
          ▼
   ┌──────────────┐
   │ Embed Query  │  Convert question → vector
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Vector Search│  Find most similar chunks (cosine similarity)
   │  in Qdrant   │
   └──────┬───────┘
          │
          ▼
   ┌────────────────────────────┐
   │ Top-K Relevant Chunks      │
   │ ["chunk 5", "chunk 12", ...]│
   └────────────────────────────┘

💬 STEP 4: GENERATION (RAG Magic!)
   ┌─────────────────────────────────────┐
   │ Prompt Template:                    │
   │                                     │
   │ Context: [Retrieved chunks]         │
   │ Question: [User question]           │
   │                                     │
   │ Answer based ONLY on the context.  │
   └──────┬──────────────────────────────┘
          │
          ▼
   ┌──────────────┐
   │ LLM (GPT/    │  Generate answer grounded in context
   │  Cohere/     │
   │  Ollama)     │
   └──────┬───────┘
          │
          ▼
   ┌──────────────────────────────────┐
   │ ✅ Accurate Answer               │
   │ "The main topic is..."           │
   │ (Based on YOUR documents!)       │
   └──────────────────────────────────┘
```

### Why RAG is Powerful

| Traditional LLM | RAG-Enhanced LLM |
|----------------|------------------|
| ❌ Limited to training data | ✅ Uses YOUR documents |
| ❌ Can't access new info | ✅ Always up-to-date |
| ❌ Hallucinates answers | ✅ Grounded in facts |
| ❌ No source attribution | ✅ Can cite sources |
| ❌ Generic responses | ✅ Domain-specific answers |

### Real-World Example

**Without RAG:**
```
User: "What was our Q3 revenue?"
LLM: "I don't have access to your company's financial data."
```

**With RAG:**
```
User: "What was our Q3 revenue?"
RAG System:
  1. Searches your uploaded financial reports
  2. Finds: "Q3 2024 revenue reached $2.5M..."
  3. LLM generates: "According to your Q3 report, revenue was $2.5M,
     representing a 15% increase from Q2."
```

---

## 🎯 What Can It Do?

<table>
<tr>
<td width="50%">

### �📤 **Smart Document Processing**
- Drop in your PDFs or text files
- Auto-chunking with intelligent overlap
- Metadata extraction & organization

</td>
<td width="50%">

### 🧠 **AI-Powered Search**
- Semantic search (not just keywords!)
- Vector embeddings via OpenAI/Cohere/Ollama
- Lightning-fast Qdrant vector DB

</td>
</tr>
<tr>
<td width="50%">

### 💬 **RAG Question Answering**
- Ask questions in natural language
- Get answers grounded in YOUR docs
- No hallucinations, just facts

</td>
<td width="50%">

### 🎨 **Multi-Project Support**
- Organize docs into projects
- Isolated knowledge bases
- Easy project switching

</td>
</tr>
</table>

---

## ⚡ Quick Start

### 1️⃣ **Clone & Install**

```bash
# Clone the repo
git clone <your-repo-url>
cd mini-rag-app

# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r src/requirements.txt
```

### 2️⃣ **Setup MongoDB**

<details>
<summary><b>🐳 Option A: Docker (Recommended)</b></summary>

```bash
cd docker
docker-compose up -d
```

That's it! MongoDB will be running on `localhost:27017` 🎉

</details>

<details>
<summary><b>💻 Option B: Local MongoDB</b></summary>

**Windows:**
1. Download from [MongoDB Download Center](https://www.mongodb.com/try/download/community)
2. Install with default settings
3. MongoDB will auto-start as a service

**Mac:**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Linux:**
```bash
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
```

Verify it's running:
```bash
mongosh --eval "db.version()"
```

</details>

### 3️⃣ **Configure Your LLM**

```bash
cd src
cp .env.example .env
```

Now edit `.env` and choose your AI provider:

<details>
<summary><b>🌐 OpenAI (Cloud)</b></summary>

```env
GENERATION_BACKEND="OPENAI"
EMBEDDING_BACKEND="OPENAI"
OPENAI_API_KEY="sk-your-actual-key-here"
OPENAI_API_URL="https://api.openai.com/v1/"
GENERATION_MODEL_ID="gpt-3.5-turbo"
EMBEDDING_MODEL_ID="text-embedding-ada-002"
EMBEDDING_MODEL_SIZE=1536
```

</details>

<details>
<summary><b>🦙 Ollama (Local & Free!)</b></summary>

First, install Ollama from [ollama.ai](https://ollama.ai), then:

```bash
# Pull the models
ollama pull qwen2.5-coder:7b
ollama pull nomic-embed-text
```

Update `.env`:
```env
GENERATION_BACKEND="OPENAI"
EMBEDDING_BACKEND="OPENAI"
OPENAI_API_KEY="not-needed"
OPENAI_API_URL="http://localhost:11434/v1/"
GENERATION_MODEL_ID="qwen2.5-coder:7b"
EMBEDDING_MODEL_ID="nomic-embed-text"
EMBEDDING_MODEL_SIZE=768
```

</details>

<details>
<summary><b>🔮 Cohere</b></summary>

```env
GENERATION_BACKEND="COHERE"
EMBEDDING_BACKEND="COHERE"
COHERE_API_KEY="your-cohere-key"
```

</details>

### 4️⃣ **Launch! 🚀**

```bash
cd src
uvicorn main:app --reload --port 8000
```

**🎉 Done!** Visit `http://localhost:8000/docs` for the interactive API playground.

---

## 🎮 Real Examples

### Example 1: Upload & Query a Document

```bash
# 1. Upload your document
curl -X POST "http://localhost:8000/api/v1/data/upload/my_project" \
  -F "file=@research_paper.pdf"

# Response: {"signal": "file_upload_success", "file_id": "abc123"}

# 2. Process it into chunks
curl -X POST "http://localhost:8000/api/v1/data/process/my_project" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "abc123",
    "chunk_size": 500,
    "overlap_size": 50,
    "do_reset": 0
  }'

# Response: {"signal": "processing_success", "inserted_chunks": 42}

# 3. Index into vector database
curl -X POST "http://localhost:8000/api/v1/nlp/index/push/my_project" \
  -H "Content-Type: application/json" \
  -d '{"do_reset": 0}'

# Response: {"signal": "insert_into_vectordb_success", "inserted_items_count": 42}

# 4. Ask a question!
curl -X POST "http://localhost:8000/api/v1/nlp/index/answer/my_project" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "What are the main findings?",
    "limit": 5
  }'

# Response: {"signal": "rag_answer_success", "answer": "The main findings are..."}
```

### Example 2: Search for Similar Content

```bash
curl -X POST "http://localhost:8000/api/v1/nlp/index/search/my_project" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "machine learning algorithms",
    "limit": 3
  }'
```

Returns the top 3 most relevant chunks from your documents!

---

## 📚 API Playground

Once running, explore the **auto-generated interactive docs**:

- **Swagger UI**: http://localhost:8000/docs 👈 *Try it live!*
- **ReDoc**: http://localhost:8000/redoc 👈 *Beautiful docs*

### Core Endpoints

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/api/v1/data/upload/{project_id}` | POST | 📤 Upload a file |
| `/api/v1/data/process/{project_id}` | POST | ✂️ Chunk the document |
| `/api/v1/nlp/index/push/{project_id}` | POST | 🗄️ Index into vector DB |
| `/api/v1/nlp/index/search/{project_id}` | POST | 🔍 Semantic search |
| `/api/v1/nlp/index/answer/{project_id}` | POST | 💬 RAG Q&A |
| `/api/v1/nlp/index/info/{project_id}` | GET | ℹ️ Get index stats |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     FastAPI Server                      │
│                  (Async, High Performance)              │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
   ┌────────┐  ┌─────────┐  ┌──────────┐
   │ Upload │  │ Process │  │   RAG    │
   │  API   │  │   API   │  │   API    │
   └───┬────┘  └────┬────┘  └────┬─────┘
       │            │            │
       ▼            ▼            ▼
   ┌────────────────────────────────────┐
   │         Controllers Layer          │
   │  (Business Logic & Orchestration)  │
   └───────────────┬────────────────────┘
                   │
       ┌───────────┼───────────┐
       │           │           │
       ▼           ▼           ▼
   ┌────────┐ ┌────────┐ ┌──────────┐
   │MongoDB │ │Qdrant  │ │   LLM    │
   │(Chunks)│ │(Vectors)│ │(OpenAI/  │
   │        │ │        │ │ Cohere/  │
   │        │ │        │ │ Ollama)  │
   └────────┘ └────────┘ └──────────┘
```

---

## 🗂️ Project Structure

```
mini-rag-app/
│
├── 🚀 src/
│   ├── main.py                    # FastAPI app entry point
│   ├── .env.example               # Config template
│   │
│   ├── 🛣️ routes/                 # API endpoints
│   │   ├── data.py                # Upload & processing
│   │   ├── nlp.py                 # Search & RAG
│   │   └── schemes/               # Request/response models
│   │
│   ├── 🎮 controllers/            # Business logic
│   │   ├── DataController.py      # File validation
│   │   ├── ProcessController.py   # Document chunking
│   │   ├── NLPController.py       # RAG operations
│   │   └── ProjectController.py   # Project management
│   │
│   ├── 💾 models/                 # Database models
│   │   ├── ProjectModel.py
│   │   ├── AssetModel.py
│   │   ├── ChunkModel.py
│   │   └── db_schemes.py
│   │
│   ├── 🔌 stores/                 # External integrations
│   │   ├── llm/                   # LLM providers (Factory Pattern)
│   │   │   ├── LLMProviderFactory.py
│   │   │   ├── providers/
│   │   │   │   ├── OpenAIProvider.py
│   │   │   │   └── CoHereProvider.py
│   │   │   └── templates/         # Prompt templates
│   │   │
│   │   └── vectordb/              # Vector DB (Factory Pattern)
│   │       ├── VectorDBProviderFactory.py
│   │       └── providers/
│   │           └── QdrantDBProvider.py
│   │
│   └── 📦 assets/                 # Uploaded files
│
├── 🐳 docker/
│   └── docker-compose.yml         # MongoDB setup
│
└── 📄 requirements.txt            # Python packages
```

---

## 🔧 Configuration Deep Dive

### Essential Settings

```env
# App Basics
APP_NAME="mini-rag"
FILE_ALLOWED_TYPES=["text/plain","application/pdf"]
FILE_MAX_SIZE=10  # MB

# Database
MONGODB_URL="mongodb://localhost:27017"
MONGODB_DATABASE="mini_rag_db"

# Vector Database
VECTOR_DB_BACKEND="QDRANT"
VECTOR_DB_PATH="qdrant_db"
VECTOR_DB_DISTANCE_METHOD="cosine"

# Generation Settings
GENERATION_DEFAULT_MAX_TOKENS=200
GENERATION_DEFAULT_TEMPERATURE=0.1
INPUT_DEFAULT_MAX_CHARACTERS=1024
```

---

## 🐛 Troubleshooting

<details>
<summary><b>❌ "Connection refused to MongoDB"</b></summary>

**Check if MongoDB is running:**
```bash
# Docker
docker ps | grep mongodb

# Local
mongosh --eval "db.version()"
```

**Fix:**
```bash
# Docker
cd docker && docker-compose up -d

# Local
sudo systemctl start mongod  # Linux
brew services start mongodb-community  # Mac
```

</details>

<details>
<summary><b>❌ "Collection not found" in Qdrant</b></summary>

You forgot to index! Run:
```bash
# 1. Process documents first
POST /api/v1/data/process/{project_id}

# 2. Then index them
POST /api/v1/nlp/index/push/{project_id}
```

</details>

<details>
<summary><b>❌ "processing_failed" error</b></summary>

**Common causes:**
- Empty file uploaded
- Unsupported file type
- File too large (check `FILE_MAX_SIZE` in `.env`)

**Debug:**
```bash
# Check file size
ls -lh path/to/file

# Check file type
file path/to/file
```

</details>

<details>
<summary><b>❌ OpenAI/Cohere API errors</b></summary>

**Checklist:**
- ✅ API key is correct in `.env`
- ✅ You have API credits
- ✅ API URL is correct
- ✅ Model ID exists

**For Ollama users:**
```bash
# Make sure Ollama is running
ollama serve

# Check available models
ollama list
```

</details>

<details>
<summary><b>❌ Module import errors</b></summary>

```bash
# Reinstall dependencies
pip install -r src/requirements.txt --force-reinstall

# Or use a fresh venv
deactivate
rm -rf .venv
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r src/requirements.txt
```

</details>

---

## 🚀 Advanced Usage

### Batch Process All Files in a Project

```bash
# Don't specify file_id to process ALL files
curl -X POST "http://localhost:8000/api/v1/data/process/my_project" \
  -H "Content-Type: application/json" \
  -d '{
    "chunk_size": 500,
    "overlap_size": 50,
    "do_reset": 1
  }'
```

### Reset & Re-index

```bash
# Clear existing chunks and re-process
curl -X POST "http://localhost:8000/api/v1/data/process/my_project" \
  -d '{"do_reset": 1, "chunk_size": 500, "overlap_size": 50}'

# Clear vector DB and re-index
curl -X POST "http://localhost:8000/api/v1/nlp/index/push/my_project" \
  -d '{"do_reset": 1}'
```

### Check Index Statistics

```bash
curl -X GET "http://localhost:8000/api/v1/nlp/index/info/my_project"
```

---

## 🤝 Contributing

We love contributions! Here's how:

1. **Fork** the repo
2. **Create** a feature branch: `git checkout -b feature/awesome-feature`
3. **Commit** your changes: `git commit -m 'Add awesome feature'`
4. **Push** to the branch: `git push origin feature/awesome-feature`
5. **Open** a Pull Request

---

## 📜 License

MIT License - feel free to use this in your projects!

---

## 🌟 Star Us!

If you find this useful, give it a ⭐ on GitHub!

---

<div align="center">

**Built with ❤️ using FastAPI, LangChain, Qdrant, and MongoDB**

[Report Bug](../../issues) • [Request Feature](../../issues) • [Documentation](http://localhost:8000/docs)

</div>