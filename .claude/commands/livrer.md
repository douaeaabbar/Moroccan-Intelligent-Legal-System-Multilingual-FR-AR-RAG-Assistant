---
description: Vérifier, documenter, puis commit + push + Pull Request de l'étape en cours
argument-hint: [message de commit optionnel]
---

Livre l'étape en cours. Suis ces étapes dans l'ordre et arrête-toi au premier échec.

1. Lance `ruff check . --fix` puis `ruff format .`.
2. Lance `pytest -q`. Si un test échoue, montre-moi l'erreur, propose une correction et arrête-toi.
3. Montre-moi `git status` et un résumé du `git diff` : fichier par fichier, ce qui a changé et pourquoi.
4. Si une décision technique a été prise dans cette étape, crée `docs/decisions/NNN-titre.md`
   (contexte, options, choix, raison, résultat mesuré), avec NNN = numéro suivant.
5. Propose un message de commit au format Conventional Commits
   (ou utilise celui-ci s'il est fourni : $ARGUMENTS).
6. **Demande-moi une confirmation explicite (« oui ») avant de continuer.**
7. Après mon « oui » : `git add -A`, `git commit -m "<message>"`, `git push -u origin HEAD`.
8. Crée la Pull Request : `gh pr create --fill --base main`, puis donne-moi le lien.
9. Ne merge pas : c'est moi qui relis et merge la PR sur GitHub.
