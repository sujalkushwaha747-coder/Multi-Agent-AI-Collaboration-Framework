# Project Overview

## Project Title

ShodhAI: A Comparative Framework for Evaluating Single-Agent and Multi-Agent Large Language Model Systems

## Project Type

Web-Based AI Application

## Research Type

Experimental and Comparative

## Core Technologies

- React.js
- FastAPI
- Python
- LangChain
- LangGraph
- Llama 3
- Ollama
- FAISS
- MySQL

## Objectives

1. Develop Single-Agent and Multi-Agent LLM architectures.
2. Implement role-based Multi-Agent collaboration.
3. Compare both architectures using standard evaluation metrics.
4. Analyze their performance on academic and complex technical tasks.

## System Summary

ShodhAI runs the same prompt through a Single-Agent LLM pipeline and a Multi-Agent LangGraph workflow. Both outputs are evaluated and displayed side by side. The project does not claim that Multi-Agent systems are always superior; it reports measured and labeled results for each experiment.

## Multi-Agent Roles

- Research Agent: retrieves context, extracts findings, and identifies information gaps.
- Planner Agent: creates a structured response plan.
- Writer Agent: drafts the response.
- Reviewer Agent: checks completeness, relevance, clarity, and unsupported claims.
- Verifier Agent: produces the final verified response and concise verification findings.

## Data Storage

MySQL stores users, documents, experiments, prompts, Single-Agent results, Multi-Agent results, evaluation results, agent runs, benchmark prompts, and system settings.

FAISS stores vector-search indexes for knowledge documents. It is not used as the relational database.

