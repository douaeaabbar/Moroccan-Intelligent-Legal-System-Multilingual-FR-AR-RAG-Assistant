# 001 — Stabiliser l'application RAG avant les évolutions

- **Date** : 2026-11-17
- **Étape / branche** : `chore/stabilise`

## Contexte
L'application ne pouvait pas trouver sa base vectorielle hors du PC d'origine
(chemin `C:\Users\azuz\Downloads\...` codé en dur). Le modèle Claude était codé en dur
(`claude-sonnet-4-6`) et `.env` n'était jamais chargé. Les questions en français étaient
envoyées à Claude avec des libellés arabes. Toute la logique était dans
`app/streamlit_app.py`, donc non testée, et la CI échouait (40 erreurs ruff, 5 fichiers mal formatés).

## Options étudiées
1. **Stabiliser d'abord** : extraire la logique dans `src/legal_rag/`, la tester, corriger les bugs,
   rendre le lint vert. + base saine pour la suite ; − aucune nouvelle fonctionnalité visible.
2. **Commencer une évolution** (recherche hybride, MCP, agent) : + avance la feuille de route ;
   − construite sur une app qui ne démarre pas ailleurs et sans tests pour mesurer.

Sous-choix : `src/` ajouté au chemin d'import (vs `pip install -e .`, plus propre mais demande
packaging + CI) ; `except Exception` gardés dans l'app avec `# noqa: BLE001` + raison
(vs exceptions précises, qui feraient planter la page sur une erreur imprévue).

## Décision
Option 1. Code dans `src/legal_rag/` (`config.py` : chemins relatifs, `CLAUDE_MODEL`,
`load_env()` ; `rag.py` : `semantic_search`, `build_user_message`, `call_claude`).
L'app importe ce paquet. Tests sans clé API ni réseau (faux modèle et faux client Claude).

## Raison
On ne peut pas mesurer une amélioration (reranker, hybride) sans une app qui démarre
et une logique testable. Le client Claude injecté rend `call_claude` testable gratuitement en CI.

## Résultat mesuré
| Mesure | Avant | Après |
|---|---|---|
| Tests pytest | 2 (fichiers présents) | 10 passent (dont recherche FAISS réelle, FR/AR, modèle) |
| Erreurs `ruff check .` | 40 | 0 |
| Fichiers à reformater | 5 | 0 |
| Chemin / modèle codés en dur | oui / oui | non / non (`CLAUDE_MODEL`, défaut `claude-sonnet-5-5`) |

## Suites possibles (non faites)
- Lancer l'app Streamlit en réel avec une clé API (non vérifié dans cette étape).
- Épingler la version de ruff (pre-commit en 0.8.4, local 0.17.5, CI = dernière version).
- Retirer `vector_db/embeddings.npy` de git (déjà dans `.gitignore`) ; corriger le README
  (dossier `models/` absent, ancien nom de modèle).
- Prochaine étape conseillée : évaluation chiffrée du retrieval (Recall@5) avant tout reranker.
