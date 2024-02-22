from bs4 import BeautifulSoup
import csv

# Load the HTML from the file
# with open('./data/rawVSiN.html', 'r') as file:
#     html_content = file.read()
with open('./data/odds_VSiN.html', 'r') as file:
    html_content = file.read()

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Find the table by the div class name and then the table within it
table_div = soup.find('div', {'class': 'table-responsive'})
table = table_div.find('table')

# Get the headers
headers = [header.get_text(strip=True) for header in table.find_all('th')]

# Write to CSV
csv_file = "./data/odds_VSiN.csv"
with open(csv_file, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(headers)  # write headers

    # Write data rows
    for row in table.find_all('tr')[1:]:  # skipping the header row
        csvwriter.writerow([td.get_text(strip=True) for td in row.find_all('td')])

# Return the path to the CSV file created
csv_file
