# ⚖️ Système Juridique Intelligent Marocain
### *المستشار القانوني المغربي الذكي*

> Assistant juridique IA basé sur les lois marocaines, combinant RAG + LLM (Claude) + FAISS

---

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture](#architecture)
3. [Structure du projet](#structure-du-projet)
4. [Installation](#installation)
5. [Utilisation pas à pas](#utilisation-pas-à-pas)
6. [Notebooks](#notebooks)
7. [Interface Streamlit](#interface-streamlit)
8. [Données juridiques](#données-juridiques)
9. [Configuration API](#configuration-api)
10. [FAQ](#faq)

---

## Vue d'ensemble

Le **Système Juridique Intelligent Marocain** est une application d'intelligence artificielle qui permet aux utilisateurs de :

- 🗣️ **Décrire leur situation juridique** en arabe ou en français
- 🔍 **Obtenir les textes de loi pertinents** via recherche sémantique
- 📋 **Recevoir une analyse juridique structurée** générée par Claude
- 📄 **Analyser des documents** (PDF, DOCX, images scannées)
- 📚 **Explorer la base juridique marocaine**

**Domaines couverts** : Droit civil · Droit pénal · Droit social · Droit de la famille · Éducation

---

## Architecture

```
Utilisateur
     │
     ▼
[Streamlit Interface]
     │
     ├──► [NLP Preprocessing]
     │         └── Nettoyage · Tokenisation · Détection langue
     │
     ├──► [Embedding Model]  (paraphrase-multilingual-MiniLM-L12-v2)
     │         └── Génère un vecteur 384-dim multilingue (FR/AR)
     │
     ├──► [FAISS Index]
     │         └── Recherche cosinus sur 45+ articles de loi marocains
     │
     └──► [Claude API]  (claude-sonnet-4-6)
               └── Génère une réponse juridique structurée
```

### Pipeline RAG (Retrieval-Augmented Generation)

```
Question → Embedding → FAISS Search → Context → Claude → Réponse
```

1. La question est encodée en vecteur 384-dim
2. FAISS trouve les N articles les plus proches (cosine similarity)
3. Les articles récupérés forment le contexte
4. Claude génère une analyse juridique basée sur ce contexte

---

## Structure du projet

```
legal_ai_morocco/
├── data/
│   ├── raw_laws.csv              # Articles de loi bruts
│   └── *.pdf                     # PDFs des textes officiels
│
├── processed_data/
│   ├── processed_laws.csv        # Données après NLP (généré par NB01)
│   ├── fig_category_lang.png     # Visualisations
│   ├── fig_word_distribution.png
│   ├── fig_top_terms.png
│   ├── fig_penalty_heatmap.png
│   ├── fig_confusion_matrix.png
│   ├── fig_model_comparison.png
│   ├── fig_cross_validation.png
│   └── fig_rag_scores.png
│
├── notebooks/
│   ├── 01_Data_Preprocessing.ipynb   # NLP complet
│   ├── 02_Model_Training.ipynb       # Embeddings + Classification ML
│   └── 03_RAG_Pipeline.ipynb         # Pipeline RAG + tests
│
├── vector_db/
│   ├── embeddings.npy            # Vecteurs FAISS (généré par NB02)
│   ├── faiss_index.bin           # Index FAISS (généré par NB02)
│   └── metadata.pkl              # Mapping index → articles
│
├── models/
│   ├── best_classifier.pkl       # Meilleur classifieur (généré par NB02)
│   └── label_encoder.pkl         # Encodeur de labels
│
├── app/
│   └── streamlit_app.py          # Interface utilisateur principale
│
├── processed_laws.csv            # Données traitées (copie racine)
├── requirements.txt
└── README.md
```

---

## Installation

### Prérequis

- Python 3.11+
- pip
- Tesseract OCR (optionnel, pour les PDFs scannés)

### Étape 1 — Cloner / extraire le projet

```bash
unzip legal_ai_morocco.zip
cd legal_ai_morocco
```

### Étape 2 — Créer un environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate.bat     # Windows
```

### Étape 3 — Installer les dépendances

```bash
pip install -r requirements.txt
```

### Étape 4 — (Optionnel) Installer Tesseract

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-fra tesseract-ocr-ara

# macOS
brew install tesseract
brew install tesseract-lang

# Windows
# Télécharger depuis : https://github.com/UB-Mannheim/tesseract/wiki
```

---

## Utilisation pas à pas

### 1. Prétraitement NLP

```bash
jupyter notebook notebooks/01_Data_Preprocessing.ipynb
```

Résultat : `processed_data/processed_laws.csv` + visualisations

### 2. Création des embeddings et évaluation

```bash
jupyter notebook notebooks/02_Model_Training.ipynb
```

Résultat : `vector_db/faiss_index.bin` + `vector_db/metadata.pkl` + métriques

### 3. Test du pipeline RAG

```bash
jupyter notebook notebooks/03_RAG_Pipeline.ipynb
```

### 4. Lancer l'interface Streamlit

```bash
export ANTHROPIC_API_KEY="sk-ant-..."   # Linux/macOS
# set ANTHROPIC_API_KEY=sk-ant-...       # Windows

streamlit run app/streamlit_app.py
```

Ouvrir dans le navigateur : `http://localhost:8501`

---

## Notebooks

### 📓 01_Data_Preprocessing.ipynb

| Section | Description |
|---------|-------------|
| Exploration | Statistiques descriptives, aperçu des données |
| Extraction PDF | PyMuPDF + OCR Tesseract pour PDFs scannés |
| Nettoyage | Suppression caractères inutiles, normalisation |
| Normalisation arabe | Suppression diacritiques, normalisation alef |
| Tokenisation | Par mots, gestion FR et AR |
| Stopwords | Suppression mots vides juridiques FR/AR |
| Métadonnées | Extraction peines, amendes, mots-clés |
| Visualisations | 4 graphiques (catégories, langues, mots, heatmap) |
| Export | `processed_laws.csv` |

### 📓 02_Model_Training.ipynb

| Section | Description |
|---------|-------------|
| Embeddings | `paraphrase-multilingual-MiniLM-L12-v2` (384 dims) |
| Index FAISS | `IndexFlatIP` (cosine similarity) |
| Classification ML | Logistic Regression, SVM, Random Forest, Gradient Boosting |
| Métriques | Accuracy, Precision, Recall, F1-Score |
| Confusion Matrix | Heatmap seaborn |
| Validation croisée | 5-Fold stratifié |
| Export | `models/best_classifier.pkl`, `vector_db/faiss_index.bin` |

### 📓 03_RAG_Pipeline.ipynb

| Section | Description |
|---------|-------------|
| Retriever | `MoroccanLegalRetriever` avec filtre par catégorie |
| Agent RAG | `MoroccanLegalAgent` (FAISS + Claude) |
| Tests | 5 requêtes (FR + AR) |
| Évaluation | Recall@1, Recall@3, MRR |
| Visualisations | Scores de similarité, distribution par catégorie |

---

## Interface Streamlit

### Pages disponibles

| Page | Description |
|------|-------------|
| 🏠 Accueil | Statistiques, guide d'utilisation, domaines |
| 💬 Assistant | Saisie libre, analyse RAG + Claude |
| 📄 Document | Upload PDF/DOCX/image + analyse |
| 🔍 Explorer | Parcourir et filtrer les lois |
| 📜 Historique | Consultations passées + export JSON |

### Fonctionnalités clés

- **Multilingue** : Français et Arabe
- **Filtrage** : Par domaine juridique
- **Upload** : PDF, DOCX, TXT, PNG, JPG
- **Export** : Historique en JSON
- **Responsive** : Compatible mobile

---

## Données juridiques

### Sources incluses

| Fichier | Loi | Domaine |
|---------|-----|---------|
| Code des Obligations et Contrats | DOC-12-101 | Civil |
| Code du Travail | Loi 65-99 | Social |
| Loi contre les violences | Loi 103-13 | Pénal |
| Kafala (enfants abandonnés) | Loi 15-01 | Familial |
| Code de la nationalité | Loi 62-06 | Familial |
| Sécurité des produits | Loi 24-09 | Civil |
| Répression fraudes | Loi 13-83 | Pénal |
| Loi-cadre éducation | Loi 51-17 | Éducation |
| Fraude aux examens | Loi 02-00 | Éducation |
| Arbitrage & médiation | Loi 95-17 | Civil |
| Code pénal (extraits) | DOC-1-59-413 | Pénal |
| Code de la famille | Loi 70-03 | Familial |
| مجلة الشؤون الجنائية | — | Pénal (AR) |

### Ajouter de nouvelles lois

1. Placer le PDF dans `data/`
2. Exécuter le notebook `01_Data_Preprocessing.ipynb`
3. Ré-exécuter `02_Model_Training.ipynb` pour mettre à jour l'index
4. Relancer Streamlit

---

## Configuration API

### Clé Anthropic

1. Créer un compte sur [console.anthropic.com](https://console.anthropic.com)
2. Générer une clé API
3. La configurer de l'une des façons suivantes :

**Option A — Variable d'environnement (recommandé)**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Option B — Fichier `.env`**
```
ANTHROPIC_API_KEY=sk-ant-...
```

**Option C — Interface Streamlit**
Saisir la clé dans la barre latérale gauche.

### Modèle utilisé

```python
model = "claude-sonnet-4-6"
max_tokens = 1500
```

---

## FAQ

**Q: Les PDFs sont scannés et le texte n'est pas extrait correctement.**
R: Installez Tesseract avec les langues française et arabe. Le notebook gère l'OCR automatiquement.

**Q: L'index FAISS n'existe pas.**
R: Exécutez d'abord `02_Model_Training.ipynb` pour créer les embeddings et l'index.

**Q: L'application fonctionne sans clé API ?**
R: La recherche sémantique fonctionne sans API. La génération de réponse par Claude nécessite une clé Anthropic.

**Q: Comment ajouter des lois en arabe ?**
R: Ajoutez les articles dans `data/raw_laws.csv` avec `language='ar'`. Le modèle multilingue gère nativement l'arabe.

**Q: Quelle est la différence entre FAISS et ChromaDB ?**
R: Les deux sont supportés. FAISS est plus rapide pour la recherche, ChromaDB offre plus de fonctionnalités de gestion (persistance, métadonnées). Ce projet utilise FAISS par défaut.

---

## Avertissement légal

> ⚠️ Ce système est fourni à titre **informatif uniquement**. Il ne remplace pas l'avis d'un avocat ou d'un professionnel du droit marocain. Pour tout litige ou décision juridique importante, consultez un professionnel qualifié inscrit au barreau marocain.

---

*Système Juridique Intelligent Marocain — v1.0 | Anthropic Claude + FAISS + SentenceTransformers*
#   M o r o c c a n - I n t e l l i g e n t - L e g a l - S y s t e m - M u l t i l i n g u a l - F R - A R - R A G - A s s i s t a n t  
 