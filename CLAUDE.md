# Moroccan Intelligent Legal System — Assistant juridique FR/AR

## Objectif
Faire évoluer ce RAG juridique marocain (FR/AR) vers un système avancé :
corpus élargi, recherche hybride + reranker, serveur MCP, agent LangGraph,
évaluation chiffrée, API + Docker + CI.

## Commandes
- Environnement : `python -m venv .venv` puis activer, `pip install -r requirements.txt -r requirements-dev.txt`
- Tests : `pytest -q`
- Lint / format : `ruff check . --fix` et `ruff format .`
- App : `streamlit run app/streamlit_app.py`

## Règles de travail (obligatoires)
- Une seule étape à la fois. Ne jamais commencer l'étape suivante sans mon accord.
- Avant de coder : proposer 2 options avec avantages / inconvénients, puis attendre mon choix.
- Après avoir codé : expliquer ce qui a changé, fichier par fichier, et pourquoi.
- Ne jamais faire `git commit` ni `git push` en dehors de la commande `/livrer`,
  et seulement après ma confirmation explicite.
- Réutiliser le code existant avant d'en écrire du nouveau.
- Toute nouvelle fonction a un test pytest dans `tests/`.
- Clés API uniquement dans `.env`, jamais dans le code. Ne jamais lire ni afficher `.env`.
- Code dans `src/` ; les notebooks servent seulement à l'exploration.

## Conventions
- Python 3.11+, type hints, docstrings courtes.
- Commits au format Conventional Commits : `feat(scope): ...`, `fix(...)`, `docs(...)`, `test(...)`, `chore(...)`.
- Une branche par étape : `feat/...`, `chore/...`, `docs/...`.
- Chaque décision importante est notée dans `docs/decisions/NNN-titre.md`.
