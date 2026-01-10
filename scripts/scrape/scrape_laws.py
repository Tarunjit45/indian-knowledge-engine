import os
import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus
from tqdm import tqdm
from pdfminer.high_level import extract_text

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
BASE_URL = 'https://www.indiacode.nic.in/'

os.makedirs(RAW_DIR, exist_ok=True)


ACTS = [
    {'act_id': 'IT_Act_2000', 'name': 'Information Technology Act 2000'},
    {'act_id': 'IPC_1860', 'name': 'Indian Penal Code 1860'},
    {'act_id': 'CrPC_1973', 'name': 'Code of Criminal Procedure 1973'},
    {'act_id': 'Evidence_1872', 'name': 'Indian Evidence Act 1872'},
    {'act_id': 'Contract_1872', 'name': 'Indian Contract Act 1872'},
    {'act_id': 'Companies_2013', 'name': 'Companies Act 2013'},
    {'act_id': 'TPA_1882', 'name': 'Transfer of Property Act 1882'},
    {'act_id': 'Limitation_1963', 'name': 'Limitation Act 1963'},
    {'act_id': 'Negotiable_1881', 'name': 'Negotiable Instruments Act 1881'},
    {'act_id': 'GST_2017', 'name': 'Goods and Services Tax Act 2017'},
]


def save_json(obj, fname):
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def download_and_extract(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    content_type = r.headers.get('Content-Type', '').lower()
    if 'pdf' in content_type or url.lower().endswith('.pdf'):
        # save pdf
        fname = os.path.basename(url.split('?')[0]) or url.replace('://', '_')
        pdf_path = os.path.join(RAW_DIR, fname)
        with open(pdf_path, 'wb') as f:
            f.write(r.content)
        try:
            text = extract_text(pdf_path)
        except Exception:
            text = ''
        return fname, text
    else:
        soup = BeautifulSoup(r.text, 'lxml')
        for s in soup(['script', 'style', 'noscript']):
            s.extract()
        text = soup.get_text(separator='\n')
        return None, text


def find_act_url_by_search(act_name):
    # Use India Code search endpoint to find the first result for the act name
    q = quote_plus(act_name)
    search_url = urljoin(BASE_URL, f'search?q={q}')
    r = requests.get(search_url, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'lxml')
    # heuristics: find first link that looks like a handle to an act
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/handle/' in href or 'indiacode.nic.in' in href:
            return urljoin(BASE_URL, href)
    # fallback: first absolute link
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('http'):
            return href
    return None


def process_act(act):
    name = act['name']
    act_id = act['act_id']
    print('Searching for', name)
    try:
        url = find_act_url_by_search(name)
        if not url:
            print('No URL found for', name)
            return
        fname, text = download_and_extract(url)
    except Exception as e:
        print('Failed to fetch', name, e)
        return
    # try to infer year if missing
    m = re.search(r"(\b[0-9]{4}\b)", text)
    year = int(m.group(1)) if m else None
    out = {
        'act_name': name,
        'year': year,
        'source': url,
        'raw_text': text or '',
        'filename': fname
    }
    out_path = os.path.join(RAW_DIR, f"{act_id}.json")
    save_json(out, out_path)


if __name__ == '__main__':
    print('Hardcoded base:', BASE_URL)
    print('Targeting 10 acts from India Code (only)')
    for act in tqdm(ACTS):
        process_act(act)
    print('Done. Raw JSONs saved under', RAW_DIR)
