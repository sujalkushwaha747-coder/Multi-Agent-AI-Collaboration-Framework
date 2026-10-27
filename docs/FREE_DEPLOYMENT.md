# Free demo deployment with a persistent database and Ollama fallback

## What runs where

| Component | Runs on | What must remain available |
|---|---|---|
| Frontend | Vercel | Deployment and usage within free limits |
| FastAPI backend | Render Free web service | Wakes on requests; can restart/sleep |
| Experiment database | Neon Free PostgreSQL | Account/project within free limits |
| Primary inference | Groq API | Valid key and quota |
| Fallback inference | Ollama on your Mac | Mac awake, Ollama running, gateway and tunnel running |

This is a college/demo configuration, not a free always-on cloud GPU. Neon preserves experiment rows independently of Render restarts. Uploaded Knowledge Base files and the NumPy search index still use Render's temporary filesystem: re-upload and re-index documents after a restart. Document metadata alone in PostgreSQL does not preserve the source file or vectors. Durable Knowledge Base storage needs a separate object/vector storage integration.

## 1. Update the local project

From the repository root in VS Code:

```bash
git pull origin main
```

Close/restart local app processes after updating. The full local dependencies remain in `backend/requirements.txt`; the cloud's lightweight dependencies are in `backend/requirements-free.txt`. The latter uses hashing embeddings and NumPy search, avoiding PyTorch, sentence-transformers and FAISS downloads. Retrieval quality differs from semantic embeddings, so keep this setting recorded in experiments.

## 2. Create the external database

1. Sign up at https://console.neon.tech/ and select the Free plan.
2. Create a project named `multi-agent-framework`, with a region close to your intended Render region.
3. Open **Connect**, select the default branch/database/role, and copy the PostgreSQL connection URI. For initial deployment, use the direct connection (pooling off).
4. Change only the URI prefix from `postgresql://` to `postgresql+psycopg://`. Keep the actual username, password, hostname, database and TLS query parameters exactly as supplied. Do not decode URL-encoded password characters.
5. Save this as `DATABASE_URL` in Render, not in Git or Vercel. Do not include a `psql` command, quotes or the `DATABASE_URL=` label inside the value field.

Example shape, with placeholders only:

```text
postgresql+psycopg://USER:PASSWORD@YOUR-NEON-HOST/neondb?sslmode=require
```

The production startup script creates the application's tables through Alembic and seeds example prompts. You do not manually create the tables in Neon. Existing local SQLite research history is not automatically migrated into this new database.

## 3. Start local Ollama

1. Install/open Ollama from https://ollama.com/download/mac if needed.
2. Run `ollama pull llama3:8b` in a terminal. Downloading is needed once per model installation.
3. Run `ollama run llama3:8b "Reply with one short greeting."` and verify a real response.
4. Check `curl http://127.0.0.1:11434/api/tags` and confirm `llama3:8b` appears.

If the service is not running, open the Ollama Mac app or run `ollama serve` in a separate terminal. If it reports that port 11434 is already in use, the existing service is already listening; do not start another copy.

## 4. Start the protected gateway

The raw Ollama API has no local authentication. Expose the token-protected gateway on port 11435, never raw port 11434.

1. Generate a private token with `openssl rand -hex 32` in your terminal. Copy it privately.
2. In the project root create `.env.ollama` containing `OLLAMA_API_KEY=YOUR_GENERATED_TOKEN`. This file is Git-ignored. Do not share or commit it.
3. In a new VS Code terminal, from the project root, run:

```bash
set -a
source .env.ollama
set +a
backend/.venv/bin/python -m uvicorn scripts.ollama_gateway:app --host 127.0.0.1 --port 11435
```

Leave this terminal running. If the local virtual environment is missing, run `bash scripts/setup_backend.sh` first.

The gateway forwards only `/api/tags` and non-streaming `/api/generate` to Ollama at `127.0.0.1:11434`. It rejects requests without the correct bearer token and does not expose model-pull/delete endpoints.

## 5. Start a temporary HTTPS tunnel

Install Cloudflare's tunnel client on the Mac (Homebrew required for this command):

```bash
brew install cloudflared
```

If Homebrew is unavailable, use the official Cloudflare download instructions linked below. In another terminal run:

```bash
cloudflared tunnel --url http://127.0.0.1:11435
```

Copy the HTTPS URL printed by cloudflared, for example `https://YOUR-RANDOM-NAME.trycloudflare.com`. Leave the tunnel running. The URL changes when you create a new Quick Tunnel; update Render's `OLLAMA_BASE_URL` whenever it changes. A Quick Tunnel is temporary demo infrastructure with no uptime guarantee. Do not enable interactive email authentication: the backend is a non-interactive client; the gateway token already protects its requests.

## 6. Create the Render Free backend

For a manual setup, select **New → Web Service**, connect this GitHub repository and configure:

| Setting | Value |
|---|---|
| Branch | `main` |
| Language | Python |
| Root Directory | Leave blank |
| Build command | `pip install -r backend/requirements-free.txt` |
| Start command | `bash scripts/start_backend_production.sh` |
| Instance | Free |
| Health check path | `/api/health/ready` |
| Persistent disk | None |

Alternatively import a Blueprint and explicitly select **`render.free.yaml`**. The original `render.yaml` is the separate paid configuration.

Add the following environment variables, replacing all placeholders:

```dotenv
APP_ENV=production
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@YOUR-NEON-HOST/neondb?sslmode=require
LLM_PROVIDER=auto
GROQ_API_KEY=YOUR_GROQ_KEY
GROQ_MODEL=openai/gpt-oss-20b
OLLAMA_FALLBACK_ENABLED=true
OLLAMA_BASE_URL=https://YOUR-RANDOM-NAME.trycloudflare.com
OLLAMA_API_KEY=THE_SAME_TOKEN_AS_ON_YOUR_MAC
OLLAMA_MODEL=llama3:8b
OLLAMA_TIMEOUT_SECONDS=180
OLLAMA_RETRIES=0
EMBEDDING_PROVIDER=hashing
UPLOAD_DIR=/tmp/shodhai/uploads
FAISS_INDEX_PATH=/tmp/shodhai/faiss
CORS_ORIGINS=https://YOUR-FRONTEND.vercel.app
```

Use the intended frontend origin initially, then correct it once Vercel assigns the actual production URL. Remove an inherited `CORS_ORIGIN_REGEX`. A CORS origin has no trailing slash or `/api`; the Ollama base URL also has no `/api` suffix.

Deploy and copy the Render backend URL. Open `/api/health/ready` and `/api/docs`. Review the deployment logs for migration completion. On Neon, inspect the Tables page: `experiments`, result/evaluation tables, `agent_runs`, `documents` and benchmark tables should now exist.

## 7. Deploy the frontend

In Vercel, import the same repository with Root Directory **`frontend`**, framework **Vite** and Node.js **22.x**. The committed config supplies `npm ci`, `npm run build` and `dist`.

Add `VITE_API_BASE_URL=https://YOUR-BACKEND.onrender.com/api` and deploy. Put the actual Vercel production origin into Render's `CORS_ORIGINS`, save and redeploy the backend. Backend keys and database passwords never belong in the frontend.

## 8. Test all connections separately

1. **Database:** `/api/health/ready` returns `database.available: true`. Create an experiment and confirm its row appears in Neon. A new Render deploy should retain the saved experiment.
2. **Ollama connection:** `/api/health` should report Ollama `available: true` and `model_available: true` while the Mac, gateway and tunnel are running.
3. **Ollama generation:** temporarily set Render `LLM_PROVIDER=ollama`, redeploy and run a short experiment. Confirm the result's model is `ollama:llama3:8b`.
4. **Groq generation:** restore `LLM_PROVIDER=auto` with a working Groq key and run a short task. It should normally use Groq.
5. **Real fallback:** while leaving `LLM_PROVIDER=auto`, temporarily replace the Render Groq key with an intentionally invalid test value, redeploy and run a short task. Groq will reject the request and the app should use Ollama. Then immediately restore the real Groq key and redeploy. Do not delete the key value completely: production validation requires a configured key in auto mode.

Automatic fallback happens per generation request, including calls inside the multi-agent graph. A single experiment can contain calls from different providers if failures occur partway through; inspect each stage's metadata for research comparisons. A provider health check is not proof that a generation request will succeed.

## Troubleshooting

| Symptom | Check |
|---|---|
| Database startup failure | Use `postgresql+psycopg://`, keep TLS parameters, copy the current Neon role password and hostname |
| Ready succeeds but generation fails | Ready checks the database only; inspect `/api/health` and experiment errors |
| Gateway returns 401 | Render and `.env.ollama` tokens must match exactly; no quotes in the Render value |
| Ollama connection unavailable | Mac awake, local tags check, gateway terminal, current tunnel URL |
| Tunnel gives 502 | Gateway on port 11435 is stopped or local Ollama is stopped |
| Ollama model unavailable | Pull exactly `llama3:8b` on the Mac |
| Free backend slow to open | Render sleeps on inactivity and wakes on a later request |
| Uploaded document disappears after restart | Database rows persist in Neon; local file/index storage is still temporary |

## Official references

- https://render.com/docs/free
- https://neon.com/pricing
- https://neon.com/docs/guides/sqlalchemy
- https://docs.ollama.com/api/authentication
- https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/
- https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/downloads/
