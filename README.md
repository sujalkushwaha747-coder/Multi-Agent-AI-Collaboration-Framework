# ShodhAI: A Comparative Framework for Evaluating Single-Agent and Multi-Agent Large Language Model Systems

ShodhAI is a full-stack academic research application for comparing two LLM system architectures:

1. A Single-Agent LLM pipeline.
2. A LangGraph-based Multi-Agent pipeline with Research, Planner, Writer, Reviewer, and Verifier agents.

Both systems receive the same prompt. The backend records execution time, retrieval context, generated responses, agent metadata, and transparent evaluation metrics before the frontend displays the comparison side by side.

## Problem Statement

Complex academic and technical tasks often require research, planning, writing, review, and verification. A single LLM call may be faster, while a role-based multi-agent workflow may produce more complete or reliable outputs. ShodhAI evaluates this tradeoff with measured runs rather than assuming one architecture is always better.

## Objectives

- Develop a working Single-Agent LLM architecture.
- Develop a controlled Multi-Agent LLM workflow.
- Use RAG with FAISS for document-grounded context retrieval.
- Store experiment results in MySQL using SQLAlchemy and Alembic.
- Compare outputs using accuracy, quality, hallucination rate, completeness, execution time, and a normalized overall score.
- Provide dashboard, result, history, knowledge-base, and methodology pages.
- Avoid fabricated research results or fake benchmark scores.

## Proposed Solution

The application lets a user enter an academic, technical, or general prompt. The prompt is sent to both architectures. Optional indexed documents are retrieved through FAISS and supplied as context. The evaluation engine compares both outputs and marks estimated metrics when no reference answer or evidence is available.

## Workflow

```text
User Prompt
  -> Single-Agent pipeline
  -> Multi-Agent LangGraph workflow
       -> Research Agent
       -> Planner Agent
       -> Writer Agent
       -> Reviewer Agent
       -> Verifier Agent
  -> Evaluation Engine
  -> MySQL storage
  -> Comparison Dashboard
```

## Architecture

```text
Browser
  -> React + Vite frontend
  -> FastAPI REST API
  -> Service layer
       -> Single-Agent service
       -> LangGraph Multi-Agent service
       -> Evaluation engine
       -> Retrieval service
  -> MySQL for structured data
  -> FAISS for vector search
  -> Ollama for Llama 3 inference
```

## Features

- Dashboard with aggregate experiment counts, average scores, execution time, and comparison charts.
- New Experiment page with prompt entry, task category selection, optional reference answer, and optional knowledge documents.
- Result page with Single-Agent and Multi-Agent responses, metric scorecard, comparison chart, agent workflow, timing, and retrieval details.
- Knowledge Base page for PDF, TXT, and DOCX upload, indexing, deletion, and retrieval testing.
- Experiment History page with search, sort, detail view, and deletion.
- Benchmark prompt seeding for academic and technical prompts.
- Transparent evaluation methodology with estimated labels.
- Error handling for invalid prompts, uploads, retrieval failures, LLM failures, and partial experiment runs.

## Technology Stack

- Frontend: React, Vite, TypeScript, Recharts, Lucide icons.
- Backend: Python, FastAPI, Pydantic, SQLAlchemy, Alembic.
- LLM: Llama 3 through Ollama.
- Orchestration: LangChain prompt templates and LangGraph StateGraph.
- Retrieval: FAISS with sentence-transformer embeddings when available; deterministic hashing fallback for local/offline development.
- Database: MySQL.
- Testing: Pytest, Vitest, React Testing Library.
- DevOps: Docker and docker-compose.

## Requirements

- Python 3.11 or 3.12 recommended.
- Node.js 20+ recommended.
- MySQL 8+.
- Ollama running locally.
- Llama model pulled in Ollama, for example `llama3:8b`.

## Installation

Copy `.env.example` to `.env` and adjust values for your machine.

```bash
cp .env.example .env
```

### MySQL Setup

Using Docker:

```bash
docker compose up -d mysql
```

Manual MySQL setup:

```sql
CREATE DATABASE shodhai;
CREATE USER 'shodhai'@'localhost' IDENTIFIED BY 'shodhai';
GRANT ALL PRIVILEGES ON shodhai.* TO 'shodhai'@'localhost';
FLUSH PRIVILEGES;
```

Then set:

```env
DATABASE_URL=mysql+pymysql://shodhai:shodhai@localhost:3306/shodhai
```

### Ollama Installation

Install Ollama from the official Ollama website, start the Ollama service, then pull the configured model:

```bash
ollama pull llama3:8b
ollama serve
```

Set:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3:8b
```

## Backend Setup

macOS/Linux:

```bash
./scripts/setup_backend.sh
```

Windows PowerShell:

```powershell
.\scripts\setup_backend.ps1
```

Run migrations and seed benchmark prompts:

```bash
./scripts/init_database.sh
```

Start the backend:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

FastAPI docs are available at `http://localhost:8000/api/docs`.

## Frontend Setup

macOS/Linux:

```bash
./scripts/setup_frontend.sh
```

Windows PowerShell:

```powershell
.\scripts\setup_frontend.ps1
```

Start the frontend:

```bash
cd frontend
npm run dev
```

The app runs at `http://localhost:5173`.

## FAISS Setup

FAISS is installed through `backend/requirements.txt` as `faiss-cpu`. Indexed chunks and vector metadata are stored under `data/faiss`. Uploaded documents are stored under `data/uploads`.

For lower-resource machines, set:

```env
EMBEDDING_PROVIDER=hashing
```

This keeps retrieval functional without downloading a sentence-transformer model, but semantic quality will be lower.

## Running the Application

One-command local development after dependencies are installed:

```bash
./scripts/run_dev.sh
```

Then open:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000/api/docs`

## Running Tests

Backend:

```bash
cd backend
source .venv/bin/activate
pytest
```

Frontend:

```bash
cd frontend
npm test
```

## Benchmarking

Seed prompts are stored in `data/samples/benchmark_prompts.json` and inserted into the database by `scripts/init_database.sh`. The benchmark endpoint runs both architectures for each prompt and stores actual results. It does not seed fake performance values.

## Evaluation Methodology

Higher is better:

- Accuracy
- Response Quality
- Completeness

Lower is better:

- Hallucination Rate
- Execution Time

Improvement for higher-is-better metrics:

```text
((MultiAgent - SingleAgent) / SingleAgent) * 100
```

Improvement for lower-is-better metrics:

```text
((SingleAgent - MultiAgent) / SingleAgent) * 100
```

The overall score normalizes metric direction before weighting:

- Accuracy: 25%
- Quality: 25%
- Completeness: 20%
- Hallucination benefit: 20%
- Execution-time benefit: 10%

This weighting is configurable and is not claimed to be scientifically universal.

## Project Limitations

- Local LLM speed and quality depend on hardware.
- Llama 3 output may vary between runs.
- LLM-based or heuristic evaluation is imperfect.
- Accuracy is difficult to measure objectively without a reference answer.
- Hallucination detection is estimated when no external ground truth is available.
- Multi-Agent workflows usually require more calls and more execution time.
- FAISS retrieval quality depends on document quality, chunking, and embeddings.

## Future Scope

- Add authenticated project roles for student, evaluator, and admin.
- Add PDF export for experiment reports.
- Support benchmark datasets with reference answers.
- Add evaluator-model selection.
- Add richer citation-aware retrieval.
- Add background jobs for long benchmark runs.

## Research References

- Evaluation and Benchmarking of LLM Agents: A Survey: https://doi.org/10.1145/3711896.3736570
- SAMVAD: A Multi-Agent System for Simulating Judicial Deliberation Dynamics in India: https://arxiv.org/abs/2509.03793
- MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework: https://arxiv.org/abs/2308.00352
- AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation: https://arxiv.org/abs/2308.08155

