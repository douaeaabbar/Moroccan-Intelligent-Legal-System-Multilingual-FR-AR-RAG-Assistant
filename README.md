#  Système Juridique Intelligent Marocain
### *المستشار القانوني المغربي الذكي*

> Assistant juridique IA basé sur les lois marocaines, combinant RAG + LLM (Claude) + FAISS

---


## Vue d'ensemble

Le **Système Juridique Intelligent Marocain** est une application d'intelligence artificielle qui permet aux utilisateurs de :

-  **Décrire leur situation juridique** en arabe ou en français
-  **Obtenir les textes de loi pertinents** via recherche sémantique
-  **Recevoir une analyse juridique structurée** générée par Claude
-  **Analyser des documents** (PDF, DOCX, images scannées)
-  **Explorer la base juridique marocaine**

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


## Avertissement légal

> ⚠️ Ce système est fourni à titre **informatif uniquement**. Il ne remplace pas l'avis d'un avocat ou d'un professionnel du droit marocain. Pour tout litige ou décision juridique importante, consultez un professionnel qualifié inscrit au barreau marocain.

