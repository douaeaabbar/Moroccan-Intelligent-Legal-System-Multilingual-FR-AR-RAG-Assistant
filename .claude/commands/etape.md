---
description: Démarrer une nouvelle étape (branche + plan avec 2 options)
argument-hint: <nom-de-branche> <objectif de l'étape>
---

Nouvelle étape : $ARGUMENTS

1. Vérifie avec `git status` que l'arbre de travail est propre. Sinon, arrête-toi et dis-le-moi.
2. Fais `git checkout main && git pull`, puis crée la branche indiquée par le premier mot des arguments
   (`git checkout -b <nom>`).
3. Lis les fichiers concernés par cet objectif. Ne modifie rien.
4. Propose-moi un plan avec **2 options** : pour chacune, les fichiers créés ou modifiés,
   les avantages, les inconvénients et la façon de mesurer le résultat.
5. Arrête-toi et attends que je choisisse une option. N'écris aucun code avant mon choix.
