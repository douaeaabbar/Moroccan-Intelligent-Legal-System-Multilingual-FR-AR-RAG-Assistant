# SPEC — Step 1: Stabilise the existing RAG app

Goal: the current app runs from any clone, its logic is tested, and CI is green,
before any roadmap feature (hybrid search, MCP, agent, Docker).

## Requirements (source)
- R1 Paths are relative to the repo, not a hardcoded user folder
  (bug: `app/streamlit_app.py:38`).
- R2 The Claude model comes from `CLAUDE_MODEL` in `.env`, default `claude-sonnet-5-5`;
  `.env` is loaded with python-dotenv (`.env.example`, `app/streamlit_app.py:467`).
- R3 The message sent to Claude uses French labels for French questions and Arabic
  labels for Arabic ones (bug: `app/streamlit_app.py:470`).
- R4 Search + prompt logic lives in `src/` and the app imports it (CLAUDE.md: "Code dans `src/`").
- R5 Every new function has a pytest test; tests need no API key or network (CLAUDE.md).
- R6 `ruff check .` and `ruff format --check .` pass, as CI requires (`.github/workflows/ci.yml`).

## Acceptance criteria
- AC1 Given the repo cloned in any folder, When the config paths are computed,
  Then `VEC_DIR` is `<repo>/vector_db` and `faiss_index.bin` exists there.
- AC2 Given `CLAUDE_MODEL=my-model` in the environment, When the model name is read,
  Then it is `my-model`; Given it is unset, Then it is `claude-sonnet-5-5`.
- AC3 Given `lang="fr"`, When the user message is built, Then it contains French labels
  and no Arabic labels; Given `lang="ar"`, Then it contains the Arabic labels.
- AC4 Given the real FAISS index and a category filter, When `semantic_search` runs with
  `top_k=3`, Then it returns at most 3 results, all of that category, with no duplicates.
- AC5 Given a fake Anthropic client, When `call_claude` runs, Then it sends the configured
  model and returns the text, without network access.
- AC6 Given the repo, When `pytest -q`, `ruff check .`, `ruff format --check .` run,
  Then all pass.

## Out of scope
- New data or corpus, hybrid search, reranker, MCP, LangGraph, API, Docker.
- UI redesign; rewriting the notebooks (only lint fixes if needed).
- Removing `vector_db/embeddings.npy` from git; README fixes (noted as follow-ups).
