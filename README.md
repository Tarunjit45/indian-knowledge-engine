Indian Knowledge Engine — Laws (v0.1)

This repository collects, normalizes, and indexes Indian legislation (Acts & Sections) from official sources for research and search.

What this is
- A reproducible pipeline: scrape -> clean -> build SQLite (with FTS)
- Data stored under data/ (raw, cleaned, structured)

What this is NOT
- Legal advice. Use primary sources and consult lawyers for decisions.

Quick start
1. Install dependencies: pip install -r requirements.txt
2. Scrape (example): python scripts/scrape/scrape_laws.py
3. Clean raw data: python scripts/clean/clean_laws.py
4. Build DB: python scripts/build_db/build_db.py

Repository layout
```
indian-knowledge-engine/
├── data/
│   ├── raw/
│   ├── cleaned/
│   └── structured/
├── scripts/
│   ├── scrape/
│   ├── clean/
│   └── build_db/
├── db/
│   └── indian_laws.db
├── docs/
│   └── schema.md
├── README.md
└── requirements.txt
```

Vision (5–10 years): curate a maintained, documented, and queryable corpus of primary legislative texts from official sources to power research and trustworthy downstream tools.

Limitations
- Sources: Scraper is hard-limited to India Code (official consolidated Acts). Do not add other sites without explicit review.
- Coverage: Initial run targets 10 Acts only. Expect missing or malformed sections for some Acts.
- Cleaning: `scripts/clean/clean_laws.py` enforces a strict numeric-section model and will intentionally fail when numeric section headings are not found. This surfaces real-world inconsistencies for manual review.
- Not production-ready: No embeddings, UI, or packaging. This is a data-first, minimal pipeline.

Data & DB policy
-----------------

This repository follows a reproducible data contract. The SQLite database is treated as a derived artifact (Option A):

- **DB is NOT a source of truth.** The canonical pipeline is: `scrape` -> `clean` -> `build_db` and the database is produced from files under `data/cleaned/`.
- To reproduce the DB from scratch:

```bash
git clone <repo>
pip install -r requirements.txt
python scripts/scrape/scrape_laws.py
python scripts/clean/clean_laws.py
python scripts/build_db/build_db.py
```

- An initial manifest `data/manifest.json` is included to record provenance; update it after running the scraper/cleaner.
- Commit history must not treat `db/*.db` as authoritative. The repository includes `.gitignore` rules to avoid checking in built DB files.

If you prefer to keep a committed DB (Option B) you MUST provide a manifest including `source URLs`, `scrape timestamp`, `act count`, `section count`, and `schema version`. This project currently follows Option A (DB is derived).
