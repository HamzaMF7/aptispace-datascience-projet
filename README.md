# 📊 Mon Projet Data Science

[![CI Compilation Pipeline](https://github.com/aptitek/aptispace-datascience-projet/actions/workflows/ci.yml/badge.svg)](https://github.com/aptitek/aptispace-datascience-projet/actions/workflows/ci.yml)
[GitHub Release](../../releases/latest)
[Quarto](https://quarto.org)
[Typst](https://typst.app)
[Python](https://python.org)

> **Bienvenue dans le portail d'accueil de notre Projet Data Science.**
> Ce dépôt contient l'intégralité du pipeline analytique (de l'acquisition multi-sources des données jusqu'à l'évaluation et la communication des résultats).
>
> Pour préserver la propreté de l'historique et simplifier la collaboration, **toutes les compilations de rapports sont déportées sur notre intégration continue (CI)**. Les livrables finaux sont publiés automatiquement à chaque mise à jour.

---

## 📥 Livrables du Projet (Rapports & Supports)

Les rapports compilés dans tous les formats, ainsi que le code source exécutable et ses journaux, sont mis à jour en temps réel à chaque push et disponibles au téléchargement sur la **[dernière version du Release GitHub](../../releases/latest)**.

| Format | Description | Lien de Téléchargement |
| :--- | :--- | :--- |
| **📄 Rapport PDF** | Rapport complet mis en page de haute qualité via **Typst** | [**Télécharger le PDF**](../../releases/download/latest/rapport.pdf) |
| **🌐 Rapport Interactif** | Rapport HTML complet intégrant le tableau de bord dynamique **Observable JS (OJS)** | [**Télécharger l'HTML**](../../releases/download/latest/rapport.html) |
| **📝 Rapport Markdown** | Version de lecture rapide optimisée pour l'affichage GitHub | [**Consulter le Markdown**](../../releases/download/latest/README.md) |
| **🧠 Scripts Python** | Archive compressée des scripts extraits de tous les notebooks | [**Télécharger les Sources (.zip)**](../../releases/download/latest/sources.zip) |
| **🪵 Journaux d'Exécution** | Archive de tous les logs de compilation et d'exécution | [**Télécharger les Logs (.zip)**](../../releases/download/latest/logs.zip) |

*Note : Si vous avez forké ce dépôt, vos propres compilations seront disponibles dans l'onglet **Releases** de votre propre dépôt GitHub après l'exécution du pipeline Actions.*

---

## 📂 Structure du Projet

```text
├── .github/workflows/      # Pipelines d'intégration continue
├── build/                  # Fichiers de compilation générés (exclus de Git)
│   ├── src/                # Scripts Python extraits des notebooks
│   ├── logs/               # Rapports d'exécution de chaque étape
│   ├── notebooks/          # Fichiers Quarto Markdown intermédiaires
│   └── report/             # PDF, HTML et Markdown compilés finaux
├── data/                   # Dossier de stockage des données
│   ├── raw/                # Données brutes sources
│   └── processed/          # Données nettoyées après Wrangling
├── notebooks/              # Travaux pratiques (fichiers .ipynb d'origine)
│   ├── 01_acquisition.ipynb
│   ├── 02_wrangling.ipynb
│   ├── ...
├── report/                 # Modèles et configurations des rapports
│   ├── rapport.qmd         # Fichier maître du rapport
│   └── slides.qmd          # Support de soutenance RevealJS
└── tools/                  # Utilitaires de compilation et de preprocessing
```

---

## 🛠️ Exécuter et compiler localement

Toutes les tâches du projet sont orchestrées simplement via le gestionnaire de tâches **Go-Task** (`task`).

### 1. Prérequis

Assurez-vous d'avoir installé :
- [Python 3.12](https://www.python.org/)
- [Quarto CLI](https://quarto.org/docs/get-started/)
- [Go-Task](https://taskfile.dev/installation/)

Installez ensuite les dépendances du projet :
```bash
pip install -r requirements.txt
```

### 2. Commandes de compilation rapides

Depuis la racine du projet, lancez :

* **Compiler l'intégralité du pipeline et des rapports** (génère tout dans `build/`) :
  ```bash
  task render
  ```
* **Prévisualiser dynamiquement le rapport dans le navigateur** (rechargement automatique lors de la saisie) :
  ```bash
  task preview
  ```
* **Compiler uniquement le guide d'installation** :
  ```bash
  task install-guide
  ```
* **Nettoyer tous les fichiers temporaires et compilations locales** :
  ```bash
  task clean
  ```