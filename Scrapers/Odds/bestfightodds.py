# Get all fighter urls from bestfightodds to fighter_urls_bfo.csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import pandas as pd
from tqdm import tqdm
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

# Define a function to get a new WebDriver instance
def create_driver():
    return webdriver.Chrome(options=chrome_options)

# Define a function to get fighter URL
def get_fighter_url(fighter):
    driver = create_driver()
    driver.implicitly_wait(5)  # Implicit wait for elements to be found
    try:
        # Fighter path in a href has dashes in place of spaces and dots
        path_fighter = fighter.replace(' ', '-').replace('.', '-').lower()

        # URL to search for the fighter
        url = 'https://www.bestfightodds.com/search?query=' + path_fighter

        # Navigate to the URL
        driver.get(url)

        # Find the first result link
        try:
            first_link = driver.find_element(By.XPATH, '//table/tbody/tr[1]/td[2]/a')
            first_path = first_link.get_attribute('href')
            print(fighter, first_path)
            return (fighter, first_path)
        except NoSuchElementException:
            return (fighter, None)
    
    except WebDriverException as e:
        print(f"WebDriver error occurred: {e}")
        return (fighter, None)
    
    finally:
        driver.quit()

# Read fighters from CSV file
df = pd.read_csv('./data/fighter_info.csv')

# File path for the new CSV file
output_csv_path = './data/fighter_urls_bfo.csv'

# Ensure the CSV file is created with headers if it does not exist
if not os.path.isfile(output_csv_path):
    pd.DataFrame(columns=['Fighter', 'BFO URL']).to_csv(output_csv_path, index=False)

# Load existing URLs to avoid redundant work
existing_urls = pd.read_csv(output_csv_path).set_index('Fighter')['BFO URL'].to_dict()

# Batch size and sleep time between batches
batch_size = 20
sleep_time = 3  # 1 minute sleep time between batches

def process_batch(start_index, end_index):
    with ThreadPoolExecutor(max_workers=10) as executor:  # Increase the number of workers
        futures = []
        for i in range(start_index, end_index):
            fighter = df.loc[i, 'Fighter']
            if fighter not in existing_urls or pd.isna(existing_urls[fighter]) or existing_urls[fighter].strip() == '':
                futures.append(executor.submit(get_fighter_url, fighter))
        for future in as_completed(futures):
            fighter, url = future.result()
            if url:
                # Append URL to the CSV file
                # with open(output_csv_path, 'a') as f:
                #     f.write(f"{fighter},{url}\n")
                with open(output_csv_path, 'a') as f:
                    f.write(f"{fighter},{url if url else ''}\n")
                # Update the existing URLs dictionary
                existing_urls[fighter] = url

# Process in batches
num_fighters = len(df)
for i in tqdm(range(0, num_fighters, batch_size)):
    end_index = min(i + batch_size, num_fighters)
    process_batch(i, end_index)
    if end_index < num_fighters:
        print(f"Sleeping for {sleep_time} seconds before next batch...")
        time.sleep(sleep_time)  # Sleep between batches

# Close the WebDriver
driver.quit()

# Now try just the first name search for those that didn't work before 

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import os

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

# Define a function to get a new WebDriver instance
def create_driver():
    return webdriver.Chrome(options=chrome_options)

# Define a function to get fighter URL by first name
def get_fighter_url_by_first_name(fighter):
    driver = create_driver()
    driver.implicitly_wait(3)  # Implicit wait for elements to be found
    try:
        # Use only the first name
        first_name = fighter.split()[0].replace(' ', '-').replace('.', '-').lower()

        # URL to search for the fighter
        url = 'https://www.bestfightodds.com/search?query=' + first_name

        # Navigate to the URL
        driver.get(url)

        # Find the first result link
        try:
            first_link = driver.find_element(By.XPATH, '//table/tbody/tr[1]/td[2]/a')
            first_path = first_link.get_attribute('href')
            print(f"URL found for {fighter}: {first_path}")
            return (fighter, first_path)
        except NoSuchElementException:
            print(f"No URL found for {fighter} using first name search.")
            return (fighter, None)

    except WebDriverException as e:
        print(f"WebDriver error occurred for {fighter}: {e}")
        return (fighter, None)

    finally:
        driver.quit()

# Read the existing file with fighter URLs
df_urls = pd.read_csv('./data/fighter_urls_bfo.csv')

# Find fighters with NaN (missing) URLs
fighters_without_urls = df_urls[df_urls['BFO URL'].isnull()]['Fighter'].tolist()

if fighters_without_urls:
    print("Retrying fighters with only first names...")

    for fighter in fighters_without_urls:
        fighter, url = get_fighter_url_by_first_name(fighter)
        if url:
            # Update the URL in the DataFrame
            df_urls.loc[df_urls['Fighter'] == fighter, 'BFO URL'] = url

    # Save the updated URLs back to the CSV file
    df_urls.to_csv('./data/fighter_urls_bfo.csv', index=False)

    print("Updated fighter URLs saved to ./data/fighter_urls_bfo.csv.")
else:
    print("No fighters with empty URLs found.")

# Try getting the rest from direct url destination
# Just first name

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import os

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

# Define a function to get a new WebDriver instance
def create_driver():
    return webdriver.Chrome(options=chrome_options)

# Define a function to get fighter URL by first name
def get_fighter_url_by_first_name(fighter):
    driver = create_driver()
    driver.implicitly_wait(3)  # Implicit wait for elements to be found
    try:
        # Use only the first name
        first_name = fighter.split()[0].replace(' ', '-').replace('.', '-').lower()

        # URL to search for the fighter
        url = 'https://www.bestfightodds.com/search?query=' + first_name

        # Navigate to the URL
        driver.get(url)

        # Check if we were redirected directly to the fighter's page
        if driver.current_url != url:
            # We were redirected, capture the URL
            print(f"Redirected to {driver.current_url} for {fighter}")
            return (fighter, driver.current_url)

        # If not redirected, find the first result link
        try:
            first_link = driver.find_element(By.XPATH, '//table/tbody/tr[1]/td[2]/a')
            first_path = first_link.get_attribute('href')
            print(f"URL found for {fighter}: {first_path}")
            return (fighter, first_path)
        except NoSuchElementException:
            print(f"No URL found for {fighter} using first name search.")
            return (fighter, None)

    except WebDriverException as e:
        print(f"WebDriver error occurred for {fighter}: {e}")
        return (fighter, None)

    finally:
        driver.quit()

# Read the existing file with fighter URLs
df_urls = pd.read_csv('./data/fighter_urls_bfo.csv')

# Find fighters with NaN (missing) URLs
fighters_without_urls = df_urls[df_urls['BFO URL'].isnull()]['Fighter'].tolist()

if fighters_without_urls:
    print("Retrying fighters with only first names...")

    for fighter in fighters_without_urls:
        fighter, url = get_fighter_url_by_first_name(fighter)
        if url:
            # Update the URL in the DataFrame
            df_urls.loc[df_urls['Fighter'] == fighter, 'BFO URL'] = url

    # Save the updated URLs back to the CSV file
    df_urls.to_csv('./data/fighter_urls_bfo.csv', index=False)

    print("Updated fighter URLs saved to ./data/fighter_urls_bfo.csv.")
else:
    print("No fighters with empty URLs found.")


# Try getting the rest from direct url destination
# Full name 

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import os

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

# Define a function to get a new WebDriver instance
def create_driver():
    return webdriver.Chrome(options=chrome_options)

# Define a function to get fighter URL by full name
def get_fighter_url_by_full_name(fighter):
    driver = create_driver()
    driver.implicitly_wait(5)  # Implicit wait for elements to be found
    try:
        # Use the full name
        full_name = fighter.replace(' ', '-').replace('.', '-').lower()

        # URL to search for the fighter
        url = 'https://www.bestfightodds.com/search?query=' + full_name

        # Navigate to the URL
        driver.get(url)

        # Check if we were redirected directly to the fighter's page
        if driver.current_url != url:
            # We were redirected, capture the URL
            print(f"Redirected to {driver.current_url} for {fighter}")
            return (fighter, driver.current_url)

        # If not redirected, find the first result link
        try:
            first_link = driver.find_element(By.XPATH, '//table/tbody/tr[1]/td[2]/a')
            first_path = first_link.get_attribute('href')
            print(f"URL found for {fighter}: {first_path}")
            return (fighter, first_path)
        except NoSuchElementException:
            print(f"No URL found for {fighter} using full name search.")
            return (fighter, None)

    except WebDriverException as e:
        print(f"WebDriver error occurred for {fighter}: {e}")
        return (fighter, None)

    finally:
        driver.quit()

# Read the existing file with fighter URLs
df_urls = pd.read_csv('./data/fighter_urls_bfo.csv')

# Find fighters with NaN (missing) URLs
fighters_without_urls = df_urls[df_urls['BFO URL'].isnull()]['Fighter'].tolist()

if fighters_without_urls:
    print("Retrying fighters with full names...")

    for fighter in fighters_without_urls:
        fighter, url = get_fighter_url_by_full_name(fighter)
        if url:
            # Update the URL in the DataFrame
            df_urls.loc[df_urls['Fighter'] == fighter, 'BFO URL'] = url

    # Save the updated URLs back to the CSV file
    df_urls.to_csv('./data/fighter_urls_bfo.csv', index=False)

    print("Updated fighter URLs saved to ./data/fighter_urls_bfo.csv.")
else:
    print("No fighters with empty URLs found.")


# Hardcode and clean the remaining few

df_urls = pd.read_csv('./data/fighter_urls_bfo.csv')

# Hard code the URL for Abdulkareem Alselwady
df_urls.loc[df_urls['Fighter'] == 'abdulkareem alselwady', 'BFO URL'] = 'https://www.bestfightodds.com/fighters/Abdul-Kareem-Al-Selwady-10295'

# List of fighters to delete
fighters_to_delete = [
    "jinnosuke kashimura",
    "dokonjonosuke mishima",
    "keigo kunihara",
    "romie aram",
    "genki sudo",
    "masutatsu yano"
]

# Remove these fighters from the DataFrame
df_urls = df_urls[~df_urls['Fighter'].isin(fighters_to_delete)]

# Save the updated DataFrame back to the CSV file
df_urls.to_csv('./data/fighter_urls_bfo.csv', index=False)

print("Updated fighter URLs saved.")
