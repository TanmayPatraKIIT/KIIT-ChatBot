# KIIT ChatBot

A RAG-based (Retrieval-Augmented Generation) chatbot system for KIIT University that provides accurate, source-grounded information about notices, exam schedules, academic calendar, holidays, and more.

## 🎯 Features

- **Semantic Search**: Uses sentence-transformers and FAISS for intelligent document retrieval
- **RAG Pipeline**: Combines retrieval with LLaMA/Mistral LLM for accurate, source-referenced responses
- **Automated Scraping**: Continuously scrapes 4 KIIT data sources every 6 hours
- **Real-time Streaming**: WebSocket support for streaming chat responses
- **Caching**: Redis-based caching reduces response time and LLM costs
- **Background Tasks**: Celery workers handle scraping, indexing, and maintenance
- **API-First**: Clean REST API with comprehensive documentation
- **Admin Dashboard**: Monitor system health and trigger manual scrapes
- **Versioning**: Tracks changes to notices with full version history
- **Docker-Ready**: Complete containerized deployment with docker-compose

## 📋 Data Sources

The chatbot scrapes information from:

1. **General Notices** - https://kiit.ac.in/notices/
2. **Examination Notices** - http://coe.kiit.ac.in/notices.php
3. **Holiday Calendar** - https://kiit.ac.in/notices/holidays/
4. **Academic Calendar** - https://kiit.ac.in/academics/

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                   │
│                     [Chat UI | Search | Admin]              │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTP/WebSocket
┌────────────────▼────────────────────────────────────────────┐
│                    Backend API (FastAPI)                     │
│  ┌────────────┐  ┌──────────┐  ┌────────────┐             │
│  │   Chat     │  │  Search  │  │   Admin    │             │
│  │  Routes    │  │  Routes  │  │  Routes    │             │
│  └────────────┘  └──────────┘  └────────────┘             │
└──┬────────┬──────────┬─────────────┬──────────────────────┘
   │        │          │             │
┌──▼──┐  ┌─▼────┐  ┌──▼────┐    ┌──▼───────┐
│ RAG │  │Cache │  │Scraper│    │ Celery   │
│     │  │      │  │       │    │ Workers  │
└──┬──┘  └─┬────┘  └───────┘    └──────────┘
   │       │
┌──▼───┐ ┌▼─────┐  ┌──────────┐  ┌────────┐
│ LLM  │ │Redis │  │ MongoDB  │  │ FAISS  │
│(LLaMA│ │      │  │          │  │ Vector │
│)     │ │      │  │          │  │  Store │
└──────┘ └──────┘  └──────────┘  └────────┘
```

### Tech Stack

**Backend:**
- FastAPI (Python 3.11)
- LLaMA 3 8B via Ollama
- Sentence Transformers (all-mpnet-base-v2)
- FAISS for vector search
- MongoDB for data storage
- Redis for caching
- Celery for background tasks
- BeautifulSoup4 + Selenium for scraping

**Frontend:** (To be implemented)
- Next.js 14+ with TypeScript
- Tailwind CSS + shadcn/ui
- Zustand for state management
- WebSocket for streaming

**Infrastructure:**
- Docker + Docker Compose
- Prometheus metrics (optional)
- Structured JSON logging

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 8GB RAM (16GB recommended)
- 20GB free disk space

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd KIIT-ChatBot
```

2. **Create environment file:**
```bash
cd backend
cp .env.example .env
# Edit .env with your configurations
```

3. **Build and start all services:**
```bash
cd ..
docker-compose build
docker-compose up -d
```

4. **Initialize Ollama model (one-time):**
```bash
# Enter Ollama container
docker exec -it kiit_ollama bash

# Pull LLaMA 3 8B model (~4.7GB download)
ollama pull llama3:8b

# Verify
ollama list

# Exit container
exit
```

5. **Trigger initial data scrape:**
```bash
curl -X POST http://localhost:8000/api/admin/scrape \
  -H "X-API-Key: your_secret_api_key_for_admin_endpoints" \
  -H "Content-Type: application/json" \
  -d '{"source": "all"}'
```

6. **Access the application:**
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

### Verify Installation

```bash
# Check all services are running
docker-compose ps

# Check backend health
curl http://localhost:8000/api/health

# View backend logs
docker-compose logs -f backend

# Check MongoDB for notices
docker exec -it kiit_mongodb mongosh kiit_chatbot \
  --eval "db.notices.countDocuments({is_latest: true})"
```

## 📖 Usage

### API Endpoints

#### Chat

**POST /api/chat**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "When is the mid-semester exam?",
    "session_id": "optional_session_id"
  }'
```

Response:
```json
{
  "response": "Based on recent notices, the mid-semester exams are scheduled...",
  "sources": [
    {
      "title": "Mid-Semester Exam Schedule",
      "date": "2025-10-15",
      "url": "http://coe.kiit.ac.in/notices.php",
      "type": "exam"
    }
  ],
  "query_time_ms": 450,
  "from_cache": false
}
```

**WebSocket /ws/chat**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat');

ws.onopen = () => {
  ws.send(JSON.stringify({
    query: "When is the exam?",
    session_id: "abc123"
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'token') {
    console.log(data.content); // Stream tokens
  } else if (data.type === 'sources') {
    console.log(data.data); // Source references
  } else if (data.type === 'done') {
    console.log('Complete');
  }
};
```

#### Search

**GET /api/search/notices**
```bash
curl "http://localhost:8000/api/search/notices?q=exam&type=exam&limit=10"
```

**GET /api/search/recent**
```bash
curl "http://localhost:8000/api/search/recent?type=general&limit=5"
```

#### Admin (Requires API Key)

**POST /api/admin/scrape**
```bash
curl -X POST http://localhost:8000/api/admin/scrape \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"source": "all"}'
```

**GET /api/admin/stats**
```bash
curl http://localhost:8000/api/admin/stats \
  -H "X-API-Key: your_api_key"
```

## 🔧 Configuration

### Environment Variables

Edit `backend/.env`:

```bash
# MongoDB
MONGODB_URL=mongodb://mongodb:27017
MONGODB_DB_NAME=kiit_chatbot

# LLM Configuration
LLM_MODEL=llama3:8b  # or mistral:7b
LLM_BASE_URL=http://ollama:11434
LLM_TEMPERATURE=0.7

# Scraping
SCRAPE_INTERVAL_HOURS=6

# Security
API_KEY=your_secret_api_key_for_admin_endpoints

# CORS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/api/health
```

Response includes:
- Overall system status
- Individual service status (MongoDB, Redis, FAISS, LLM)
- Statistics (total notices, index size)

### Logs

```bash
# Backend logs
docker-compose logs -f backend

# Celery worker logs
docker-compose logs -f celery_worker

# All logs
docker-compose logs -f
```

### Metrics (Optional)

If Prometheus is enabled:
- Metrics endpoint: http://localhost:8000/metrics

## 🔄 Background Tasks

Celery handles scheduled tasks:

- **Scrape All Sources**: Every 6 hours
- **Rebuild FAISS Index**: Weekly (Sunday 2 AM)
- **Cleanup Old Versions**: Monthly (1st day, 3 AM)
- **Generate Daily Stats**: Daily at midnight

Manual trigger:
```bash
# Trigger scraping manually
curl -X POST http://localhost:8000/api/admin/scrape \
  -H "X-API-Key: your_api_key" \
  -d '{"source": "all"}'
```

## 🧪 Development

### Local Development (Without Docker)

1. **Install dependencies:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Start services:**
```bash
# Terminal 1: MongoDB
mongod --dbpath ./data/db

# Terminal 2: Redis
redis-server

# Terminal 3: Ollama
ollama serve

# Terminal 4: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 5: Celery Worker
celery -A app.workers.celery_app worker --loglevel=info
```

3. **Run tests:**
```bash
cd backend
pytest tests/ -v
```

## 📝 Project Structure

```
KIIT-ChatBot/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # API endpoints
│   │   ├── services/         # Core services (RAG, LLM, scraper, etc.)
│   │   ├── models/           # Pydantic models
│   │   ├── db/               # Database connections
│   │   ├── workers/          # Celery tasks
│   │   ├── utils/            # Utilities
│   │   ├── config.py         # Configuration
│   │   └── main.py           # FastAPI app
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/                  # To be implemented
├── docker-compose.yml
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- KIIT University for data sources
- Anthropic Claude for development assistance
- Ollama team for LLM deployment
- FastAPI and LangChain communities

## 📧 Contact

For issues or questions, please open an issue on GitHub.

---

**Note**: This chatbot provides information based on official KIIT sources. Always verify critical information with official KIIT administration.
