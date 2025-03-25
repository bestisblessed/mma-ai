import shutil
import os
import pandas as pd
import numpy as np
import re
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import os
import shutil

shutil.rmtree("data", ignore_errors=True)
os.makedirs("data")
shutil.rmtree("Streamlit/data", ignore_errors=True)
os.makedirs("Streamlit/data")
os.system('cp "../Scrapers/data/event_data_sherdog.csv" "data/"')
os.system('cp "../Scrapers/data/fighter_info.csv" "data/"')
os.system('cp "../Scrapers/data/event_data_sherdog.csv" "Streamlit/data/"')
os.system('cp "../Scrapers/data/fighter_info.csv" "Streamlit/data/"')
os.system('cp "/Users/td/Code/odds-monitoring/UFC/Analysis/data/ufc_odds_movements_fightoddsio.csv" "data/"')
os.system('cp "/Users/td/Code/odds-monitoring/UFC/Analysis/data/ufc_odds_movements.csv" "data/"')
# shutil.make_archive("data/fighters_data", 'zip', "../Scrapers/data", "fighters") # The zip file "fighters_data.zip" will be created in the "data" directory
# shutil.make_archive("data/fighters", 'zip', "../Scrapers/data/fighters")


# # Remove the backup directory if it exists
# if os.path.exists('data-bak'):
#     shutil.rmtree('data-bak')

# # Rename the current 'data' directory to 'data-bak'
# if os.path.exists('data'):
#     os.rename('data', 'data-bak')

# # Create a new 'data' directory
# os.makedirs('data')

# # Copy the required files and directory to the new 'data' directory
# shutil.copy('../../Scrapers/data/fighter_info.csv', 'data/')
# shutil.copy('../../Scrapers/data/event_data_sherdog.csv', 'data/')
# shutil.copy('../../Scrapers/data/github/master.csv', 'data/')
# shutil.copytree('../../Scrapers/data/fighters', 'data/fighters')

# # Load event data and clean it
# df = pd.read_csv('data/event_data_sherdog.csv')
# df.columns = df.columns.str.lower().str.strip()  # Clean column names
# for col in df.select_dtypes(include=['object']).columns:
#     df[col] = df[col].str.lower().str.strip()  # Clean string values
# df.to_csv('data/event_data_sherdog.csv', index=False)  # Save cleaned data

# # Load fighter_info.csv and clean it
# df_fighters = pd.read_csv('data/fighter_info.csv')
# df_fighters.columns = df_fighters.columns.str.lower().str.strip()  # Clean column names
# for col in df_fighters.select_dtypes(include=['object']).columns:
#     df_fighters[col] = df_fighters[col].str.lower().str.strip()  # Clean string values
# df_fighters.to_csv('data/fighter_info.csv', index=False)  # Save cleaned data

# # Load master_logistic_regression.csv and clean it
# df = pd.read_csv('data/master_logistic_regression.csv')
# df.columns = df.columns.str.lower().str.strip()  # Clean column names
# for col in df.select_dtypes(include=['object']).columns:
#     df[col] = df[col].str.lower().str.strip()  # Clean string values
# df.to_csv('data/master_logistic_regression.csv', index=False)  # Save cleaned data

# # Loop through all CSV files in the 'data' directory and clean them
# for filename in os.listdir('data'):
#     if filename.endswith('.csv'):
#         df = pd.read_csv(f'data/{filename}')
#         df.columns = df.columns.str.lower().str.strip()
#         df = df.apply(lambda x: x.str.lower().str.strip() if x.dtype == 'object' else x)
#         df.to_csv(f'data/{filename}', index=False)

# For Predictive Modeling
# Remove all fights before 2012
df = pd.read_csv('data/event_data_sherdog.csv')
initial_row_count = len(df)  # Capture initial row count
df['event date'] = pd.to_datetime(df['event date'], errors='coerce')
df = df[df['event date'] >= '2012-01-01']
filtered_row_count = len(df)  # Capture row count after filtering
print(f"\nFiltered out {initial_row_count - filtered_row_count} rows due to events before 2012.")
print(f"Total rows before filtering: {initial_row_count}")
print(f"Total rows after filtering: {filtered_row_count}")
df.to_csv('data/master_logistic_regression.csv', index=False)

# Remove all DQs, No Contests, and Draws
df = pd.read_csv('data/master_logistic_regression.csv')
initial_row_count = len(df)  # Capture initial row count
df = df[~df['winning method'].str.contains('Disqualification|No contest|Draw', case=False)]
filtered_row_count = len(df)  # Capture row count after filtering
filtered_out_count = initial_row_count - filtered_row_count
print(f"\nFiltered out {filtered_out_count} fights due to unwanted outcomes (Disqualification, No Contest, Draw).")
print(f"Total number of fights before filtering: {initial_row_count}")
print(f"Total number of fights after filtering: {filtered_row_count}")
df.to_csv('data/master_logistic_regression.csv', index=False)

# Remove special characters from winning fighter column
df = pd.read_csv('data/master_logistic_regression.csv')
def clean_name(name):
    return re.sub(r'[^a-zA-Z\s]', '', name).strip()
df['winning fighter'] = df['winning fighter'].apply(clean_name)
df['fighter 1'] = df['fighter 1'].apply(clean_name)
df['fighter 2'] = df['fighter 2'].apply(clean_name)
df.to_csv('data/master_logistic_regression.csv', index=False)

# Randomly switch 50% of fighter 1 to fighter 2 to balance dataset
df = pd.read_csv('data/master_logistic_regression.csv')

# Create the target variable: 1 if Fighter 1 wins, else 0
df['target'] = (df['winning fighter'] == df['fighter 1']).astype(int)

# Randomly select half of the rows to swap
rows_to_swap = df.sample(frac=0.5, random_state=42).index

# Swap Fighter 1 and Fighter 2 stats in the selected rows
swap_columns = [
    ('fighter1_age_on_fight_night', 'fighter2_age_on_fight_night'),
    ('fighter 1', 'fighter 2'),
    ('fighter1_current_win_streak', 'fighter2_current_win_streak'),
    ('fighter1_recent_win_rate_7fights', 'fighter2_recent_win_rate_7fights'),
    ('fighter1_recent_win_rate_5fights', 'fighter2_recent_win_rate_5fights'),
    ('fighter1_recent_win_rate_3fights', 'fighter2_recent_win_rate_3fights'),
    ('fighter1_current_layoff', 'fighter2_current_layoff'),
    ('fighter1_total_wins', 'fighter2_total_wins'),
    ('fighter1_total_losses', 'fighter2_total_losses'),
    ('fighter1_height_in_inches', 'fighter2_height_in_inches')
]

for col1, col2 in swap_columns:
    df.loc[rows_to_swap, [col1, col2]] = df.loc[rows_to_swap, [col2, col1]].values

# Swap the target variable
df.loc[rows_to_swap, 'target'] = 1 - df.loc[rows_to_swap, 'target']

# Save the updated dataset
df.to_csv('data/master_logistic_regression.csv', index=False)

# Create upcoming fights to predict later on
df_events = pd.read_csv('data/master_logistic_regression.csv')
df_fighters = pd.read_csv('data/fighter_info.csv')

# Define the list of upcoming fights
upcoming_fighters = [
    ('gilbert burns', 'sean brady'),
    ('steve garcia', 'kyle nelson'),
    ('matt schnell', 'alessandro costa'),
    ('trevor peek', 'yanal ashmoz'),
    ('isaac dulgarian', 'brendon marotte')
]

# Function to calculate fighter age on fight night using current date
def calculate_age(birthdate):
    birthdate = datetime.strptime(birthdate, '%b %d, %Y')
    today = datetime.today()
    age = (today - birthdate).days // 365  # Age in years without decimals
    return age

# Function to parse event date
def parse_event_date(date_string):
    return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

# Function to get the most recent fight stats for a given fighter from the event dataset
def get_most_recent_fight_stats(fighter_name, df):
    fighter_fights = df[(df['fighter 1'].str.lower() == fighter_name) | 
                        (df['fighter 2'].str.lower() == fighter_name)]
    
    if fighter_fights.empty:
        return None
    
    most_recent_fight = fighter_fights.sort_values(by='event date', ascending=False).iloc[0]
    return most_recent_fight

# Prepare data for upcoming fights
upcoming_fight_data = []

for fighter1, fighter2 in upcoming_fighters:
    # Normalize fighter names
    fighter1 = fighter1.lower()
    fighter2 = fighter2.lower()
    
    # Get fighter details from fighter_info.csv
    fighter1_info = df_fighters[df_fighters['fighter'].str.lower() == fighter1]
    fighter2_info = df_fighters[df_fighters['fighter'].str.lower() == fighter2]
    
    if fighter1_info.empty or fighter2_info.empty:
        print(f"\nMissing data for {fighter1} or {fighter2}")
        continue
    
    # Calculate fighter age on fight night
    fighter1_age = calculate_age(fighter1_info.iloc[0]['birth date'])
    fighter2_age = calculate_age(fighter2_info.iloc[0]['birth date'])
    
    # Get fighter height in inches
    fighter1_height = fighter1_info.iloc[0]['height_in_inches']
    fighter2_height = fighter2_info.iloc[0]['height_in_inches']
    
    # Get most recent fight stats for current win streak and layoff
    fighter1_recent_fight = get_most_recent_fight_stats(fighter1, df_events)
    fighter2_recent_fight = get_most_recent_fight_stats(fighter2, df_events)
    
    if fighter1_recent_fight is None or fighter2_recent_fight is None:
        print(f"Skipping fight: {fighter1} vs {fighter2} due to missing recent fight data.")
        continue
    
    fighter1_win_streak = fighter1_recent_fight['fighter1_current_win_streak'] if fighter1_recent_fight['fighter 1'].lower() == fighter1 else fighter1_recent_fight['fighter2_current_win_streak']
    fighter2_win_streak = fighter2_recent_fight['fighter1_current_win_streak'] if fighter2_recent_fight['fighter 1'].lower() == fighter2 else fighter2_recent_fight['fighter2_current_win_streak']
    
    # Calculate layoff (time since last fight)
    today = datetime.today()
    fighter1_layoff = (today - parse_event_date(fighter1_recent_fight['event date'])).days
    fighter2_layoff = (today - parse_event_date(fighter2_recent_fight['event date'])).days
    
    # Create a new row with all data
    new_row = {
        'fighter1_age_on_fight_night': fighter1_age,
        'fighter2_age_on_fight_night': fighter2_age,
        'fighter1_height_in_inches': fighter1_height,
        'fighter2_height_in_inches': fighter2_height,
        'fighter1_current_win_streak': fighter1_win_streak,
        'fighter2_current_win_streak': fighter2_win_streak,
        'fighter1_current_layoff': fighter1_layoff,
        'fighter2_current_layoff': fighter2_layoff,
        'fighter 1': fighter1.title(),
        'fighter 2': fighter2.title()
    }
    
    upcoming_fight_data.append(new_row)

# Convert the list of dictionaries into a DataFrame
upcoming_fights_df = pd.DataFrame(upcoming_fight_data)
upcoming_fights_df.to_csv('data/upcoming_fights.csv')

# Copy the master_logistic_regression.csv file to the Streamlit/data/ directory
shutil.copy('data/master_logistic_regression.csv', 'Streamlit/data/master_logistic_regression.csv')

# Optionally, if you want to copy the original event data as well
shutil.copy('data/event_data_sherdog.csv', 'Streamlit/data/event_data_sherdog.csv')

# Optional: Copy the upcoming_fights.csv file as well
shutil.copy('data/upcoming_fights.csv', 'Streamlit/data/upcoming_fights.csv')

# Copy all CSV files from the data directory to the Streamlit/data directory
for filename in os.listdir('data/'):
    if filename.endswith('.csv'):
        shutil.copy(os.path.join('data/', filename), os.path.join('Streamlit/data/', filename))

