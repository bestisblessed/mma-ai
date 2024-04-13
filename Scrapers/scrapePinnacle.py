from bs4 import BeautifulSoup

# Load your HTML document
with open("./data/raw.html", "r", encoding="utf-8") as file:
    html_content = file.read()

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Find elements containing fighter names
# This is an example; you'll need to replace 'div.matchup' with the actual path to the elements containing fighter names in your HTML
matchups = soup.select('div.matchup')

for match in matchups:
    fighters = match.find_all('div', class_='fighter-name')  # Adjust 'div.fighter-name' based on your HTML structure
    if fighters:
        fighter_names = [fighter.get_text().strip() for fighter in fighters]
        print(" vs ".join(fighter_names))

