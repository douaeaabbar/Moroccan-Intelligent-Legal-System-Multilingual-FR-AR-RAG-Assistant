"""Run the article-level retrieval evaluation with the real embedding model.

Usage: python scripts/evaluate.py [--queries eval/queries.csv] [--out eval/results/baseline.json]
Needs the embedding model (downloaded once, then cached). Not run in CI.
"""

import argparse
import json
import pickle
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from legal_rag.config import EMBEDDING_MODEL, ROOT, VEC_DIR
from legal_rag.evaluation import evaluate, format_report, load_queries


def main() -> None:
    """Load index + model, evaluate, print the table and misses, save the JSON report."""
    sys.stdout.reconfigure(encoding="utf-8")  # Arabic text on the Windows console
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--queries", type=Path, default=ROOT / "eval" / "queries.csv")
    parser.add_argument(
        "--out", type=Path, default=ROOT / "eval" / "results" / "baseline.json"
    )
    args = parser.parse_args()

    import faiss
    from sentence_transformers import SentenceTransformer

    index = faiss.read_index(str(VEC_DIR / "faiss_index.bin"))
    with open(VEC_DIR / "metadata.pkl", "rb") as f:
        metadata = pickle.load(f)
    model = SentenceTransformer(EMBEDDING_MODEL)

    report = evaluate(load_queries(args.queries), index, metadata, model)
    print(format_report(report))

    misses = [d for d in report["details"] if d["recall@5"] == 0.0]
    print(f"\nQuestions with no expected article in the top 5: {len(misses)}")
    for d in misses:
        print(f"  [{d['lang']}] {d['question']}")
        print(f"       expected={d['expected_ids']} got={d['returned_ids']}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"\nSaved: {args.out}")


if __name__ == "__main__":
    main()
