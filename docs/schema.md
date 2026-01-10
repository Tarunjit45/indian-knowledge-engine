Schema for Indian Laws dataset

JSON (raw per-act) — data/raw/*.json
- act_name: Title of the Act
- year: Numeric year (if available)
- source: Source URL (official)
- raw_text: Full extracted text (messy)
- filename: raw saved filename (pdf/html)

JSON (cleaned per-act) — data/cleaned/*.json
- act_id: Unique id (e.g., IT_ACT_2000)
- title: Clean title
- year: 2000
- source: original source URL
- sections: list of {
  - section: string identifier (e.g., "43A")
  - text: cleaned section text
}

SQLite DB — db/indian_laws.db
Tables:
- acts(id INTEGER PRIMARY KEY, act_id TEXT UNIQUE, title TEXT, year INTEGER, source TEXT, raw_path TEXT)
- sections(id INTEGER PRIMARY KEY, act_id TEXT, section TEXT, text TEXT)
- metadata(key TEXT PRIMARY KEY, value TEXT)

Full-text search:
- sections_fts: FTS5 virtual table (section, text) linked to `sections` table contents for fast search.

Extensibility:
- Add more metadata columns to `acts` (e.g., jurisdiction, amended_date)
- Store original PDFs under data/raw/pdfs/ and keep checksums in metadata

Contributing:
- Only add sources from official government / court / gazette portals.
- Keep raw extracts intact; cleaning should aim for fidelity to original section boundaries.
