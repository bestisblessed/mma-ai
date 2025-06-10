"""
Scrape all Wikidata URLs for MMA fighters and events
"""

import csv
import time
from SPARQLWrapper import SPARQLWrapper, JSON
import os

wikidata_dir = "data/wikidata"
os.makedirs(wikidata_dir, exist_ok=True)

ENDPOINT = "https://query.wikidata.org/sparql"
BATCH   = 10_000            # hard limit per WDQS call
DELAY   = 1.0               # be nice to the endpoint

def fetch_batch_for_property(prop: str, offset: int) -> list[str]:
    query = f"""
    SELECT ?fighter WHERE {{
      ?fighter wdt:{prop} ?id .
      ?fighter wdt:P31 wd:Q5 .
    }} LIMIT {BATCH} OFFSET {offset}
    """
    sparql = SPARQLWrapper(ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return [
        b['fighter']['value']
        for b in sparql.query().convert()['results']['bindings']
    ]

def fetch_all_for_property(prop: str) -> list[str]:
    urls, offset = [], 0
    while True:
        batch = fetch_batch_for_property(prop, offset)
        if not batch:
            break
        urls.extend(batch)
        offset += BATCH
        time.sleep(DELAY)
    return urls

def fetch_batch_for_event_property(prop: str, offset: int) -> list[str]:
    query = f"""
    SELECT ?event WHERE {{
      ?event wdt:{prop} ?id .
    }} LIMIT {BATCH} OFFSET {offset}
    """
    sparql = SPARQLWrapper(ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return [
        b['event']['value']
        for b in sparql.query().convert()['results']['bindings']
    ]

def fetch_all_for_event_property(prop: str) -> list[str]:
    urls, offset = [], 0
    while True:
        batch = fetch_batch_for_event_property(prop, offset)
        if not batch:
            break
        urls.extend(batch)
        offset += BATCH
        time.sleep(DELAY)
    return urls

def save_urls_to_csv(urls: list[str], filename: str) -> None:
    with open(filename, "w", newline='', encoding="utf-8") as f:
        csv.writer(f).writerows([["wikidata_url"], *[[u] for u in urls]])

def main() -> None:
    properties = {
        "P9722": "ufc_fighters_urls.csv",      # UFC athlete ID
        "P9726": "bellator_fighters_urls.csv", # Bellator fighter ID
        "P9727": "pfl_fighters_urls.csv",      # PFL fighter ID
        "P9728": "tapology_fighters_urls.csv", # Tapology fighter ID
        "P2818": "sherdog_fighters_urls.csv",  # Sherdog fighter ID
    }
    event_properties = {
        "P2090": "sherdog_events_urls.csv",    # Sherdog event ID
        "P2091": "tapology_events_urls.csv",   # Tapology event ID
        "P2092": "ufc_events_urls.csv",        # UFC event ID
    }
    for prop, filename in properties.items():
        print(f"Fetching fighters for property {prop} → {filename}")
        urls = fetch_all_for_property(prop)
        save_urls_to_csv(urls, os.path.join(wikidata_dir, filename))
        print(f"Saved {len(urls)} fighter URLs → {filename}")
    for prop, filename in event_properties.items():
        print(f"Fetching events for property {prop} → {filename}")
        urls = fetch_all_for_event_property(prop)
        save_urls_to_csv(urls, os.path.join(wikidata_dir, filename))
        print(f"Saved {len(urls)} event URLs → {filename}")

if __name__ == "__main__":
    main()
