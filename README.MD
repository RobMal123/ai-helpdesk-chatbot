# AI Helpdesk Chatbot with Monitoring and ETL

A complete AI chatbot system that answers questions using RAG (Retrieval Augmented Generation) on PDF documents, with scheduled ETL processes and comprehensive monitoring.

## Features

- 🤖 **AI Chatbot**: Using LlamaIndex and Google Gemini for question answering
- 📚 **RAG**: Vector search on PDF knowledge base
- 🔄 **ETL Pipeline**: Scheduled download and processing of PDF documents
- 🐳 **Docker**: Containerized application with Docker Compose
- 📊 **Monitoring**: Prometheus metrics, Grafana dashboards, and Discord alerts
- 🚀 **CI/CD**: Automated deployment with GitHub Actions

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ ETL Process │───▶│ Vector Store │◀───│ AI Chatbot  │
└─────────────┘    └─────────────┘    └─────────────┘
       │                                      │
       │                                      │
       ▼                                      ▼
┌─────────────┐                       ┌─────────────┐
│ Monitoring  │◀──────────────────────│ API Server  │
└─────────────┘                       └─────────────┘
```

## Getting Started

### Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Google Gemini API key

### Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/ai-helpdesk-chatbot.git
   cd ai-helpdesk-chatbot
   ```

2. Create a virtual environment and install dependencies:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your configuration:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.0-flash-lite
   ```

### Running the Application

#### Development Mode

```
uvicorn app.main:app --reload
```

#### Using Docker

```
cd docker
docker-compose up -d
```

### Usage

1. Place PDF files in the `data/raw` directory or add URLs to `data/pdf_urls.txt`
2. Run the ETL process to download and process PDFs:
   ```
   python -m etl.schedule_etl
   ```
3. Access the API at http://localhost:8000
4. Access Prometheus at http://localhost:9090
5. Access Grafana at http://localhost:3000

## Project Structure

- `app/` - FastAPI server and chatbot logic
- `etl/` - Data processing pipeline
- `monitor/` - Monitoring and alerting
- `docker/` - Docker configuration
- `.github/` - CI/CD workflows

## Configuration

Configuration is managed via environment variables in `.env` file:

- `GEMINI_API_KEY` - Your Google Gemini API key
- `GEMINI_MODEL` - Model to use (e.g., gemini-2.0-flash-lite)
- `APP_PORT` - Port to run the API server (default: 8000)
- `ETL_SCHEDULE_HOUR` - Hour to run daily ETL job (0-23)
- `DISCORD_WEBHOOK_URL` - Discord webhook for alerts (optional)

## License

MIT
