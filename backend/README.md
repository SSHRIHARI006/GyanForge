# GyanForge Backend

GyanForge is an AI-powered adaptive learning platform that creates personalized learning modules with notes, videos, assignments, and quizzes.

## Features

- Generate personalized learning modules based on user prompts
- Intelligent video recommendations using Gemini and Pinecone
- LaTeX assignments with PDF export
- Quizzes with automatic grading
- Adaptive learning path based on user progress

## Tech Stack

- **FastAPI**: Async API framework
- **SQLModel**: Single-definition models for SQLAlchemy + Pydantic
- **Gemini 2.0 Flash**: Core AI model for content generation
- **LangChain**: For RAG and AI components
- **Pinecone**: Vector database for semantic search

## Setup

### Prerequisites

- Python 3.9+
- uv or pip/poetry for package management
- LaTeX (optional, for PDF generation)

### Setup (uv)

1. Create a virtual environment and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate
   uv sync
   ```

### Setup (Poetry)

1. Install Poetry: https://python-poetry.org/docs/#installation
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Run the server:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

### Setup (pip)

1. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Environment Variables

Create a `.env` file (copy from `.env.example`) and add your API keys.

### Running the API

```bash
uvicorn app.main:app --reload
```

Visit [http://localhost:8000/docs](http://localhost:8000/docs) for the Swagger UI documentation.

## Project Structure

```
backend/
├── app/
│   ├── main.py                # FastAPI entrypoint
│   ├── api/                   # API endpoints
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── modules.py
│   │       ├── quizzes.py
│   │       └── assignments.py
│   ├── models/                # SQLModel definitions
│   ├── services/              # Business logic and AI components
│   │   ├── content_service.py
│   ├── utils/                 # Utility functions
│   │   └── latex_utils.py
│   ├── core/                  # Core configuration
│   ├── db/                    # Database utilities
│   ├── scraping/              # Web scraping (from partner)
│   └── embedding/             # Vector embeddings (from partner)
```
