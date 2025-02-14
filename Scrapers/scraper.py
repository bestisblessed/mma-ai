import subprocess
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from tqdm import tqdm
import warnings
import re
import csv
import os
from datetime import datetime
import glob
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from xml.etree.ElementTree import fromstring 
import shutil
import warnings
import random
import xml.etree.ElementTree as ET
if os.path.exists("data"):
    shutil.rmtree("data")
if os.path.exists("ufc_database.db"):
    os.remove("ufc_database.db")
os.makedirs("data")
urls = [
    'https://www.sherdog.com/organizations/Ultimate-Fighting-Championship-UFC-2/recent-events/1',
    'https://www.sherdog.com/organizations/Ultimate-Fighting-Championship-UFC-2/recent-events/2',
    'https://www.sherdog.com/organizations/Ultimate-Fighting-Championship-UFC-2/recent-events/3',
    'https://www.sherdog.com/organizations/Ultimate-Fighting-Championship-UFC-2/recent-events/4',
    'https://www.sherdog.com/organizations/Ultimate-Fighting-Championship-UFC-2/recent-events/5',
    'https://www.sherdog.com/organizations/Ultimate-Fighting-Championship-UFC-2/recent-events/6',
    'https://www.sherdog.com/organizations/Ultimate-Fighting-Championship-UFC-2/recent-events/7',
    'https://www.sherdog.com/organizations/Ultimate-Fighting-Championship-UFC-2/recent-events/8'
]
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
]
headers = {"User-Agent": random.choice(user_agents)}
df = pd.read_csv('./data/event_urls_sherdog.csv') if os.path.isfile('./data/event_urls_sherdog.csv') else pd.DataFrame(columns=['Event_URL'])
existing_urls = set(df['Event_URL'])
print(f"Starting to scrape {len(urls)} URLs...")
for i, url in enumerate(urls, 1):
    print(f"Processing URL {i}/{len(urls)}")
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        specific_div = soup.find('div', {'class': 'single_tab', 'id': 'recent_tab'})
        if specific_div:
            new_urls = [a.get('href') for a in specific_div.find_all('a', itemprop='url') if a.get('href') and a.get('href') not in existing_urls]
            df = pd.concat([df, pd.DataFrame(new_urls, columns=['Event_URL'])], ignore_index=True)
    except requests.RequestException:
        print(f"Failed to process URL {i}")
        pass
df.to_csv('./data/event_urls_sherdog.csv', index=False)
print("Updated event URLs saved.")
urls_to_delete = {
    "/events/UFC-233-Ultimate-Fighting-Championship-233-72021",
    "/events/UFC-Fight-Night-97-Lamas-vs-Penn-90890",
    "/events/UFC-176-Aldo-vs-Mendes-2-37609",
    "/events/UFC-151-Jones-vs-Henderson-25809"
}
df = pd.read_csv("./data/event_urls_sherdog.csv")
df = df[~df["Event_URL"].isin(urls_to_delete)]
df.to_csv("./data/event_urls_sherdog.csv", index=False)
print("Broken URLs removed.")
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
]
df = pd.read_csv('./data/event_urls_sherdog.csv')
df['Event_URL'] = "https://sherdog.com" + df['Event_URL'].astype(str)
event_dates = []
with requests.Session() as session:
    session.headers.update({"User-Agent": random.choice(user_agents)})
    with ThreadPoolExecutor(max_workers=40) as executor:
        futures = {executor.submit(lambda url: session.get(url, headers={"User-Agent": random.choice(user_agents)}, timeout=30), url): url for url in df['Event_URL']}
        for future in tqdm(as_completed(futures), total=len(df['Event_URL']), desc="Scraping Events", unit="Event"):
            url = futures[future]
            try:
                response = future.result()
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    event_date_meta = soup.find('meta', itemprop='startDate')
                    event_dates.append(event_date_meta['content'].strip() if event_date_meta else None)
                else:
                    event_dates.append("Error")
            except requests.exceptions.RequestException:
                event_dates.append("Error")
df['Event Date'] = event_dates
df.to_csv('./data/event_urls_sherdog.csv', index=False)
print("Event dates appended successfully.")
print(f"Total number of rows including the header in event_urls_sherdog.csv: {len(df)}")
print(f"Column names: {list(df.columns)}")
warnings.filterwarnings("ignore", category=FutureWarning)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}
urls_df = pd.read_csv('data/event_urls_sherdog.csv')
all_data = []
def fetch_event_data(url, session):
    full_url = f'https://sherdog.com{url}' if not url.startswith('http') else url
    event_data = []
    try:
        with session.get(full_url, headers=headers) as response:
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                event_name = soup.find('span', itemprop='name').text.strip()
                event_location = soup.find('span', itemprop='location').text.strip()
                event_date = soup.find('meta', itemprop='startDate')['content'].strip()
                main_event_fighters = soup.find_all('div', class_='fighter')
                if main_event_fighters:
                    fighter1 = main_event_fighters[0].find('span', itemprop='name').text.strip()
                    fighter2 = main_event_fighters[1].find('span', itemprop='name').text.strip()
                    fighter1_id = main_event_fighters[0].find('a', itemprop='url')['href'].split('-')[-1]
                    fighter2_id = main_event_fighters[1].find('a', itemprop='url')['href'].split('-')[-1]
                    weight_class = soup.find('span', class_='weight_class').text.strip()
                    winning_fighter = fighter1  
                    winning_method_em = soup.find('em', string='Method').parent
                    winning_method = winning_method_em.contents[2].strip()
                    winning_round_em = soup.find('em', string='Round').parent
                    winning_round = winning_round_em.contents[2].strip()
                    winning_time_em = soup.find('em', string='Time').parent
                    winning_time = winning_time_em.contents[2].strip()
                    referee_em = soup.find('em', string='Referee').parent
                    referee = referee_em.find('a').text.strip()
                    event_data.append({
                        'Event Name': event_name,
                        'Event Location': event_location,
                        'Event Date': event_date,
                        'Fighter 1': fighter1,
                        'Fighter 2': fighter2,
                        'Fighter 1 ID': fighter1_id,
                        'Fighter 2 ID': fighter2_id,
                        'Weight Class': weight_class,
                        'Winning Fighter': winning_fighter,
                        'Winning Method': winning_method,
                        'Winning Round': winning_round,
                        'Winning Time': winning_time,
                        'Referee': referee,
                        'Fight Type': 'Main Event'
                    })
                other_bouts = soup.find_all('tr', itemprop='subEvent')
                for bout in other_bouts:
                    fighters = bout.find_all('div', class_='fighter_list')
                    if len(fighters) >= 2:
                        fighter1 = fighters[0].find('img')['title']
                        fighter2 = fighters[1].find('img')['title']
                        fighter1_url = fighters[0].find('a', itemprop='url')['href']
                        fighter2_url = fighters[1].find('a', itemprop='url')['href']
                        fighter1_id = fighter1_url.split('-')[-1]
                        fighter2_id = fighter2_url.split('-')[-1]
                        weight_class = bout.find('span', class_='weight_class')
                        weight_class = weight_class.text.strip() if weight_class else "Unknown"
                        winning_method = bout.find('td', class_='winby').find('b').get_text(strip=True)
                        winning_round = bout.find_all('td')[-2].get_text(strip=True)
                        winning_time = bout.find_all('td')[-1].get_text(strip=True)
                        referee = bout.find('td', class_='winby').find('a').get_text(strip=True)
                        event_data.append({
                            'Event Name': event_name,
                            'Event Location': event_location,
                            'Event Date': event_date,
                            'Fighter 1': fighter1,
                            'Fighter 2': fighter2,
                            'Fighter 1 ID': fighter1_id,
                            'Fighter 2 ID': fighter2_id,
                            'Weight Class': weight_class,
                            'Winning Fighter': fighter1,  
                            'Winning Method': winning_method,
                            'Winning Round': winning_round,
                            'Winning Time': winning_time,
                            'Referee': referee,
                            'Fight Type': 'Undercard'
                        })
        return event_data
    except Exception as e:
        print(f"Request failed for {full_url}: {e}")
        return None
session = requests.Session()
total_urls = len(urls_df['Event_URL'])
completed_requests = 0
with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
    futures = [executor.submit(fetch_event_data, url, session) for url in urls_df['Event_URL']]
    for future in concurrent.futures.as_completed(futures):
        data = future.result()
        completed_requests += 1
        progress_percentage = (completed_requests / total_urls) * 100
        print(f"Completed {completed_requests}/{total_urls} requests ({progress_percentage:.2f}%)")
        if data:
            all_data.extend(data)
df = pd.DataFrame(all_data)
file_path = './data/event_data_sherdog.csv'
write_mode = 'a' if os.path.isfile(file_path) else 'w'
df.to_csv(file_path, mode=write_mode, header=not os.path.isfile(file_path), index=False)
print("Data successfully written to data/event_data_sherdog.csv")
print(f"Total number of rows: {len(df)}")
print(f"Column names: {list(df.columns)}")
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
df.to_csv(file_path, index=False)
df = pd.read_csv('./data/event_data_sherdog.csv')
df2 = pd.DataFrame(columns=['Fighter', 'Fighter_ID'])
df2.to_csv('./data/fighter_id_sherdog.csv', index=False)
for index, row in df.iterrows():
    fighter1 = row['Fighter 1']
    fighter2 = row['Fighter 2']
    fighter1_id = row['Fighter 1 ID']
    fighter2_id = row['Fighter 2 ID']
    for fighter, fighter_id in zip([fighter1, fighter2], [fighter1_id, fighter2_id]):
        if fighter not in df2['Fighter'].values and fighter_id not in df2['Fighter_ID'].values:
            df2 = pd.concat([df2, pd.DataFrame([{'Fighter': fighter, 'Fighter_ID': fighter_id}])])  
df2.to_csv('./data/fighter_id_sherdog.csv', index=False)
print("Data successfully written to data/fighter_id_sherdog.csv")
print(f"Total number of rows: {len(df2)}")
print(f"Column names: {list(df2.columns)}")
df = pd.read_csv('./data/fighter_id_sherdog.csv')
df['Fighter'] = df['Fighter'].str.replace(r" '.+?'", "", regex=True)
df.to_csv('./data/fighter_id_sherdog.csv', index=False)
df = pd.read_csv('./data/event_data_sherdog.csv')
for col in ['Fighter 1', 'Fighter 2', 'Winning Fighter']:
    df[col] = df[col].str.replace(r" '.+?'", "", regex=True)
df.to_csv('./data/event_data_sherdog.csv', index=False)
df = pd.read_csv('./data/fighter_id_sherdog.csv')
df['UFC'] = 'y'
df.to_csv('./data/fighter_id_sherdog.csv', index=False)
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
df.to_csv('./data/fighter_id_sherdog.csv', index=False)
def scrape_fighter_general_info_sherdog(fighter, fighter_id):
    url = f'https://www.sherdog.com/fighter/{fighter_id}'
    headers = {"User-Agent": "'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'"}
    max_retries = 6  
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                break
        except (requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:
            retry_count += 1
            if retry_count == max_retries:
                print(f"Failed to fetch data for fighter {fighter} after {max_retries} retries")
                return {}
            print(f"Connection error, retrying in 10 seconds... (Attempt {retry_count}/{max_retries})")
            time.sleep(10)
            continue
    if response.status_code != 200:
        return {}
    soup = BeautifulSoup(response.content, 'html.parser')
    fighter_dict = {}
    try:
        fighter_data = soup.find('div', class_='fighter-data')
    except AttributeError:
        fighter_data = None
    try:
        birthdate = soup.find('span', itemprop='birthDate')
        birthdate = (birthdate.text).strip('""')
    except AttributeError:
        birthdate = '-'
    try:
        nationality = soup.find('strong', itemprop='nationality')
        nationality = (nationality.text).strip()
    except AttributeError:
        nationality = '-'
    try:
        hometown = soup.find('span', {'itemprop': 'addressLocality'}).text
        hometown = hometown.strip()
    except AttributeError:
        hometown = '-'
    try:
        association = soup.find('span', {'itemprop': 'name'}).text
        association = association.strip()
    except AttributeError:
        association = '-'
    try:
        weight_class_div = fighter_data.find('div', {'class': 'association-class'})
        links = weight_class_div.find_all('a')
        weight_class = links[-1].text
        weight_class = weight_class.strip()
    except (AttributeError, IndexError):
        weight_class = ''
    try:
        nickname = soup.find('span', class_='nickname')
        nickname = (nickname.text).strip('"')
    except AttributeError:
        nickname = '-'
    try:
        height = soup.find('b', itemprop='height')
        height = (height.text).strip('"')
    except AttributeError:
        height = '-'
    try:
        wins = soup.find('div', class_='winloses win').find_all('span')[1]
        wins = (wins.text).strip()
    except AttributeError:
        wins = '-'
    try:
        losses = soup.find('div', class_='winloses lose').find_all('span')[1]
        losses = (losses.text).strip()
    except AttributeError:
        losses = '-'
    dec_data_list = []
    try:
        win_type = fighter_data.find_all('div', class_='meter-title', string='DECISIONS')
        for method in win_type:
            if method.text.startswith('DECISIONS'):
                dec_data = method.find_next('div', class_='pl').text
                dec_data_list.append(dec_data)
        wins_dec = (dec_data_list[0]).strip()
        losses_dec = (dec_data_list[1]).strip()
    except (AttributeError, IndexError):
        wins_dec = '-'
        losses_dec = '-'
    ko_data_list = []
    try:
        win_type = soup.find_all('div', class_='meter-title')
        for method in win_type:
            if method.text.startswith('KO'):
                ko_data = method.find_next('div', class_='pl').text
                ko_data_list.append(ko_data)
        wins_ko = (ko_data_list[0]).strip()
        losses_ko = (ko_data_list[1]).strip()
    except (AttributeError, IndexError):
        wins_ko = '-'
        losses_ko = '-'
    sub_data_list = []
    try:
        win_type = fighter_data.find_all('div', class_='meter-title', string='SUBMISSIONS')
        for method in win_type:
            if method.text.startswith('SUBMISSIONS'):
                sub_data = method.find_next('div', class_='pl').text
                sub_data_list.append(sub_data)
        wins_sub = (sub_data_list[0]).strip()
        losses_sub = (sub_data_list[1]).strip()
    except (AttributeError, IndexError):
        wins_sub = '-'
        losses_sub = '-'
    fighter_dict = {
        'Fighter': fighter,
        'Nickname': nickname,
        'Birth Date': birthdate,
        'Nationality': nationality,
        'Hometown': hometown,
        'Association': association,
        'Weight Class': weight_class,
        'Height': height,
        'Wins': wins,
        'Losses': losses,
        'Win_Decision': wins_dec,
        'Win_KO': wins_ko,
        'Win_Sub': wins_sub,
        'Loss_Decision': losses_dec,
        'Loss_KO': losses_ko,
        'Loss_Sub': losses_sub,
        'Fighter_ID': fighter_id
    }
    return fighter_dict
def scrape_fighters_concurrently():
    warnings.filterwarnings("ignore", category=FutureWarning)
    df_fighter_id = pd.read_csv('./data/fighter_id_sherdog.csv')
    fighter_data_list = []
    total_fighters = len(df_fighter_id)
    fighters_processed = 0
    with ThreadPoolExecutor(max_workers=40) as executor:
        future_to_fighter = {executor.submit(scrape_fighter_general_info_sherdog, row['Fighter'], row['Fighter_ID']): row for index, row in df_fighter_id.iterrows()}
        for future in tqdm(as_completed(future_to_fighter), total=len(future_to_fighter)):
            fighter_data = future.result()
            if fighter_data:
                fighter_data_list.append(fighter_data)
            fighters_processed += 1
            print(f"Scraping Fighter Info: {fighters_processed}/{total_fighters} fighters processed")
    new_df = pd.DataFrame(fighter_data_list)
    new_df.to_csv('./data/fighter_info.csv', index=False)
scrape_fighters_concurrently()
df = pd.read_csv('./data/fighter_info.csv')
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
df.to_csv('./data/fighter_info.csv', index=False)
print("Data successfully written to data/fighter_info.csv")
print(f"Total number of rows: {len(df)}")
print(f"Column names: {list(df.columns)}")
os.makedirs('./data/fighters/', exist_ok=True)
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
})
def scrape_fighter_fights_sherdog(session, fighter_name, fighter_id, fighter_url):
    try:
        response = session.get(fighter_url, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', {'class': 'new_table fighter'})
            rows = table.find_all('tr')[1:] if table else []
            fight_data = []
            new_opponents = []
            for row in rows:
                cols = row.find_all('td')
                fight_dict = {
                    'Result': cols[0].text.strip(),
                    'Opponent': cols[1].find('a').text.strip() if cols[1].find('a') else '-',
                    'Event Date': cols[2].find_all('span')[-1].text.strip() if cols[2].find_all('span') else '-',
                    'Method/Referee': cols[3].text.strip().split('\n')[0],
                    'Rounds': cols[4].text.strip(),
                    'Time': cols[5].text.strip()
                }
                fight_data.append(fight_dict)
                opponent_link = cols[1].find('a')['href'] if cols[1].find('a') else None
                if opponent_link:
                    opponent_id = opponent_link.split('-')[-1]
                    new_opponents.append({'Fighter': fight_dict['Opponent'], 'Fighter_ID': opponent_id})
            return fighter_id, fighter_name, fight_data, new_opponents
        print(f"Failed to retrieve page for {fighter_name} (Status code: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"Request error for {fighter_name}: {e}")
    return fighter_id, fighter_name, [], []
df_fighter_id = pd.read_csv('./data/fighter_id_sherdog.csv')
all_new_opponents = []
def process_fighter(row, session):
    fighter_name = row['Fighter']
    fighter_id = row['Fighter_ID']
    fighter_file = f"./data/fighters/{fighter_name.replace(' ', '_')}_{fighter_id}.csv"
    if os.path.exists(fighter_file):
        print(f"Skipping {fighter_name} - file already exists")
        return fighter_id, fighter_name, [], []
    fighter_url = f"https://www.sherdog.com/fighter/{fighter_name.replace(' ', '-')}-{fighter_id}"
    return scrape_fighter_fights_sherdog(session, fighter_name, fighter_id, fighter_url)
total_fighters = len(df_fighter_id)
fighters_processed = 0
print(f"\nStarting to process {total_fighters} fighters")
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(process_fighter, row, session) for _, row in df_fighter_id.iterrows()]
    for future in as_completed(futures):
        fighter_id, fighter_name, fight_data, new_opponents = future.result()
        fighters_processed += 1
        print(f"Progress: {fighters_processed}/{total_fighters} fighters processed ({(fighters_processed/total_fighters)*100:.1f}%)")
        if fight_data:
            output_file = f"./data/fighters/{fighter_name.replace(' ', '_')}_{fighter_id}.csv"
            pd.DataFrame(fight_data).to_csv(output_file, index=False)
            print(f"Saved {len(fight_data)} fights for {fighter_name} to {output_file}")
            all_new_opponents.extend(new_opponents)
if all_new_opponents:
    print(f"\nFound {len(all_new_opponents)} new opponents")
    df_new_opponents = pd.DataFrame(all_new_opponents).drop_duplicates()
    df_fighter_id = pd.concat([df_fighter_id, df_new_opponents], ignore_index=True).drop_duplicates()
    df_fighter_id.to_csv('./data/fighter_id_sherdog.csv', index=False)
    print(f"Updated fighter_id_sherdog.csv with {len(df_new_opponents)} new unique opponents")
first_name = "Dustin"
last_name = "Poirier"
file_pattern = f'./data/fighters/*{first_name}*{last_name}*.csv'
matching_files = glob.glob(file_pattern)
if matching_files:
    first_file = matching_files[0]
    df = pd.read_csv(first_file)
    print(f"Total number of rows including the header in {first_file}: {len(df)}")
    print(f"Column names: {list(df.columns)}")
else:
    print("No files found matching the pattern.")
fighter_info_df = pd.read_csv('./data/fighter_info.csv')
event_data_df = pd.read_csv('./data/event_data_sherdog.csv')
print(f"Number of rows in fighter_info.csv: {len(fighter_info_df)}")
print(f"Number of rows in event_data_sherdog.csv: {len(event_data_df)}")
if os.path.exists("data/ufc_roster.csv"): os.remove("data/ufc_roster.csv")
ns = {
    "s": "http://www.sitemaps.org/schemas/sitemap/0.9",
    "xhtml": "http://www.w3.org/1999/xhtml"
}
all_fighters = []
page = 1
consecutive_empty_pages = 0
max_consecutive_empty = 100
while True:
    sitemap_url = f"https://www.ufc.com/sitemap.xml?page={page}"
    try:
        response = requests.get(sitemap_url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Page {page} does not exist. Stopping.")
        break
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {page}: {e}")
        page += 1
        continue
    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        print(f"Error parsing page {page}: {e}")
        if "not well-formed (invalid token)" in str(e):
            print("Reached end of valid pages. Stopping.")
            break
        page += 1
        continue
    fighter_urls = []
    for url_elem in root.findall("s:url", ns):
        loc_elem = url_elem.find("s:loc", ns)
        if loc_elem is not None:
            url_text = loc_elem.text
            if "/athlete/" in url_text:
                fighter_urls.append(url_text)
    print(f"https://www.ufc.com/sitemap.xml?page={page} -> {len(fighter_urls)} fighter URLs")
    if len(fighter_urls) == 0:
        consecutive_empty_pages += 1
        if consecutive_empty_pages >= max_consecutive_empty:
            print(f"Found {max_consecutive_empty} consecutive empty pages. Stopping.")
            break
    else:
        consecutive_empty_pages = 0
    for url in fighter_urls:
        try:
            slug = url.split("/athlete/")[1]
            name = slug.replace("-", " ").title()
        except IndexError:
            name = ""
        all_fighters.append({"name": name, "url": url})
    page += 1
print(f"Total fighter records found: {len(all_fighters)}")
csv_filename = "data/ufc_roster.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["name", "url"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for fighter in all_fighters:
        writer.writerow(fighter)
print(f"All fighter names and URLs saved to {csv_filename}")
df = pd.read_csv("data/ufc_roster.csv")
all_fighter_urls = df["url"].tolist()
print(f"Total fighter URLs loaded from CSV: {len(all_fighter_urls)}")
roster_csv = "data/ufc_roster.csv"
df = pd.read_csv(roster_csv)
print(f"Columns in {roster_csv}: {df.columns.tolist()}")
all_fighter_urls = df["url"].dropna().tolist()
print(f"Total fighter URLs loaded from CSV: {len(all_fighter_urls)}")
profile_csv = "data/ufc_fighter_profiles.csv"
if os.path.exists("data/ufc_fighter_profiles.csv"): os.remove("data/ufc_fighter_profiles.csv")
fieldnames = ["name", "nickname", "weight_class", "profile_url", "thumbnail"]
def scrape_fighter(url):
    """
    Scrapes a fighter page and returns the extracted data as a dictionary.
    Implements basic retry logic in case of temporary rate limiting or non-200 responses.
    """
    for attempt in range(1, 4):
        try:
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                name_tag = soup.find("h1", class_="hero-profile__name")
                name = name_tag.get_text(strip=True) if name_tag else "Unknown"
                nickname_tag = soup.find("p", class_="hero-profile__nickname")
                nickname = nickname_tag.get_text(strip=True) if nickname_tag else ""
                weight_class_tag = soup.find("p", class_="hero-profile__division-title")
                weight_class = weight_class_tag.get_text(strip=True) if weight_class_tag else ""
                thumbnail_tag = soup.find("img", class_="hero-profile__image")
                thumbnail = thumbnail_tag["src"] if thumbnail_tag and "src" in thumbnail_tag.attrs else ""
                fighter_data = {
                    "name": name,
                    "nickname": nickname,
                    "weight_class": weight_class,
                    "profile_url": url,
                    "thumbnail": thumbnail
                }
                return fighter_data
            elif resp.status_code == 429:
                print(f"Rate-limited. Waiting before retry... (Attempt {attempt} of 3)")
                time.sleep(60)
            else:
                print(f"Error fetching fighter page {url} (status {resp.status_code}), attempt {attempt} of 3.")
                time.sleep(20)
        except Exception as e:
            print(f"Exception occurred while scraping {url}: {e} (Attempt {attempt} of 3)")
            time.sleep(20)
    print(f"Failed to fetch fighter page after 3 retries: {url}")
    return None
results = []
max_workers = 10
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    future_to_url = {executor.submit(scrape_fighter, url): url for url in all_fighter_urls}
    for idx, future in enumerate(as_completed(future_to_url), start=1):
        data = future.result()
        if data:
            results.append(data)
        print(f"Processed {idx} of {len(all_fighter_urls)} fighter profiles")
        if idx % 100 == 0:
            with open(profile_csv, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                for fighter_data in results:
                    writer.writerow(fighter_data)
            results = []
            print(f"Saved {idx} fighter profiles to {profile_csv}")
            time.sleep(10)  
with open(profile_csv, "a", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    for fighter_data in results:
        writer.writerow(fighter_data)
print(f"All fighter profiles saved to {profile_csv}")
subprocess.run(['open', 'data/event_data_sherdog.csv'])
subprocess.run(['open', 'data/fighter_info.csv'])