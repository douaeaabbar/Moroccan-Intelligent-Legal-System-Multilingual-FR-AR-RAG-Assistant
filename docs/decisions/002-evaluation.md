# 002 — Évaluer la recherche au niveau de l'article

- **Date** : 2026-11-18
- **Étape / branche** : `feat/evaluation` (basée sur `chore/stabilise`)

## Contexte
L'évaluation du notebook 02 comptait un résultat comme correct s'il était dans la bonne
**catégorie** (5 catégories seulement), avec 18 requêtes en mots-clés. Résultat : 1,0 partout
(Recall@1 = Recall@5 = MRR = 1,0). Un score déjà au maximum ne peut pas montrer qu'un reranker
ou une recherche hybride améliore quoi que ce soit.

## Options étudiées
1. **Reprendre l'évaluation du notebook telle quelle** dans `src/` : + rapide, réutilise le code ;
   − reste à 1,0, donc inutile pour comparer des versions.
2. **Évaluation au niveau de l'article** (choisie) : un résultat est correct seulement si c'est
   l'article attendu (par `id`). + mesure ce que vit l'utilisateur, laisse de la marge ;
   − il faut écrire et relire les étiquettes (article attendu par question).

## Décision
Option 2. `src/legal_rag/evaluation.py` (Recall@k, MRR, nDCG@5, formules du notebook adaptées
aux `id`), 34 questions réelles dans `eval/queries.csv` (25 FR, 9 AR, 5 domaines, étiquettes
relues par Douae), passage par `semantic_search` (même chemin que l'app), script
`scripts/evaluate.py`. Le score par catégorie est gardé comme métrique secondaire.
Correction au passage : le nDCG « idéal » est calculé sur les articles **attendus**
(le notebook le calculait sur les articles trouvés, ce qui masquait les articles manqués).

## Raison
On ne peut pas décider d'un reranker ou d'une recherche hybride sans un chiffre qui peut monter.
Les questions en langage courant (« mon patron peut-il me renvoyer… ») reflètent l'usage réel.

## Résultat mesuré (baseline, `eval/results/baseline.json`)
| Métrique | Global (34) | AR (9) | FR (25) |
|---|---|---|---|
| Recall@1 | **0,765** | 0,667 | 0,800 |
| Recall@5 | 0,941 | 0,889 | 0,960 |
| MRR | **0,829** | 0,778 | 0,848 |
| nDCG@5 | 0,857 | 0,798 | 0,878 |
| Catégorie@1 (ancienne métrique) | 0,941 | 1,000 | 0,920 |

Échecs complets (article attendu absent du top 5) :
- « Mon mari me frappe… » → articles mariage/divorce (41, 40, 42) au lieu de violence (16, 18).
- « ما هي عقوبة السرقة… » (vol, en arabe) → fraude/examens au lieu de l'article 38.

## Limites
- 34 questions : une question = environ 3 points de Recall ; petites variations à interpréter avec prudence.
- Étiquettes relues par une seule personne ; textes des articles non vérifiés contre le Bulletin officiel.
- Articles 43-44 (« مجلة الشؤون الجنائية ») : source à vérifier.

## Suites possibles (non faites)
- Prochaine étape : recherche hybride (BM25 + FAISS) ou reranker, **à comparer à ce baseline**.
- Ajouter des questions « piège » sans réponse dans la base.
- Agrandir le corpus arabe (2 articles sur 45).
