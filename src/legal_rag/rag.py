"""Semantic search over the FAISS index and the call to Claude."""

from typing import Any

import numpy as np

from legal_rag.config import get_model_name

SYSTEM_PROMPTS = {
    "fr": """Vous êtes un assistant juridique expert en droit marocain, intégré au système officiel du Ministère de la Justice.
Basez-vous EXCLUSIVEMENT sur les articles fournis. Répondez en français.
## 📋 Analyse de la situation
## ⚖️ Lois applicables
## 🛡️ Droits et obligations
## 📝 Procédure recommandée
## 📚 Références légales""",
    "ar": """أنت مساعد قانوني خبير في القانون المغربي، مدمج في المنظومة الرسمية لوزارة العدل.
استند حصراً إلى المواد المقدمة. أجب بالعربية.
## 📋 تحليل الوضع
## ⚖️ القوانين المنطبقة
## 🛡️ الحقوق والالتزامات
## 📝 الإجراء الموصى به
## 📚 المراجع القانونية""",
}


def semantic_search(
    query: str,
    index: Any,
    metadata: list[dict],
    model: Any,
    top_k: int = 5,
    category_filter: str | None = None,
) -> list[dict]:
    """Return up to top_k unique articles closest to the query, optionally in one category."""
    q_emb = model.encode([query], normalize_embeddings=True).astype(np.float32)
    dists, idxs = index.search(q_emb, top_k * 3)
    results, seen = [], set()
    for dist, idx in zip(dists[0], idxs[0], strict=True):
        if idx < 0 or idx >= len(metadata):
            continue
        meta = metadata[idx].copy()
        if category_filter and meta.get("category") != category_filter:
            continue
        key = str(meta.get("article_text", ""))[:80]
        if key in seen:
            continue
        seen.add(key)
        meta["score"] = float(dist)
        results.append(meta)
        if len(results) >= top_k:
            break
    return results


def build_user_message(question: str, context: str, lang: str) -> str:
    """Build the user message sent to Claude (labels fixed per language in T3)."""
    return f"السؤال:\n{question}\n\nالمواد القانونية:\n{context}"


def call_claude(question: str, context: str, lang: str, client: Any) -> str:
    """Ask Claude for a legal analysis based only on the given articles."""
    msg = client.messages.create(
        model=get_model_name(),
        max_tokens=1500,
        system=SYSTEM_PROMPTS["ar" if lang == "ar" else "fr"],
        messages=[
            {"role": "user", "content": build_user_message(question, context, lang)}
        ],
    )
    return msg.content[0].text
