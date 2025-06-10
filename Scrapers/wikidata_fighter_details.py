import csv
import os
import re
import time
from SPARQLWrapper import SPARQLWrapper, JSON

DATA_DIR = "data/wikidata"
ORG_CSVS = [
    "ufc_fighters_urls.csv",
    "bellator_fighters_urls.csv",
    "pfl_fighters_urls.csv",
    "tapology_fighters_urls.csv",
    "sherdog_fighters_urls.csv",
]
MASTER_CSV = os.path.join(DATA_DIR, "master_fighters.csv")
ENDPOINT = "https://query.wikidata.org/sparql"
BATCH_SIZE = 50
DELAY = 1.0

# Properties to fetch
PROPS = {
    'name': 'rdfs:label',
    'dob': 'wdt:P569',
    'nationality': 'wdt:P27',
    'gender': 'wdt:P21',
    'ufc_id': 'wdt:P9722',
    'bellator_id': 'wdt:P9726',
    'pfl_id': 'wdt:P9727',
    'tapology_id': 'wdt:P9728',
    'sherdog_id': 'wdt:P2818',
}

def read_all_fighter_qids():
    qids = set()
    for fname in ORG_CSVS:
        path = os.path.join(DATA_DIR, fname)
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                m = re.search(r'/entity/(Q\d+)', row['wikidata_url'])
                if m:
                    qids.add(m.group(1))
    qids = sorted(qids)
    print(f"First 5 QIDs: {qids[:5]}")
    return qids

def batch(iterable, n):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]

def fetch_fighter_details(qids):
    qid_str = ' '.join(f'wd:{qid}' for qid in qids)
    query = f"""
    SELECT ?qid ?name ?dob ?nationalityLabel ?genderLabel ?ufc_id ?bellator_id ?pfl_id ?tapology_id ?sherdog_id WHERE {{
      VALUES ?qid {{ {qid_str} }}
      OPTIONAL {{ ?qid rdfs:label ?name FILTER (LANG(?name) = 'en') }}
      OPTIONAL {{ ?qid wdt:P569 ?dob }}
      OPTIONAL {{ ?qid wdt:P27 ?nationality . ?nationality rdfs:label ?nationalityLabel FILTER (LANG(?nationalityLabel) = 'en') }}
      OPTIONAL {{ ?qid wdt:P21 ?gender . ?gender rdfs:label ?genderLabel FILTER (LANG(?genderLabel) = 'en') }}
      OPTIONAL {{ ?qid wdt:P9722 ?ufc_id }}
      OPTIONAL {{ ?qid wdt:P9726 ?bellator_id }}
      OPTIONAL {{ ?qid wdt:P9727 ?pfl_id }}
      OPTIONAL {{ ?qid wdt:P9728 ?tapology_id }}
      OPTIONAL {{ ?qid wdt:P2818 ?sherdog_id }}
    }}
    """
    sparql = SPARQLWrapper(ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()['results']['bindings']
    fighters = []
    for r in results:
        fighters.append({
            'qid': r['qid']['value'].split('/')[-1],
            'name': r.get('name', {}).get('value', ''),
            'dob': r.get('dob', {}).get('value', ''),
            'nationality': r.get('nationalityLabel', {}).get('value', ''),
            'gender': r.get('genderLabel', {}).get('value', ''),
            'ufc_id': r.get('ufc_id', {}).get('value', ''),
            'bellator_id': r.get('bellator_id', {}).get('value', ''),
            'pfl_id': r.get('pfl_id', {}).get('value', ''),
            'tapology_id': r.get('tapology_id', {}).get('value', ''),
            'sherdog_id': r.get('sherdog_id', {}).get('value', ''),
        })
    return fighters

def main():
    qids = read_all_fighter_qids()
    print(f"Total unique fighters: {len(qids)}")
    all_fighters = []
    for qid_batch in batch(qids, BATCH_SIZE):
        fighters = fetch_fighter_details(qid_batch)
        all_fighters.extend(fighters)
        print(f"Processed {len(all_fighters)}/{len(qids)} fighters...")
        time.sleep(DELAY)
    # Clean and deduplicate by QID
    seen = set()
    clean_fighters = []
    for f in all_fighters:
        if f['qid'] not in seen:
            seen.add(f['qid'])
            clean_fighters.append(f)
    # Write to CSV
    with open(MASTER_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'qid', 'name', 'dob', 'nationality', 'gender',
            'ufc_id', 'bellator_id', 'pfl_id', 'tapology_id', 'sherdog_id'
        ])
        writer.writeheader()
        for row in clean_fighters:
            writer.writerow(row)
    print(f"Saved {len(clean_fighters)} fighters to {MASTER_CSV}")

if __name__ == "__main__":
    main() 