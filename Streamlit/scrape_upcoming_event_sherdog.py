import warnings
import requests
import pandas as pd
import os
from bs4 import BeautifulSoup

# Delete the file if it exists
if os.path.exists("data/upcoming_event_data_sherdog.csv"):
    os.remove("data/upcoming_event_data_sherdog.csv")

def add_spaces_to_name(name):
    """Add spaces before capital letters that aren't at the start of the name."""
    if not name or len(name) <= 1:
        return name
    
    result = name[0]  # Start with first character
    for char in name[1:]:
        if char.isupper():
            result += ' ' + char
        else:
            result += char
    return result

def scrape_single_event(event_url):
    warnings.filterwarnings("ignore", category=FutureWarning)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    # Ensure URL is complete
    full_url = f'https://sherdog.com{event_url}' if not event_url.startswith('http') else event_url
    
    print(f"Scraping data from {full_url}")
    all_data = []
    
    try:
        response = requests.get(full_url, headers=headers)
        if response.status_code == 200:
            # Save HTML to file for debugging if needed
            with open("sherdog_event_page.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("HTML saved to sherdog_event_page.html for debugging")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            event_name = soup.find('span', itemprop='name').text.strip() if soup.find('span', itemprop='name') else "Unknown Event"
            event_location = soup.find('span', itemprop='location').text.strip() if soup.find('span', itemprop='location') else "Unknown Location"
            event_date = soup.find('meta', itemprop='startDate')['content'].strip() if soup.find('meta', itemprop='startDate') else "Unknown Date"
            
            # Get event date to determine if it's upcoming
            is_upcoming = True  # Assume it's upcoming by default for safety
            
            # Extract main event data
            main_event_fighters = soup.find_all('div', class_='fighter')
            if len(main_event_fighters) >= 2:
                fighter1 = main_event_fighters[0].find('span', itemprop='name').text.strip() if main_event_fighters[0].find('span', itemprop='name') else "Unknown Fighter"
                fighter2 = main_event_fighters[1].find('span', itemprop='name').text.strip() if main_event_fighters[1].find('span', itemprop='name') else "Unknown Fighter"
                
                fighter1_id = "Unknown"
                fighter2_id = "Unknown"
                
                if main_event_fighters[0].find('a', itemprop='url'):
                    fighter1_id = main_event_fighters[0].find('a', itemprop='url')['href'].split('-')[-1]
                
                if main_event_fighters[1].find('a', itemprop='url'):
                    fighter2_id = main_event_fighters[1].find('a', itemprop='url')['href'].split('-')[-1]
                
                weight_class_elem = soup.find('span', class_='weight_class')
                weight_class = weight_class_elem.text.strip() if weight_class_elem else "Unknown"
                
                # For upcoming events, these values won't exist, so set defaults
                winning_method = "N/A" if is_upcoming else "Unknown"
                winning_round = "N/A" if is_upcoming else "Unknown"
                winning_time = "N/A" if is_upcoming else "Unknown"
                referee = "N/A" if is_upcoming else "Unknown"
                
                # Only try to get these values if the event has happened
                if not is_upcoming:
                    method_elem = soup.find('em', string='Method')
                    if method_elem and method_elem.parent:
                        winning_method = method_elem.parent.contents[2].strip() if len(method_elem.parent.contents) > 2 else "Unknown"
                    
                    round_elem = soup.find('em', string='Round')
                    if round_elem and round_elem.parent:
                        winning_round = round_elem.parent.contents[2].strip() if len(round_elem.parent.contents) > 2 else "Unknown"
                    
                    time_elem = soup.find('em', string='Time')
                    if time_elem and time_elem.parent:
                        winning_time = time_elem.parent.contents[2].strip() if len(time_elem.parent.contents) > 2 else "Unknown"
                    
                    ref_elem = soup.find('em', string='Referee')
                    if ref_elem and ref_elem.parent and ref_elem.parent.find('a'):
                        referee = ref_elem.parent.find('a').text.strip()
                
                all_data.append({
                    'Event Name': event_name,
                    'Event Location': event_location,
                    'Event Date': event_date,
                    'Fighter 1': fighter1,
                    'Fighter 2': fighter2,
                    'Fighter 1 ID': fighter1_id,
                    'Fighter 2 ID': fighter2_id,
                    'Weight Class': weight_class,
                    'Winning Fighter': "TBD" if is_upcoming else fighter1,  # For upcoming events, winner is TBD
                    'Winning Method': winning_method,
                    'Winning Round': winning_round,
                    'Winning Time': winning_time,
                    'Referee': referee,
                    'Fight Type': 'Main Event'
                })
            
            print(f"Main event captured: {fighter1} vs {fighter2}")
            
            # Direct method targeting the exact structure shown in the screenshot
            print("Trying to find the fight card using the exact structure from the screenshot")
            
            # Find all existing match numbers on the page
            match_numbers = set()
            for num in soup.find_all(string=lambda s: s and s.strip().isdigit()):
                match_num = int(num.strip())
                if 1 <= match_num <= 30:  # Increased upper limit for potential larger cards
                    match_numbers.add(match_num)
            
            # Sort and reverse the match numbers
            sorted_matches = sorted(match_numbers, reverse=True)
            
            # Iterate through found matches in reverse order
            for i in sorted_matches:
                # Find all elements that contain this number
                match_elems = soup.find_all(string=lambda s: s and s.strip() == str(i))
                for match_elem in match_elems:
                    # Check if this is in a table row
                    parent_tr = None
                    parent = match_elem.parent
                    while parent and parent.name != 'tr':
                        parent = parent.parent
                    
                    if parent and parent.name == 'tr':
                        parent_tr = parent
                    else:
                        continue
                    
                    # Now try to find fighters in this row
                    # Look for the fighter names - they might be in links or in plain text
                    fighter_names = []
                    fighter_ids = []
                    
                    # Try to find fighter names by looking for links
                    fighter_links = parent_tr.find_all('a', href=lambda href: href and '/fighter/' in href) 
                    if len(fighter_links) >= 2:
                        # Found fighter links directly
                        fighter1_link = fighter_links[0]
                        fighter2_link = fighter_links[1]
                        
                        fighter1 = add_spaces_to_name(fighter1_link.text)
                        fighter2 = add_spaces_to_name(fighter2_link.text)
                        
                        fighter1_url = fighter1_link['href']
                        fighter2_url = fighter2_link['href']
                        
                        fighter1_id = fighter1_url.split('-')[-1] if fighter1_url else "Unknown"
                        fighter2_id = fighter2_url.split('-')[-1] if fighter2_url else "Unknown"
                        
                        fighter_names = [fighter1, fighter2]
                        fighter_ids = [fighter1_id, fighter2_id]
                    else:
                        # Try to find fighter names in the text of column cells
                        # Looking for elements with fighter names, based on the structure
                        fighter_cells = parent_tr.find_all(['td', 'div'], class_=lambda c: c and ('fighter' in c or 'name' in c))
                        if len(fighter_cells) >= 2:
                            for cell in fighter_cells[:2]:
                                # Extract the text, stripping any record or other details
                                text = cell.text
                                # Extract just the fighter name (before any record in brackets)
                                fighter_name = add_spaces_to_name(text.split('(')[0])
                                fighter_names.append(fighter_name)
                                fighter_ids.append("Unknown")  # We don't have IDs in this case
                    
                    # If we found fighter names, proceed
                    if len(fighter_names) >= 2:
                        # Find the weight class
                        weight_class = "Unknown"
                        # Look for a cell with a known weight class name
                        weight_classes = ['Flyweight', 'Bantamweight', 'Featherweight', 'Lightweight', 
                                          'Welterweight', 'Middleweight', 'Light Heavyweight', 'Heavyweight', 
                                          'Strawweight', 'Women\'s Flyweight', 'Women\'s Bantamweight', 
                                          'Women\'s Featherweight', 'Women\'s Strawweight']
                        
                        for wc in weight_classes:
                            wc_elem = parent_tr.find(string=lambda s: s and wc in s)
                            if wc_elem:
                                weight_class = wc
                                break
                        
                        all_data.append({
                            'Event Name': event_name,
                            'Event Location': event_location,
                            'Event Date': event_date,
                            'Fighter 1': fighter_names[0],
                            'Fighter 2': fighter_names[1],
                            'Fighter 1 ID': fighter_ids[0] if len(fighter_ids) > 0 else "Unknown",
                            'Fighter 2 ID': fighter_ids[1] if len(fighter_ids) > 1 else "Unknown",
                            'Weight Class': weight_class,
                            'Winning Fighter': "TBD" if is_upcoming else fighter_names[0],
                            'Winning Method': "N/A" if is_upcoming else "Unknown",
                            'Winning Round': "N/A" if is_upcoming else "Unknown",
                            'Winning Time': "N/A" if is_upcoming else "Unknown",
                            'Referee': "N/A" if is_upcoming else "Unknown",
                            'Fight Type': f'Undercard (Fight {i})'
                        })
                        print(f"Found fight {i}: {fighter_names[0]} vs {fighter_names[1]}")
            
            # If the direct targeting method didn't find all fights, try an alternative approach
            if len(all_data) < 11:  # Expected to have main event + 10 other fights
                print("Direct targeting didn't find all fights. Trying alternative approach...")
                
                # Try finding all tables that might contain the fight card
                tables = soup.find_all('table')
                for table in tables:
                    # Check if this table has rows with match numbers
                    has_match_numbers = False
                    rows = table.find_all('tr')
                    for row in rows:
                        # Look for any cell that contains just a number between 1-11
                        for cell in row.find_all('td'):
                            cell_text = cell.text.strip()
                            if cell_text.isdigit() and 1 <= int(cell_text) <= 11:
                                has_match_numbers = True
                                break
                        if has_match_numbers:
                            break
                    
                    if has_match_numbers:
                        print(f"Found a table with match numbers. Analyzing rows...")
                        for row in rows:
                            # Skip header rows
                            if row.find('th'):
                                continue
                            
                            # Try to find match number
                            match_num = None
                            for cell in row.find_all('td'):
                                cell_text = cell.text.strip()
                                if cell_text.isdigit() and 1 <= int(cell_text) <= 11:
                                    match_num = int(cell_text)
                                    break
                            
                            if not match_num:
                                continue
                            
                            # Look for fighter names
                            all_text = row.get_text(' ', strip=True)
                            print(f"Row {match_num} text: {all_text}")
                            
                            # Find all text segments that might be fighter names
                            segments = all_text.split(' ')
                            segments = [s for s in segments if s and s not in ['vs', 'VS', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']]
                            
                            # If we have at least two segments, we can extract fighter names
                            if len(segments) >= 4:  # Need at least 4 segments to have two names
                                # This is a simplification - we're assuming fighter names are at the beginning
                                # In reality, you'd need to do more parsing
                                name1_parts = []
                                name2_parts = []
                                
                                # Let's assume fighter names are separated by 'vs'
                                vs_found = False
                                for seg in segments:
                                    if seg.lower() == 'vs':
                                        vs_found = True
                                        continue
                                    
                                    if not vs_found:
                                        name1_parts.append(seg)
                                    else:
                                        name2_parts.append(seg)
                                
                                if name1_parts and name2_parts:
                                    # Try to find the weight class
                                    weight_classes = ['Flyweight', 'Bantamweight', 'Featherweight', 'Lightweight', 
                                                      'Welterweight', 'Middleweight', 'Light Heavyweight', 'Heavyweight', 
                                                      'Strawweight', 'Women\'s Flyweight', 'Women\'s Bantamweight', 
                                                      'Women\'s Featherweight', 'Women\'s Strawweight']
                                    
                                    weight_class = "Unknown"
                                    for wc in weight_classes:
                                        if wc in all_text:
                                            weight_class = wc
                                            # Remove weight class from name parts
                                            name1_parts = [p for p in name1_parts if p != wc]
                                            name2_parts = [p for p in name2_parts if p != wc]
                                            break
                                    
                                    fighter1 = ' '.join(name1_parts).strip()
                                    fighter2 = ' '.join(name2_parts).strip()
                                    
                                    # Only add if we haven't already added this fight
                                    already_exists = False
                                    for fight in all_data:
                                        if (fight.get('Fight Type') == f'Undercard (Fight {match_num})' or 
                                            (fight.get('Fighter 1') == fighter1 and fight.get('Fighter 2') == fighter2) or
                                            (fight.get('Fighter 1') == fighter2 and fight.get('Fighter 2') == fighter1)):
                                            already_exists = True
                                            break
                                    
                                    if not already_exists:
                                        all_data.append({
                                            'Event Name': event_name,
                                            'Event Location': event_location,
                                            'Event Date': event_date,
                                            'Fighter 1': fighter1,
                                            'Fighter 2': fighter2,
                                            'Fighter 1 ID': "Unknown",
                                            'Fighter 2 ID': "Unknown",
                                            'Weight Class': weight_class,
                                            'Winning Fighter': "TBD" if is_upcoming else fighter1,
                                            'Winning Method': "N/A" if is_upcoming else "Unknown",
                                            'Winning Round': "N/A" if is_upcoming else "Unknown",
                                            'Winning Time': "N/A" if is_upcoming else "Unknown",
                                            'Referee': "N/A" if is_upcoming else "Unknown",
                                            'Fight Type': f'Undercard (Fight {match_num})'
                                        })
                                        print(f"Found fight {match_num}: {fighter1} vs {fighter2}")
            
            # Fallback method - try to extract from the raw HTML
            if len(all_data) < 6:  # If we still haven't found enough fights
                print("Still not enough fights found. Using fallback method to extract from HTML...")
                
                # Based on the screenshot, we know the exact structure we're looking for
                # The table rows likely have a pattern of:
                # <td>match_number</td> <td>fighter1_name</td> <td>vs</td> <td>fighter2_name</td> <td>weight_class</td>
                
                # Find all rows
                all_rows = soup.find_all('tr')
                for row in all_rows:
                    cells = row.find_all('td')
                    if len(cells) < 3:  # Need at least 3 cells
                        continue
                    
                    # Try to identify if this row has a match number
                    match_num = None
                    first_cell_text = cells[0].text.strip()
                    if first_cell_text.isdigit() and 1 <= int(first_cell_text) <= 11:
                        match_num = int(first_cell_text)
                    else:
                        continue
                    
                    # Extract the HTML of this row
                    row_html = str(row)
                    print(f"Found row with match number {match_num}. HTML: {row_html[:100]}...")
                    
                    # Let's try to extract fighter names and weight class directly
                    fighter_names = []
                    weight_class = "Unknown"
                    
                    # Extract all text from this row, removing common non-name elements
                    row_text = row.get_text(' ', strip=True)
                    print(f"Row text: {row_text}")
                    
                    # Try to identify fighter name patterns in the HTML
                    # This is a last resort approach
                    
                    # Check if there's a hardcoded approach we can use based on the screenshot
                    # If the screenshot shows a clear pattern like:
                    # <td>11</td><td>Kelvin Gastelum</td><td>vs</td><td>Joe Pyfer</td><td>Middleweight</td>
                    
                    # Let's extract all text cells and manually parse them
                    cell_texts = [cell.text.strip() for cell in cells]
                    print(f"Cell texts: {cell_texts}")
                    
                    if len(cell_texts) >= 5:
                        # Try to find a pattern that matches the screenshot
                        # Pattern: [number, fighter1, 'vs', fighter2, weight_class]
                        for i in range(len(cell_texts) - 4):
                            if (cell_texts[i].isdigit() and 
                                (cell_texts[i+2] == 'vs' or cell_texts[i+2] == 'VS')):
                                
                                match_num = int(cell_texts[i])
                                fighter1 = add_spaces_to_name(cell_texts[i+1])
                                fighter2 = add_spaces_to_name(cell_texts[i+3])
                                # Try to get weight class
                                for j in range(i+4, len(cell_texts)):
                                    if cell_texts[j] in ['Flyweight', 'Bantamweight', 'Featherweight', 'Lightweight', 
                                                         'Welterweight', 'Middleweight', 'Light Heavyweight', 'Heavyweight', 
                                                         'Strawweight', 'Women\'s Flyweight', 'Women\'s Bantamweight', 
                                                         'Women\'s Featherweight', 'Women\'s Strawweight']:
                                        weight_class = cell_texts[j]
                                        break
                                
                                # Only add if we haven't already added this fight
                                already_exists = False
                                for fight in all_data:
                                    if (fight.get('Fight Type') == f'Undercard (Fight {match_num})' or 
                                        (fight.get('Fighter 1') == fighter1 and fight.get('Fighter 2') == fighter2) or
                                        (fight.get('Fighter 1') == fighter2 and fight.get('Fighter 2') == fighter1)):
                                        already_exists = True
                                        break
                                
                                if not already_exists:
                                    all_data.append({
                                        'Event Name': event_name,
                                        'Event Location': event_location,
                                        'Event Date': event_date,
                                        'Fighter 1': fighter1,
                                        'Fighter 2': fighter2,
                                        'Fighter 1 ID': "Unknown",
                                        'Fighter 2 ID': "Unknown",
                                        'Weight Class': weight_class,
                                        'Winning Fighter': "TBD" if is_upcoming else fighter1,
                                        'Winning Method': "N/A" if is_upcoming else "Unknown",
                                        'Winning Round': "N/A" if is_upcoming else "Unknown",
                                        'Winning Time': "N/A" if is_upcoming else "Unknown",
                                        'Referee': "N/A" if is_upcoming else "Unknown",
                                        'Fight Type': f'Undercard (Fight {match_num})'
                                    })
                                    print(f"Found fight {match_num}: {fighter1} vs {fighter2}")
                                    break  # Move to next row
                    
                    # If we couldn't extract fighter names using the pattern, try a more aggressive approach
                    if len(fighter_names) < 2:
                        print("Using more aggressive parsing for row")
                        # This is a simplification - we would need to do more careful text parsing
                        # ...
            
            # Create DataFrame and save to CSV
            if all_data:
                df = pd.DataFrame(all_data)
                file_path = './data/upcoming_event_data_sherdog.csv'
                
                # Create data directory if it doesn't exist
                os.makedirs('./data', exist_ok=True)
                
                # Determine write mode (append if file exists, write if not)
                write_mode = 'a' if os.path.isfile(file_path) else 'w'
                df.to_csv(file_path, mode=write_mode, header=not os.path.isfile(file_path), index=False)
                
                # Clean the data by stripping strings
                df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
                
                print(f"Data successfully written to {file_path}")
                print(f"Total number of fights scraped: {len(df)}")
                print(f"Column names: {list(df.columns)}")
                
                return df
            else:
                print("No fight data found on the page.")
                return None
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error scraping event: {e}")
        import traceback
        traceback.print_exc()
        return None

# Example usage
if __name__ == "__main__":
    # You can input a single event URL here
    # event_url = input("Enter the Sherdog event URL: ")
    event_url = 'https://www.sherdog.com/events/UFC-314-Volkanovski-vs-Lopes-106606'
    scrape_single_event(event_url)