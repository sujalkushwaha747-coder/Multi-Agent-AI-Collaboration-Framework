# API Summary

Base path: `/api`

## Health

- `GET /api/health`

Returns application, database, and Ollama status.

## Experiments

- `POST /api/experiments`
- `POST /api/experiments/run-comparison`
- `POST /api/experiments/{id}/run-single`
- `POST /api/experiments/{id}/run-multi`
- `POST /api/experiments/{id}/run-both`
- `GET /api/experiments`
- `GET /api/experiments/{id}`
- `DELETE /api/experiments/{id}`

## Documents

- `POST /api/documents/upload`
- `GET /api/documents`
- `POST /api/documents/{id}/index`
- `DELETE /api/documents/{id}`
- `POST /api/documents/search`

## Dashboard

- `GET /api/dashboard/summary`
- `GET /api/dashboard/metrics`

## Benchmarks

- `GET /api/benchmarks/prompts`
- `POST /api/experiments/benchmark-run`

