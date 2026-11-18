"""Article-level retrieval evaluation: Recall@k, MRR, nDCG@k (formulas from notebook 02)."""

import csv
import math
from pathlib import Path
from typing import Any

from legal_rag.rag import semantic_search

K_VALUES = (1, 3, 5)


def recall_at_k(ids: list[int], expected: set[int], k: int) -> float:
    """1.0 if at least one expected article is in the top-k results, else 0.0."""
    return 1.0 if expected & set(ids[:k]) else 0.0


def reciprocal_rank(ids: list[int], expected: set[int]) -> float:
    """1 / position of the first expected article (0.0 if not found)."""
    for position, article_id in enumerate(ids, start=1):
        if article_id in expected:
            return 1.0 / position
    return 0.0


def ndcg_at_k(ids: list[int], expected: set[int], k: int) -> float:
    """Ranking quality in the top-k: 1.0 when all expected articles are at the top."""
    dcg = sum(
        1.0 / math.log2(position + 1)
        for position, article_id in enumerate(ids[:k], start=1)
        if article_id in expected
    )
    ideal = sum(1.0 / math.log2(p + 1) for p in range(1, min(len(expected), k) + 1))
    return dcg / ideal if ideal > 0 else 0.0


def load_queries(path: Path) -> list[dict]:
    """Read the evaluation CSV: question, lang, category, expected_ids (e.g. "35;39")."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        return [
            {
                "question": row["question"],
                "lang": row["lang"],
                "category": row["category"],
                "expected_ids": {
                    int(x) for x in row["expected_ids"].split(";") if x.strip()
                },
            }
            for row in csv.DictReader(f)
        ]


def score_query(query: dict, results: list[dict]) -> dict[str, float]:
    """All metrics for one question, from the articles returned by the search."""
    ids = [r["id"] for r in results]
    expected = query["expected_ids"]
    scores = {f"recall@{k}": recall_at_k(ids, expected, k) for k in K_VALUES}
    scores["mrr"] = reciprocal_rank(ids, expected)
    scores["ndcg@5"] = ndcg_at_k(ids, expected, 5)
    top1_category = results[0]["category"] if results else None
    scores["category_recall@1"] = 1.0 if top1_category == query["category"] else 0.0
    return scores


def _average(rows: list[dict[str, float]]) -> dict[str, float]:
    """Mean of each metric over a group of questions, plus the group size n."""
    if not rows:
        return {"n": 0}
    return {"n": len(rows), **{m: sum(r[m] for r in rows) / len(rows) for m in rows[0]}}


def evaluate(queries: list[dict], index: Any, metadata: list[dict], model: Any) -> dict:
    """Run every question through semantic_search; return mean metrics and per-question details."""
    scored = []
    for q in queries:
        results = semantic_search(q["question"], index, metadata, model, top_k=5)
        scored.append((q, [r["id"] for r in results], score_query(q, results)))

    report: dict[str, Any] = {"overall": _average([s for _, _, s in scored])}
    for lang in sorted({q["lang"] for q in queries}):
        report[lang] = _average([s for q, _, s in scored if q["lang"] == lang])
    report["details"] = [
        {
            "question": q["question"],
            "lang": q["lang"],
            "expected_ids": sorted(q["expected_ids"]),
            "returned_ids": ids,
            **s,
        }
        for q, ids, s in scored
    ]
    return report
