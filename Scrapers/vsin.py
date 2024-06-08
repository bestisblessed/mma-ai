from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import csv

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

driver = webdriver.Chrome(options=chrome_options)

driver.get("https://data.vsin.com/vegas-odds-linetracker/?sportid=ufc&linetype=moneyline")

driver.implicitly_wait(5)

with open("./data/vsin.html", "w", encoding="utf-8") as file:
    file.write(driver.page_source)

driver.quit()

# Load the HTML from the file
# with open('./data/rawVSiN.html', 'r') as file:
#     html_content = file.read()
with open('./data/vsin.html', 'r') as file:
    html_content = file.read()

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Find the table by the div class name and then the table within it
table_div = soup.find('div', {'class': 'table-responsive'})
table = table_div.find('table')

# Get the headers
# headers = [header.get_text(strip=True) for header in table.find_all('th')]
headers = ['Time', 'Fighters', 'DK Open', 'DK', 'Circa', 'South Point', 'GLD Nugget', 'Westgate', 'Wynn', 'Stations', 'Caesars', 'Mirage']

# Write to CSV
csv_file = "./data/vsin.csv"
with open(csv_file, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(headers)  # write headers

    # Write data rows
    for row in table.find_all('tr')[1:]:  # skipping the header row
        csvwriter.writerow([td.get_text(strip=True) for td in row.find_all('td')])

# Return the path to the CSV file created
csv_file
