import os
import re
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / 'data' / 'raw'
CLEAN_DIR = BASE_DIR / 'data' / 'cleaned'
STRUCT_DIR = BASE_DIR / 'data' / 'structured'

CLEAN_DIR.mkdir(parents=True, exist_ok=True)
STRUCT_DIR.mkdir(parents=True, exist_ok=True)


def normalize_whitespace(s):
    return re.sub(r"[\t\r ]+", ' ', s).strip()


def remove_headers_footers(text):
    lower = text.lower()
    idx = None
    for marker in ['be it enacted', 'an act to', 'preliminary', '\nshort title']:
        i = lower.find(marker)
        if i != -1:
            idx = i
            break
    if idx and idx > 0:
        text = text[idx:]
    lines = [l for l in text.splitlines() if l.strip()]
    filtered = []
    prev = None
    for l in lines:
        if l == prev:
            continue
        filtered.append(l)
        prev = l
    return '\n'.join(filtered)


def split_sections_strict(text):
    """
    Strictly split by numbered section headings common in Indian Acts:
    e.g., '375. Rape.—A man is said to commit...'
    Returns list of dicts with keys: section_number, title, text
    """
    parts = []
    # Pattern for numbered sections: start of line, digits, optional clause, dot or ) or full stop, then title
    pattern = re.compile(r"(?m)^(\d{1,4})\.?\s*(?:[-–—\)]\s*)?(?:([A-Z][^\n\r]{0,200})\s*[\n\r])")
    matches = list(pattern.finditer(text))
    if matches:
        for i, m in enumerate(matches):
            sec_no = m.group(1)
            title = m.group(2) or ''
            start = m.end()
            end = matches[i+1].start() if i+1 < len(matches) else len(text)
            body = text[start:end].strip()
            parts.append({'section_number': sec_no, 'title': normalize_whitespace(title), 'text': normalize_whitespace(body)})
    else:
        # fallback: no numeric sections found -> treat entire text as single chunk
        parts = [{'section_number': None, 'title': None, 'text': normalize_whitespace(text)}]
    return parts


def make_strict_section_model(act_id, section):
    # Enforce strict output schema for each section
    sec_no = section.get('section_number')
    if not sec_no:
        # deliberately surface failure for unstructured acts
        raise ValueError(f"Missing numeric section number in act {act_id}")
    section_id = f"{act_id}_{sec_no}"
    return {
        'act_id': act_id,
        'section_id': section_id,
        'section_number': sec_no,
        'title': section.get('title') or '',
        'text': section.get('text') or '',
        'notes': None
    }


def make_act_id(title):
    s = re.sub(r"[^A-Za-z0-9]+", '_', title).upper()
    return s[:60]


if __name__ == '__main__':
    files = list(RAW_DIR.glob('*.json'))
    if not files:
        print('No raw JSON files found in', RAW_DIR)
        raise SystemExit(1)
    errors = []
    for p in files:
        with open(p, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        text = raw.get('raw_text', '')
        text = remove_headers_footers(text)
        try:
            raw_sections = split_sections_strict(text)
        except Exception as e:
            errors.append(f"{p.name}: split error: {e}")
            continue
        title = raw.get('act_name') or p.stem
        year = raw.get('year')
        act_id = make_act_id(title)
        structured_sections = []
        for sec in raw_sections:
            try:
                s = make_strict_section_model(act_id, sec)
                # basic validation
                if not s['text']:
                    errors.append(f"{p.name}: empty text for section {s['section_id']}")
                structured_sections.append(s)
            except Exception as e:
                errors.append(f"{p.name}: {e}")
        cleaned = {
            'act_id': act_id,
            'title': title,
            'year': year,
            'source': raw.get('source'),
            'sections': structured_sections
        }
        out_clean = CLEAN_DIR / f"{p.stem}.clean.json"
        with open(out_clean, 'w', encoding='utf-8') as f:
            json.dump(cleaned, f, ensure_ascii=False, indent=2)
        out_struct = STRUCT_DIR / f"{act_id}.json"
        with open(out_struct, 'w', encoding='utf-8') as f:
            json.dump(cleaned, f, ensure_ascii=False, indent=2)
    if errors:
        print('Cleaning completed with errors:')
        for e in errors:
            print('-', e)
        # Fail loudly so user inspects issues (per STEP 3)
        raise SystemExit(2)
    print('Cleaning complete. Structured JSONs written to', STRUCT_DIR)
