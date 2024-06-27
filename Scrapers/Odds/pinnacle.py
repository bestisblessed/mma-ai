from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import csv

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

driver = webdriver.Chrome(options=chrome_options)

driver.get("https://www.pinnacle.com/en/mixed-martial-arts/matchups/")

driver.implicitly_wait(5)

with open("./data/pinnacle.html", "w", encoding="utf-8") as file:
    file.write(driver.page_source)

driver.quit()

# Load your HTML document
with open("./data/pinnacle.html", "r", encoding="utf-8") as file:
    html_content = file.read()

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Find elements containing fighter names
# This is an example; you'll need to replace 'div.matchup' with the actual path to the elements containing fighter names in your HTML
matchups = soup.select('div.matchup')

fighter_data = []
for match in matchups:
    fighters = match.find_all('div', class_='fighter-name')  # Adjust 'div.fighter-name' based on your HTML structure
    if fighters:
        fighter_names = [fighter.get_text().strip() for fighter in fighters]
        fighter_data.append(fighter_names)  # Add this line to populate the fighter_data list
        print(" vs ".join(fighter_names))

# Save the fighter names to a CSV file
csv_file_path = "./data/pinnacle.csv"
with open(csv_file_path, "w", newline="", encoding="utf-8") as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["Fighter 1", "Fighter 2"])  # Write header
    for matchup in fighter_data:
        if len(matchup) == 2:  # Ensure there are exactly two fighters
            csvwriter.writerow(matchup)

print(f"Data saved to {csv_file_path}")