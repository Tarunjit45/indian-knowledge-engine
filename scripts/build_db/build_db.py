import sqlite3
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[2]
# Build step reads from data/cleaned/ (normalized per-act JSON)
CLEAN_DIR = BASE_DIR / 'data' / 'cleaned'
DB_PATH = BASE_DIR / 'db' / 'indian_laws.db'
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

SCHEMA = '''
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS acts(
    id INTEGER PRIMARY KEY,
    act_id TEXT UNIQUE,
    title TEXT,
    year INTEGER,
    source TEXT,
    raw_path TEXT
);
CREATE TABLE IF NOT EXISTS sections(
    id INTEGER PRIMARY KEY,
    act_id TEXT,
    section_id TEXT UNIQUE,
    section_number TEXT,
    title TEXT,
    text TEXT,
    notes TEXT,
    FOREIGN KEY(act_id) REFERENCES acts(act_id)
);
-- FTS5 virtual table for sections full-text search (title + text)
CREATE VIRTUAL TABLE IF NOT EXISTS sections_fts USING fts5(section_id, section_number, title, text, content='sections', content_rowid='id');
CREATE TABLE IF NOT EXISTS metadata(key TEXT PRIMARY KEY, value TEXT);
'''


def load_cleaned():
    files = list(CLEAN_DIR.glob('*.json'))
    for p in files:
        with open(p, 'r', encoding='utf-8') as f:
            yield json.load(f)


def build_db():
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.executescript(SCHEMA)
    conn.commit()

    act_count = 0
    section_count = 0

    for act in load_cleaned():
        act_count += 1
        cur.execute('INSERT OR IGNORE INTO acts(act_id, title, year, source, raw_path) VALUES(?,?,?,?,?)', (
            act.get('act_id'), act.get('title'), act.get('year'), act.get('source'), act.get('raw_path')
        ))
        for sec in act.get('sections', []):
            section_count += 1
            cur.execute('INSERT OR IGNORE INTO sections(act_id, section_id, section_number, title, text, notes) VALUES(?,?,?,?,?,?)', (
                act.get('act_id'), sec.get('section_id'), sec.get('section_number'), sec.get('title'), sec.get('text'), sec.get('notes')
            ))
    conn.commit()
    # populate FTS from sections
    cur.execute("INSERT INTO sections_fts(rowid, section_id, section_number, title, text) SELECT id, section_id, section_number, title, text FROM sections;")
    conn.commit()

    # write simple metadata
    cur.execute('INSERT OR REPLACE INTO metadata(key, value) VALUES(?,?)', ('built_at', datetime.utcnow().isoformat() + 'Z'))
    cur.execute('INSERT OR REPLACE INTO metadata(key, value) VALUES(?,?)', ('act_count', str(act_count)))
    cur.execute('INSERT OR REPLACE INTO metadata(key, value) VALUES(?,?)', ('section_count', str(section_count)))
    conn.commit()
    conn.close()
    print('DB built at', DB_PATH)


if __name__ == '__main__':
    build_db()
