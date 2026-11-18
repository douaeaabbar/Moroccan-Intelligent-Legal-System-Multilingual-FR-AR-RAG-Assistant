# SPEC — Step 2: Article-level retrieval evaluation

Goal: a trustworthy baseline score for the search, so later steps (hybrid search,
reranker) can prove they help. The notebook metric (category level) is stuck at 1.0.

## Requirements (source)
- R1 Metric functions in `src/legal_rag/evaluation.py`, reusing the notebook definitions
  (Recall@k, reciprocal rank, nDCG@k), where "relevant" = article `id` in the expected set
  (CLAUDE.md: reuse code; `notebooks/02_Model_Training.ipynb` cell 12).
- R2 Dataset `eval/queries.csv`: >= 25 natural-language questions (FR and AR), each with the
  expected article id(s) among the 45 indexed; every category covered; labels reviewed by Douae.
- R3 Evaluation goes through `legal_rag.rag.semantic_search` (same path as the app).
- R4 `scripts/evaluate.py` prints article-level Recall@1/3/5, MRR, nDCG@5, category-level
  Recall@1, split by language, and saves them to `eval/results/baseline.json`.
- R5 Tests need no model download (CI); `pytest` and `ruff` stay green (CLAUDE.md, CI).

## Acceptance criteria
- AC1 Given returned ids [7, 3, 9] and expected {3}, When metrics run, Then Recall@1 = 0,
  Recall@3 = 1 and reciprocal rank = 0.5.
- AC2 Given the expected article first, Then nDCG@5 = 1.0; Given no expected article, Then 0.0.
- AC3 Given `eval/queries.csv`, When loaded, Then it has >= 25 rows, every expected id exists
  in `vector_db/metadata.pkl`, >= 5 rows are Arabic, and all 5 categories appear.
- AC4 Given the real FAISS index and a fake embedder, When `evaluate()` runs, Then it returns
  every metric above, overall and per language, each between 0 and 1.
- AC5 Given the real model (local cache), When `python scripts/evaluate.py` runs, Then it prints
  the metrics and writes `eval/results/baseline.json` (manual run, not in CI).
- AC6 Given the repo, When `pytest -q`, `ruff check .`, `ruff format --check .` run, Then all pass.

## Out of scope
- Changing the search (no reranker, hybrid search, or new embedding model).
- Adding law articles; rewriting the notebooks.
- Evaluating Claude's answers (needs API credits).
