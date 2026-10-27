# Deploy the Multi-Agent AI Collaboration Framework

This repository is configured for a Vercel frontend and a single Render backend using Groq. Render stores the SQLite database, uploaded documents, FAISS index and embedding-model cache on a persistent disk. The Blueprint selects a **paid Standard service and a 3 GB disk**; review the price in Render before creating it.

## 1. Deploy the backend

1. In https://dashboard.render.com/, choose **New → Blueprint** and connect this GitHub repository and the `main` branch.
2. Select the root `render.yaml`. It supplies the Python runtime, CPU-only PyTorch build, production startup, readiness probe and disk settings. Do not set a backend Root Directory: the scripts enter `backend` themselves.
3. Enter the requested environment values:
   - `GROQ_API_KEY`: your private Groq API key.
   - `CORS_ORIGINS`: your intended frontend origin, for example `https://YOUR-PROJECT.vercel.app`. Use an exact HTTPS origin without a trailing slash or `/api`. If Vercel assigns a different URL, update this after step 2.
4. Review the paid plan and disk, then create the Blueprint.
5. Copy the assigned backend URL, for example `https://YOUR-BACKEND.onrender.com`.
6. Open `/api/health/ready` on that URL. It must return HTTP 200 with `database.available: true`. `/api/docs` should show the API documentation. `/api/health` performs optional provider diagnostics and is deliberately not used for hosting probes.

The root `.python-version` selects Python 3.12. `scripts/build_backend_cloud.sh` installs CPU PyTorch before the existing requirements. `scripts/start_backend_production.sh` validates configuration, runs Alembic, seeds benchmark prompts idempotently, and starts one Uvicorn worker on `$PORT` (8000 locally). Migrations run at startup because the persistent disk is not mounted in Render's build/pre-deploy environment.

The Blueprint configures:

```dotenv
APP_ENV=production
LLM_PROVIDER=groq
GROQ_MODEL=openai/gpt-oss-20b
OLLAMA_FALLBACK_ENABLED=false
DATABASE_URL=sqlite:////var/data/shodhai.db
UPLOAD_DIR=/var/data/uploads
FAISS_INDEX_PATH=/var/data/faiss
HF_HOME=/var/data/huggingface
EMBEDDING_PROVIDER=sentence-transformers
```

No Ollama server is required for this cloud setup. A Groq failure is reported directly; the backend does not attempt a nonexistent local Ollama server. Local development retains the existing fallback by default. Only choose `LLM_PROVIDER=ollama` when you have actually deployed a reachable Ollama service.

## 2. Deploy the frontend

1. In https://vercel.com/dashboard, choose **Add New → Project**, import the same repository and select **Root Directory: `frontend`**.
2. Use Node.js **22.x** and the **Vite** preset. `frontend/vercel.json` supplies `npm ci`, `npm run build` and the `dist` output directory.
3. Add `VITE_API_BASE_URL=https://YOUR-BACKEND.onrender.com/api` for Production. Include `/api`. Use the real backend URL, not the example.
4. Deploy. The build rejects missing API configuration and localhost URLs on Vercel, avoiding a published app that silently calls the visitor's laptop.
5. Copy the final Vercel production origin into the Render `CORS_ORIGINS` value and redeploy the backend if it changed. Remove an inherited `CORS_ORIGIN_REGEX` when using the exact-origin configuration.
6. A changed `VITE_API_BASE_URL` requires a new frontend deployment, because Vite embeds it at build time. `GROQ_API_KEY` belongs only on the backend, never in a `VITE_` variable.

The application uses hash navigation, so no SPA rewrite rule is required. Restrict preview access or explicitly add each trusted preview origin to the comma-separated `CORS_ORIGINS` value when testing preview deployments. Do not allow all `vercel.app` sites with a broad regular expression.

## 3. Verify the deployed app

- Open Dashboard, History and New Experiment from the Vercel URL.
- Run a short comparison, open its stored results and confirm the displayed serving provider/model.
- Upload and index a small TXT/PDF/DOCX file, then run a task using that document.
- Restart the Render service and confirm the experiment and indexed document remain available.
- Check `/api/health/ready`; its status reflects database access, not the availability of the paid inference provider.

The cloud database starts empty. This setup does not upload the local research database or its history. Benchmark prompts are seeded; generated results are never fabricated.

## Operations and limits

- This is a single-instance academic demo deployment. SQLite, the file-based FAISS index and in-process background comparisons are not a distributed job system. Do not add multiple workers or replicas with this storage design.
- A deployment or restart can interrupt an active comparison. Finished records persist on the disk; in-progress jobs are not automatically resumed.
- The current app has no login/authorization layer. Use hosting/network access restrictions for a controlled demonstration. CORS is not authentication; a fully public installation needs application access control and request limits to protect inference usage and stored records.
- Maintain separate database/uploads/index backups. A persistent disk is not an independent backup. Do not delete the service/disk to troubleshoot a deploy.
- Groq rate limits still apply. `429` is an inference/quota issue, not proof that the backend deployment failed. Reduce concurrent requests or adjust your provider quota.
- Semantic indexing downloads the sentence-transformer model on first use. Its cache is persisted. If memory runs out during indexing, increase backend memory. Hashing embeddings are an explicitly lower-quality alternative: changing embedding provider/dimension requires rebuilding the knowledge-base index.
- `.env` files, local SQLite files, generated reports and papers are excluded from new commits. The example environment files contain placeholders only. The previously tracked local database is removed from the current Git tree; the local file remains on disk. Existing Git history is not rewritten.

## Local checks

```bash
cd backend
.venv/bin/python -m pytest tests -q
```

```bash
cd frontend
npm ci
npm test
VITE_API_BASE_URL=https://YOUR-BACKEND.onrender.com/api npm run build
```

For a local frontend production-build preview, a local HTTP API URL is also accepted. Docker builds accept a `VITE_API_BASE_URL` build argument; their default targets the existing local backend on port 8000.

## Hosting references

- https://render.com/docs/blueprint-spec
- https://render.com/docs/disks
- https://render.com/docs/python-version
- https://vercel.com/docs/frameworks/frontend/vite
