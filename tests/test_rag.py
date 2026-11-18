"""Tests for the RAG logic in src/legal_rag (SPEC AC1-AC5). No API key or network needed."""

import pickle
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from legal_rag import config, rag

ROOT = Path(__file__).resolve().parents[1]


# AC1 — paths are relative to the repo, not a hardcoded user folder
def test_vec_dir_points_to_repo_vector_db():
    assert config.VEC_DIR == ROOT / "vector_db"
    assert (config.VEC_DIR / "faiss_index.bin").exists()


# AC2 — model name comes from CLAUDE_MODEL, with a default
def test_model_name_read_from_env(monkeypatch):
    monkeypatch.setenv("CLAUDE_MODEL", "my-model")
    assert config.get_model_name() == "my-model"


def test_model_name_default_when_unset(monkeypatch):
    monkeypatch.delenv("CLAUDE_MODEL", raising=False)
    assert config.get_model_name() == "claude-sonnet-5-5"


# AC3 — labels sent to Claude match the question language
def test_user_message_french_labels():
    msg = rag.build_user_message("Ma question", "Article 1", lang="fr")
    assert "Question" in msg and "Articles" in msg
    assert "السؤال" not in msg


def test_user_message_arabic_labels():
    msg = rag.build_user_message("سؤالي", "المادة 1", lang="ar")
    assert "السؤال" in msg and "المواد القانونية" in msg


# AC4 — semantic search on the real FAISS index, with a fake embedding model
class FakeEmbedder:
    """Returns a stored article vector instead of calling the real model."""

    def __init__(self, vector):
        self.vector = vector

    def encode(self, texts, normalize_embeddings=True):
        return np.array([self.vector], dtype=np.float32)


def test_semantic_search_filters_category_and_limits_results():
    import faiss

    index = faiss.read_index(str(ROOT / "vector_db" / "faiss_index.bin"))
    with open(ROOT / "vector_db" / "metadata.pkl", "rb") as f:
        metadata = pickle.load(f)
    embeddings = np.load(ROOT / "vector_db" / "embeddings.npy")

    results = rag.semantic_search(
        "query",
        index,
        metadata,
        FakeEmbedder(embeddings[0]),
        top_k=3,
        category_filter="civil",
    )

    assert 0 < len(results) <= 3
    assert all(r["category"] == "civil" for r in results)
    texts = [r["article_text"] for r in results]
    assert len(texts) == len(set(texts))


# AC5 — Claude call uses the configured model, via an injected fake client
class FakeClient:
    def __init__(self):
        self.calls = []
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(content=[SimpleNamespace(text="réponse")])


@pytest.mark.parametrize("lang", ["fr", "ar"])
def test_call_claude_uses_configured_model(monkeypatch, lang):
    monkeypatch.setenv("CLAUDE_MODEL", "my-model")
    client = FakeClient()

    answer = rag.call_claude("question", "context", lang=lang, client=client)

    assert answer == "réponse"
    assert client.calls[0]["model"] == "my-model"
