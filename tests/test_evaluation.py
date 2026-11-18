"""Tests for src/legal_rag/evaluation.py (SPEC-evaluation AC1-AC4). No model download needed."""

import pickle
from pathlib import Path

import numpy as np
import pytest

from legal_rag import evaluation

ROOT = Path(__file__).resolve().parents[1]
METRICS = ["recall@1", "recall@3", "recall@5", "mrr", "ndcg@5", "category_recall@1"]


# AC1 — Recall@k and reciprocal rank at article level
def test_recall_and_reciprocal_rank():
    ids, expected = [7, 3, 9], {3}
    assert evaluation.recall_at_k(ids, expected, k=1) == 0.0
    assert evaluation.recall_at_k(ids, expected, k=3) == 1.0
    assert evaluation.reciprocal_rank(ids, expected) == 0.5


def test_reciprocal_rank_zero_when_not_found():
    assert evaluation.reciprocal_rank([1, 2, 3], {9}) == 0.0


# AC2 — nDCG@k: 1.0 when the expected article is first, 0.0 when absent
def test_ndcg_perfect_and_zero():
    assert evaluation.ndcg_at_k([3, 7, 9], {3}, k=5) == pytest.approx(1.0)
    assert evaluation.ndcg_at_k([7, 8, 9], {3}, k=5) == 0.0


def test_ndcg_lower_when_expected_is_second():
    assert 0.0 < evaluation.ndcg_at_k([7, 3], {3}, k=5) < 1.0


# AC3 — the evaluation dataset is valid
def test_eval_dataset_is_valid():
    queries = evaluation.load_queries(ROOT / "eval" / "queries.csv")
    with open(ROOT / "vector_db" / "metadata.pkl", "rb") as f:
        known_ids = {a["id"] for a in pickle.load(f)}

    assert len(queries) >= 25
    for q in queries:
        assert q["expected_ids"], f"no expected id: {q['question']}"
        assert q["expected_ids"] <= known_ids, f"unknown id in: {q['question']}"
    assert sum(q["lang"] == "ar" for q in queries) >= 5
    assert {q["category"] for q in queries} == {
        "civil",
        "penal",
        "social",
        "familial",
        "education",
    }


# AC4 — evaluate() on the real FAISS index with a fake embedder
class FakeEmbedder:
    """Always returns the vector of the first stored article."""

    def __init__(self, vector):
        self.vector = vector

    def encode(self, texts, normalize_embeddings=True):
        return np.array([self.vector], dtype=np.float32)


def test_evaluate_returns_all_metrics_overall_and_per_language():
    import faiss

    index = faiss.read_index(str(ROOT / "vector_db" / "faiss_index.bin"))
    with open(ROOT / "vector_db" / "metadata.pkl", "rb") as f:
        metadata = pickle.load(f)
    embeddings = np.load(ROOT / "vector_db" / "embeddings.npy")
    queries = [
        {"question": "q1", "lang": "fr", "category": "civil", "expected_ids": {1}},
        {"question": "q2", "lang": "ar", "category": "penal", "expected_ids": {40}},
    ]

    report = evaluation.evaluate(queries, index, metadata, FakeEmbedder(embeddings[0]))

    for group in ["overall", "fr", "ar"]:
        for metric in METRICS:
            assert 0.0 <= report[group][metric] <= 1.0
    assert report["overall"]["n"] == 2
