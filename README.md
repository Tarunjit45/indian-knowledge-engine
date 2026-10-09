# 🇮🇳 Indian Knowledge Engine — Cultural & Historical Knowledge Indexer

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![BeautifulSoup](https://img.shields.io/badge/Scraper-BeautifulSoup4-388E3C?style=for-the-badge)](https://pypi.org/project/beautifulsoup4/)
[![PDF Parsing](https://img.shields.io/badge/Parsing-PDFMiner.six-FF6F00?style=for-the-badge)](https://pypi.org/project/pdfminer.six/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

An automated ingestion, cleaning, and indexing pipeline designed to extract, sanitize, and structure knowledge from Indian historical archives, cultural encyclopedias, and open governmental publications.

---

## 📌 Architecture & ETL Pipeline

```
[ Cultural Portals, Archives & PDF Gazettes ]
                      |
                      v  `scripts/scrape/`
+-------------------------------------------------------------+
|                     1. Scraper Module                       |
|        BeautifulSoup4 web scrapers & PDFMiner.six extractors|
+-------------------------------------------------------------+
                      |
                      v  `scripts/clean/`
+-------------------------------------------------------------+
|                     2. Cleaning & Sanitization              |
|        Regex normalization, script transliteration, dedup   |
+-------------------------------------------------------------+
                      |
                      v  `scripts/build_db/`
+-------------------------------------------------------------+
|                     3. Database Builder                     |
|        Constructs structured SQLite index & embeddings      |
+-------------------------------------------------------------+
```

---

## 📁 Repository Structure

```text
indian-knowledge-engine/
├── scripts/
│   ├── scrape/         # Web crawlers & document extraction workers
│   ├── clean/          # Text sanitization, encoding normalization & deduplication
│   └── build_db/       # SQLite schema builder & search indexer
├── data/               # Raw and processed text repositories
├── docs/               # Architecture guidelines and data schemas
├── requirements.txt    # Dependencies (requests, beautifulsoup4, pdfminer.six, tqdm, lxml)
├── LICENSE             # MIT License
└── README.md
```

---

## 🚀 Getting Started

### 1. Installation
```bash
git clone https://github.com/Tarunjit45/indian-knowledge-engine.git
cd indian-knowledge-engine

pip install -r requirements.txt
```

### 2. Execute Data Pipeline
```bash
# Run web & document extraction
python scripts/scrape/main.py

# Clean extracted text corpora
python scripts/clean/sanitize.py

# Build search database
python scripts/build_db/build.py
```

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
