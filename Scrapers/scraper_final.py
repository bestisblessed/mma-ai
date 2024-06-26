import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from tqdm.notebook import tqdm
import warnings
import re
import csv
import os
from datetime import datetime
import glob
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import sqlite3

get_ipython().system('rm -rf data-raw')

### Clear data-raw directory
directory_path = './data-raw/'
for root, dirs, files in os.walk(directory_path, topdown=False):
    for file in files:
        file_path = os.path.join(root, file)
        os.remove(file_path)
    for dir in dirs:
        dir_path = os.path.join(root, dir)
        os.rmdir(dir_path)

### Create directories and csv files
directories = ['./data-raw/fighters/', './data-raw/git/']
for directory in directories:
    if not os.path.exists(directory):
        os.makedirs(directory)
csv_files = ['./data-raw/event_urls_sherdog.csv', './data-raw/event_data_sherdog.csv', './data-raw/fighter_id_sherdog.csv', './data-raw/fighter_info.csv']
for file_path in csv_files:
    if not os.path.exists(file_path):
        open(file_path, 'a').close()

### Download github data
files = ["ufc_event_details.csv", "ufc_fight_results.csv", "ufc_fight_stats.csv", "ufc_fighter_tott.csv"]
base_url = "https://raw.githubusercontent.com/Greco1899/scrape_ufc_stats/main/"
directory = "./data-raw/git/"
os.makedirs(directory, exist_ok=True)
for file in files:
    response = requests.get(base_url + file)
    if response.status_code == 200:
        with open(os.path.join(directory, file), 'wb') as f:
            f.write(response.content)
    else:
        print(f"Failed to download {file}")

### event_urls_sherdog.csv
columns = ['Event_URL']
file_path = './data-raw/event_urls_sherdog.csv'
if os.path.isfile(file_path):
    if os.path.getsize(file_path) == 0:
        df = pd.DataFrame(columns=columns)
        df.to_csv(file_path, index=False)
else:
    df = pd.DataFrame(columns=columns)
    df.to_csv(file_path, index=False)

### figher_id_sherdog.csv
columns = ['Fighter', 'Fighter_ID']
file_path = './data-raw/fighter_id_sherdog.csv'
if os.path.isfile(file_path):
    if os.path.getsize(file_path) == 0:
        df = pd.DataFrame(columns=columns)
        df.to_csv(file_path, index=False)
else:
    df = pd.DataFrame(columns=columns)
    df.to_csv(file_path, index=False)

### event_data_sherdog.csv
columns = ['Event Name', 'Event Location', 'Event Date', 'Fighter 1', 'Fighter 2', 'Weight Class', 'Winning Fighter', 'Winning Method', 'Winning Round', 'Winning Time', 'Referee']
file_path = './data-raw/event_data_sherdog.csv'
if os.path.isfile(file_path):
    if os.path.getsize(file_path) == 0:
        df = pd.DataFrame(columns=columns)
        df.to_csv(file_path, index=False)
else:
    df = pd.DataFrame(columns=columns)
    df.to_csv(file_path, index=False)

### fighter_info.csv
columns = ['Fighter', 'Nickname', 'Birth Date', 'Nationality', 'Hometown', 'Association', 'Weight Class', 'Height', 'REACH', 'STANCE', 'Wins', 'Losses', 'Win_Decision', 'Win_KO', 'Win_Sub', 'Loss_Decision', 'Loss_KO', 'Loss_Sub', 'Sherdog URL', 'BFO URL']
file_path = './data-raw/fighter_info.csv'
if os.path.isfile(file_path):
    if os.path.getsize(file_path) == 0:
        df = pd.DataFrame(columns=columns)
        df.to_csv(file_path, index=False)
else:
    df = pd.DataFrame(columns=columns)
    df.to_csv(file_path, index=False)


# Get UFC event urls from sherdog
def scrape_event_urls_sherdog():
    file_path = './data-raw/event_urls_sherdog.csv'
    urls = [
        'https://www.sherdog.com/organizations/Ultimate-Fighting-Championship-UFC-2/recent-events/1',
        'https://www.sherdog.com/organizations/Ultimate-Fighting-Championship-UFC-2/recent-events/2',
        'https://www.sherdog.com/organizations/Ultimate-Fighting-Championship-UFC-2/recent-events/3',
        'https://www.sherdog.com/organizations/Ultimate-Fighting-Championship-UFC-2/recent-events/4',
        'https://www.sherdog.com/organizations/Ultimate-Fighting-Championship-UFC-2/recent-events/5',
        'https://www.sherdog.com/organizations/Ultimate-Fighting-Championship-UFC-2/recent-events/6',
        'https://www.sherdog.com/organizations/Ultimate-Fighting-Championship-UFC-2/recent-events/7'
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    if os.path.isfile(file_path):
        df = pd.read_csv(file_path)
    else:
        df = pd.DataFrame(columns=['Event_URL'])

    progress_bar = tqdm(urls, desc="Scraping URLs", unit="URL",
                        bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {postfix}]")

    for index, url in enumerate(progress_bar, start=1):
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        specific_div = soup.find('div', {'class': 'single_tab', 'id': 'recent_tab'})
        new_urls = []
        for a in specific_div.find_all('a', itemprop='url'):
            href = a.get('href')
            if href and href not in df['Event_URL'].values:
                new_urls.append(href)

        new_urls_df = pd.DataFrame(new_urls, columns=['Event_URL'])
        df = pd.concat([df, new_urls_df], ignore_index=True)

        progress_bar.set_postfix({"Total URLs": len(df), "Current URL": url})

    df.to_csv(file_path, index=False)
    print(df)
    
## Call the function
scrape_event_urls_sherdog()

# Broken URL's 
#/events/UFC-233-Ultimate-Fighting-Championship-233-72021
#/events/UFC-Fight-Night-97-Lamas-vs-Penn-90890
#/events/UFC-176-Aldo-vs-Mendes-2-37609
#/events/UFC-151-Jones-vs-Henderson-25809

urls_to_delete = [
    "/events/UFC-233-Ultimate-Fighting-Championship-233-72021",
    "/events/UFC-Fight-Night-97-Lamas-vs-Penn-90890",
    "/events/UFC-176-Aldo-vs-Mendes-2-37609",
    "/events/UFC-151-Jones-vs-Henderson-25809"
]

input_file = "./data-raw/event_urls_sherdog.csv"
output_file = "./data-raw/event_urls_sherdog.csv"

with open(input_file, "r") as csvfile:
    reader = csv.DictReader(csvfile)
    rows = [row for row in reader if row["Event_URL"] not in urls_to_delete]

fieldnames = ["Event_URL", "Event Date"]

with open(output_file, "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("URLs deleted successfully.")

warnings.filterwarnings("ignore", category=FutureWarning)

def fetch_event_date(session, url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    try:
        response = session.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        event_date_meta = soup.find('meta', itemprop='startDate')
        if event_date_meta and 'content' in event_date_meta.attrs:
            return event_date_meta['content'].strip()
        else:
            return 'Not Found'
    except Exception as e:
        print(f"An error occurred while processing URL {url}: {e}")
        return "Error"

def scrape_event_date():
    df = pd.read_csv('./data-raw/event_urls_sherdog.csv')
    df['Event_URL'] = 'https://sherdog.com' + df['Event_URL']

    event_dates = []

    with requests.Session() as session:
        with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
            # Map fetch_event_date function to URLs
            future_to_url = {executor.submit(fetch_event_date, session, url): url for url in df['Event_URL']}
            for future in tqdm(concurrent.futures.as_completed(future_to_url), total=len(df['Event_URL']), desc="Scraping Events", unit="Event"):
                url = future_to_url[future]
                try:
                    event_date = future.result()
                    event_dates.append(event_date)
                except Exception as e:
                    print(f"An error occurred while processing URL {url}: {e}")
                    event_dates.append("Error")

    # Add the 'Event Date' column and assign the event_dates list to it
    df['Event Date'] = event_dates

    # Save the modified DataFrame back to the CSV file
    df.to_csv('./data-raw/event_urls_sherdog.csv', index=False)

    print("Event dates appended successfully.")

# Call the function
scrape_event_date()


df = pd.read_csv('./data-raw/event_urls_sherdog.csv')
print(f"Total number of rows including the header in event_urls_sherdog.csv: {len(df)}")
print(f"Column names: {list(df.columns)}")

file_path = './data-raw/event_urls_sherdog.csv' # Replace your_file_name.csv with your actual file name
specified_line_to_remove = "/events/UFC-302-June-29-101243"

# Read the original file and exclude the line containing the specified text
with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Filter out the specified line
filtered_lines = [line for line in lines if specified_line_to_remove not in line]

# Write the filtered lines back to the same file or a new file as needed
with open(file_path, 'w', encoding='utf-8') as file:  # Replace file_path if you want to write to a new file
    for line in filtered_lines:
        file.write(line)

print("Specified line has been removed.")


get_ipython().system('rm ./data-raw/event_data_sherdog.csv')

# Final Loop 

warnings.filterwarnings("ignore", category=FutureWarning)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

urls_df = pd.read_csv('data-raw/event_urls_sherdog.csv')
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

                # Main Event
                main_event_fighters = soup.find_all('div', class_='fighter')
                if main_event_fighters:
                    fighter1 = main_event_fighters[0].find('span', itemprop='name').text.strip()
                    fighter2 = main_event_fighters[1].find('span', itemprop='name').text.strip()
                    fighter1_id = main_event_fighters[0].find('a', itemprop='url')['href'].split('-')[-1]
                    fighter2_id = main_event_fighters[1].find('a', itemprop='url')['href'].split('-')[-1]
                    weight_class = soup.find('span', class_='weight_class').text.strip()
                    winning_fighter = fighter1  # Assuming fighter1 as the winner, adjust as necessary
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
                    
                # Other Bouts
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
                            'Winning Fighter': fighter1,  # Adjust as necessary
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

file_path = './data-raw/event_data_sherdog.csv'
write_mode = 'a' if os.path.isfile(file_path) else 'w'

df.to_csv(file_path, mode=write_mode, header=not os.path.isfile(file_path), index=False)


df = pd.read_csv('./data-raw/event_data_sherdog.csv')
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
df.to_csv('./data-raw/event_data_sherdog.csv', index=False)


df = pd.read_csv('./data-raw/event_data_sherdog.csv')
print(f"Total number of rows including the header in event_data_sherdog.csv: {len(df)}")
print(f"Column names: {list(df.columns)}")



### Append sherdog fighter IDs to fighter_id_sherdog.csv
df = pd.read_csv('./data-raw/event_data_sherdog.csv')
df2 = pd.read_csv('./data-raw/fighter_id_sherdog.csv')

# Iterate over each row in df
for index, row in df.iterrows():
    fighter1 = row['Fighter 1']
    fighter2 = row['Fighter 2']
    fighter1_id = row['Fighter 1 ID']
    fighter2_id = row['Fighter 2 ID']
    for fighter, fighter_id in zip([fighter1, fighter2], [fighter1_id, fighter2_id]):
        if fighter not in df2['Fighter'].values and fighter_id not in df2['Fighter_ID'].values:
            df2 = pd.concat([df2, pd.DataFrame([{'Fighter': fighter, 'Fighter_ID': fighter_id}])])  # adjusted line

# Save the DataFrame
df2.to_csv('./data-raw/fighter_id_sherdog.csv', index=False)


### Function to remove nicknames
def remove_nickname(name):
    return re.sub(r" '.+?'", "", name)

## Remove them
df = pd.read_csv('./data-raw/fighter_id_sherdog.csv')
df['Fighter'] = df['Fighter'].apply(remove_nickname) # Apply the function to the 'Fighter' column
df.to_csv('./data-raw/fighter_id_sherdog.csv', index=False)

df = pd.read_csv('./data-raw/event_data_sherdog.csv')
df['Fighter 1'] = df['Fighter 1'].apply(remove_nickname)
df.to_csv('./data-raw/event_data_sherdog.csv', index=False)

df = pd.read_csv('./data-raw/event_data_sherdog.csv')
df['Fighter 2'] = df['Fighter 2'].apply(remove_nickname)
df.to_csv('./data-raw/event_data_sherdog.csv', index=False)

df = pd.read_csv('./data-raw/event_data_sherdog.csv')
df['Winning Fighter'] = df['Winning Fighter'].apply(remove_nickname)
df.to_csv('./data-raw/event_data_sherdog.csv', index=False)


### Add 'UFC' indicator to current fighters in fighter_id_sherdog.csv.csv
# Read the CSV file into a DataFrame
input_file_path = './data-raw/fighter_id_sherdog.csv'
output_file_path = './data-raw/fighter_id_sherdog.csv'
df = pd.read_csv(input_file_path)

# Add the new column 'UFC' with the value 'y'
df['UFC'] = 'y'

# Write the modified DataFrame back to a CSV file
df.to_csv(output_file_path, index=False)

print("New column 'UFC' added to the CSV file.")


df = pd.read_csv('./data-raw/fighter_id_sherdog.csv')
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
df.to_csv('./data-raw/fighter_id_sherdog.csv', index=False)


df = pd.read_csv('./data-raw/fighter_id_sherdog.csv')
print(f"Total number of rows including the header in fighter_id_sherdog.csv: {len(df)}")
print(f"Column names: {list(df.columns)}")


# # Fighter General Info

# W/ concurrent.futures ^

import warnings
import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import tqdm

def scrape_fighter_general_info_sherdog(fighter, fighter_id):
    url = f'https://www.sherdog.com/fighter/{fighter_id}'
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
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
    df_fighter_id = pd.read_csv('./data-raw/fighter_id_sherdog.csv')
    fighter_data_list = []
    with ThreadPoolExecutor(max_workers=30) as executor:
        future_to_fighter = {executor.submit(scrape_fighter_general_info_sherdog, row['Fighter'], row['Fighter_ID']): row for index, row in df_fighter_id.iterrows()}
        for future in tqdm.tqdm(as_completed(future_to_fighter), total=len(future_to_fighter)):
            fighter_data = future.result()
            if fighter_data:
                fighter_data_list.append(fighter_data)
    new_df = pd.DataFrame(fighter_data_list)
    new_df.to_csv('./data-raw/fighter_info.csv', index=False)

scrape_fighters_concurrently()


df = pd.read_csv('./data-raw/fighter_info.csv')
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
df.to_csv('./data-raw/fighter_info.csv', index=False)


df = pd.read_csv('./data-raw/fighter_info.csv')
print(f"Total number of rows including the header in fighter_info.csv: {len(df)}")
print(f"Column names: {list(df.columns)}")

get_ipython().system('rm -rf ./data-raw/fighters/')

directory_path = './data-raw/fighters/'
if not os.path.exists(directory_path):
    os.makedirs(directory_path)


from concurrent.futures import ThreadPoolExecutor, as_completed

def scrape_fighter_fights_sherdog(fighter_name, fighter_id, fighter_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(fighter_url, headers=headers, timeout=60)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'class': 'new_table fighter'})
        rows = table.find_all('tr')[1:]
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
    return fighter_id, fighter_name, [], []

df_fighter_id = pd.read_csv('./data-raw/fighter_id_sherdog.csv')
all_new_opponents = []

def process_fighter(row):
    fighter_url = f"https://www.sherdog.com/fighter/{row['Fighter'].replace(' ', '-')}-{row['Fighter_ID']}"
    return scrape_fighter_fights_sherdog(row['Fighter'], row['Fighter_ID'], fighter_url)

total_fighters = len(df_fighter_id)
fighters_processed = 0

with ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(process_fighter, row) for _, row in df_fighter_id.iterrows()]
    for future in as_completed(futures):
        fighter_id, fighter_name, fight_data, new_opponents = future.result()
        fighters_processed += 1
        print(f"Processed {fighters_processed}/{total_fighters} fighters.")
        if fight_data:
            pd.DataFrame(fight_data).to_csv(f"./data-raw/fighters/{fighter_name.replace(' ', '_')}_{fighter_id}.csv", index=False)
            all_new_opponents.extend(new_opponents)

if all_new_opponents:
    df_new_opponents = pd.DataFrame(all_new_opponents).drop_duplicates()
    df_fighter_id = pd.concat([df_fighter_id, df_new_opponents], ignore_index=True).drop_duplicates()
    df_fighter_id.to_csv('./data-raw/fighter_id_sherdog.csv', index=False)

directory_path = './data-raw/fighters/'

for filename in os.listdir(directory_path):
    if filename.endswith('.csv'):  # Check if the file is a CSV
        file_path = os.path.join(directory_path, filename)
        df = pd.read_csv(file_path)
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
        df.to_csv(file_path, index=False)

first_name = "Dustin"
last_name = "Poirier"

# Adjust the pattern to match files containing both the first name and the last name
file_pattern = f'./data-raw/fighters/*{first_name}*{last_name}*.csv'

# Use glob to find files that match the updated pattern
matching_files = glob.glob(file_pattern)

if matching_files:
    first_file = matching_files[0]
    df = pd.read_csv(first_file)
    
    print(f"Total number of rows including the header in {first_file}: {len(df)}")
    print(f"Column names: {list(df.columns)}")
else:
    print("No files found matching the pattern.")


fighter_info_df = pd.read_csv('./data-raw/fighter_info.csv')
print(f"Number of rows in fighter_info.csv: {len(fighter_info_df)}")



fighter_info_df = pd.read_csv('./data-raw/fighter_info.csv')
print(f"Number of rows in fighter_info.csv: {len(fighter_info_df)}")


# Removing women's fights and fighters

womens_weight_classes = ['Strawweight'] # 'Flyweight', 'Bantamweight', 'Featherweight'
fighter_info_df = pd.read_csv('./data-raw/fighter_info.csv')
cleaned_fighter_info_df = fighter_info_df[~fighter_info_df['Weight Class'].isin(womens_weight_classes)]
cleaned_fighter_info_df.to_csv('./data-raw/fighter_info.csv', index=False)
print(f"Cleaned dataset saved to {'./data-raw/fighter_info.csv'}")


fighter_info_df = pd.read_csv('./data-raw/fighter_info.csv')
print(f"Number of rows in fighter_info.csv: {len(fighter_info_df)}")


# DB STUFF WITH GIT DATA
get_ipython().system('rm -rf ./data/github')
os.makedirs('./data/github/', exist_ok=True)
os.makedirs('./data/github/fighter-details', exist_ok=True)
urls = [
    'https://raw.githubusercontent.com/Greco1899/scrape_ufc_stats/main/ufc_event_details.csv',
    'https://raw.githubusercontent.com/Greco1899/scrape_ufc_stats/main/ufc_fight_details.csv',
    'https://raw.githubusercontent.com/Greco1899/scrape_ufc_stats/main/ufc_fight_results.csv',
    'https://raw.githubusercontent.com/Greco1899/scrape_ufc_stats/main/ufc_fight_stats.csv',
    'https://raw.githubusercontent.com/Greco1899/scrape_ufc_stats/main/ufc_fighter_details.csv',
    'https://raw.githubusercontent.com/Greco1899/scrape_ufc_stats/main/ufc_fighter_tott.csv'
]
for url in urls:
    df = pd.read_csv(url)
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    df.to_csv('./data/github/' + url.split('/')[-1], index=False)
    
# Merge the DATE and LOCATION of every fight
event_details_df = pd.read_csv('./data/github/ufc_event_details.csv')
fight_results_df = pd.read_csv('./data/github/ufc_fight_results.csv')

# Set the 'EVENT' column as index in the event details DataFrame for easier merging
event_details_df_for_merge = event_details_df.set_index('EVENT')

# Merge 'DATE' and 'LOCATION' from event details into fight results DataFrame based on 'EVENT'
merged_df = fight_results_df.join(event_details_df_for_merge[['DATE', 'LOCATION']], on='EVENT')

merged_df.to_csv('./data/github/master.csv', index=False)


# Create FIGHTER1, FIGHTER2, and WINNING_FIGHTER columns

fight_results_df = pd.read_csv('./data/github/master.csv')

# Split the 'BOUT' column into two new columns 'Fighter1' and 'Fighter2'
fight_results_df[['FIGHTER1', 'FIGHTER2']] = fight_results_df['BOUT'].str.split(' vs. ', expand=True)

# Use a multiline lambda within apply for readability without an external function
fight_results_df['WINNING_FIGHTER'] = fight_results_df.apply(
    lambda row: row['FIGHTER1'].strip() if row['OUTCOME'] == 'W/L' else
                (row['FIGHTER2'].strip() if row['OUTCOME'] == 'L/W' else
                 ('No Contest' if row['OUTCOME'] == 'NC/NC' else
                  ('Draw' if row['OUTCOME'] == 'D/D' else 'Unknown Outcome'))),
    axis=1
)

fight_results_df.to_csv('./data/github/master.csv', index=False)

# Load the latest master.csv file into a DataFrame
latest_master_df = pd.read_csv('./data/github/master.csv')

# Clean leading and trailing whitespace in FIGHTER1 and FIGHTER2 columns
latest_master_df['FIGHTER1'] = latest_master_df['FIGHTER1'].str.strip()
latest_master_df['FIGHTER2'] = latest_master_df['FIGHTER2'].str.strip()

# Create an SQLite database connection in a writable location
conn = sqlite3.connect('ufc_database.db')
cursor = conn.cursor()

# Create the fight_results table
create_table_query = """
CREATE TABLE IF NOT EXISTS fight_results (
    EVENT TEXT,
    BOUT TEXT,
    OUTCOME TEXT,
    WEIGHTCLASS TEXT,
    METHOD TEXT,
    ROUND INTEGER,
    TIME TEXT,
    TIME_FORMAT TEXT,
    REFEREE TEXT,
    DETAILS TEXT,
    URL TEXT,
    DATE TEXT,
    LOCATION TEXT,
    FIGHTER1 TEXT,
    FIGHTER2 TEXT,
    WINNING_FIGHTER TEXT
)
"""
cursor.execute(create_table_query)
conn.commit()

# Insert data into the fight_results table
latest_master_df.to_sql('fight_results', conn, if_exists='replace', index=False)

# Verify the data insertion
result = cursor.execute("SELECT COUNT(*) FROM fight_results").fetchone()[0]

# Close the connection
conn.close()

result



### END GIT DATA ###

# Remove white spaces and special characters

import re
import pandas as pd

# Load the datasets
master_df = pd.read_csv('./data/github/master.csv')
fighter_info_df = pd.read_csv('./data-raw/fighter_info.csv')

# Remove leading/trailing whitespace, special characters, and normalize to lowercase
fighter_info_df['Fighter'] = fighter_info_df['Fighter'].str.strip().str.lower().str.replace(r'[^\w\s]', '', regex=True)
master_df['FIGHTER1'] = master_df['FIGHTER1'].str.strip().str.lower().str.replace(r'[^\w\s]', '', regex=True)
master_df['FIGHTER2'] = master_df['FIGHTER2'].str.strip().str.lower().str.replace(r'[^\w\s]', '', regex=True)

# Save the cleaned datasets back to their original files
master_df.to_csv('./data/github/master.csv', index=False)
fighter_info_df.to_csv('./data-raw/fighter_info.csv', index=False)

print("Whitespace and special characters removed, and cleaned datasets saved.")

# Cleaning more women's names from git data

master_df = pd.read_csv('./data/github/master.csv')
fighter_info_df = pd.read_csv('./data-raw/fighter_info.csv')

womens_fights_master = master_df[master_df['WEIGHTCLASS'].str.contains('Women', case=False, na=False)]
female_fighters = set(womens_fights_master['FIGHTER1']).union(set(womens_fights_master['FIGHTER2']))
cleaned_fighter_info_df = fighter_info_df[~fighter_info_df['Fighter'].isin(female_fighters)]
cleaned_fighter_info_df.to_csv('./data-raw/fighter_info.csv', index=False)

print(f"Cleaned dataset saved to ./data-raw/fighter_info.csv")


fighter_info_df = pd.read_csv('./data-raw/fighter_info.csv')
print(f"Number of rows in fighter_info.csv: {len(fighter_info_df)}")

# Remove womens fight rows from master.csv (CANT DO BEFORE USING THEM FOR FIGHTER_INFO.CSV)

import pandas as pd

# Load the master dataset
master_df = pd.read_csv('./data/github/master.csv')

# Print the number of rows before removing women's fights
print(f"Number of rows before: {len(master_df)}")

# Filter out rows corresponding to women's fights
cleaned_master_df = master_df[~master_df['WEIGHTCLASS'].str.contains('Women', case=False, na=False)]

# Print the number of rows before removing women's fights
print(f"Number of rows before: {len(cleaned_master_df)}")

# Save the cleaned dataset back to the original file
cleaned_master_df.to_csv('./data/github/master.csv', index=False)

print("Women's fights removed, and cleaned master.csv saved.")

# Remove fights from before 2015 in master.csv

import pandas as pd

# Load the master dataset
master_df = pd.read_csv('./data/github/master.csv')

# Convert the DATE column to datetime
master_df['DATE'] = pd.to_datetime(master_df['DATE'], errors='coerce')

# Filter out rows with events before 2010
cleaned_master_df = master_df[master_df['DATE'] >= '2005-01-01']

# Save the cleaned dataset back to the original file
cleaned_master_df.to_csv('./data/github/master.csv', index=False)

print("Rows with events before 2010 removed, and cleaned master.csv saved.")

# Remove all TUF rows from master.csv

import pandas as pd

# Load the dataset
master_df = pd.read_csv('./data/github/master.csv')

# Print the number of rows before removing women's fights
print(f"Number of rows before: {len(master_df)}")

# Remove rows where the EVENT column contains 'Ultimate Fighter' or 'TUF'
filtered_df = master_df[~master_df['WEIGHTCLASS'].str.contains('Ultimate Fighter|TUF', case=False, na=False)]

# Print the number of rows before removing women's fights
print(f"Number of rows before: {len(filtered_df)}")

# Save the filtered DataFrame to a new CSV file
filtered_df.to_csv('./data/github/master.csv', index=False)

