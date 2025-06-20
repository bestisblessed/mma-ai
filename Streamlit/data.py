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

# Complete list of all fighter features that need to be swapped
# This ensures feature integrity is maintained when swapping fighter positions
swap_columns = [
    # Basic fighter info
    ('fighter 1', 'fighter 2'),
    ('fighter 1 id', 'fighter 2 id'),
    
    # Age features (handling both column name variants)
    ('fighter1_age_on_fightnight', 'fighter2_age_on_fightnight'),
    ('fighter1_age_on_fight_night', 'fighter2_age_on_fight_night'),
    
    # Physical attributes
    ('fighter1_height_in_inches', 'fighter2_height_in_inches'),
    
    # Performance metrics
    ('fighter1_current_win_streak', 'fighter2_current_win_streak'),
    ('fighter1_recent_win_rate_7fights', 'fighter2_recent_win_rate_7fights'),
    ('fighter1_recent_win_rate_5fights', 'fighter2_recent_win_rate_5fights'),
    ('fighter1_recent_win_rate_3fights', 'fighter2_recent_win_rate_3fights'),
    
    # Career stats
    ('fighter1_total_wins', 'fighter2_total_wins'),
    ('fighter1_total_losses', 'fighter2_total_losses'),
    
    # Fight timing
    ('fighter1_current_layoff', 'fighter2_current_layoff')
]

# Only swap columns that actually exist in the dataframe
existing_swap_columns = []
for col1, col2 in swap_columns:
    if col1 in df.columns and col2 in df.columns:
        existing_swap_columns.append((col1, col2))
    else:
        print(f"Warning: Column pair ({col1}, {col2}) not found in dataset")

print(f"Swapping {len(existing_swap_columns)} feature pairs for {len(rows_to_swap)} rows")

# Perform the swaps
for col1, col2 in existing_swap_columns:
    df.loc[rows_to_swap, [col1, col2]] = df.loc[rows_to_swap, [col2, col1]].values

# Swap the target variable to maintain correctness
df.loc[rows_to_swap, 'target'] = 1 - df.loc[rows_to_swap, 'target']

# Verify data integrity after swapping
print(f"Data integrity check:")
print(f"- Total rows: {len(df)}")
print(f"- Rows swapped: {len(rows_to_swap)}")
print(f"- Target distribution: {df['target'].value_counts().to_dict()}")

# Save the updated dataset
df.to_csv('data/master_logistic_regression.csv', index=False)

# Add enhanced feature engineering
print(f"\n🚀 ADDING ENHANCED FEATURES")
print("=" * 35)

def add_enhanced_features(df):
    """Add enhanced features for improved model performance."""
    print("Adding derived features...")
    
    # Physical advantage features
    df['height_difference'] = df['fighter1_height_in_inches'] - df['fighter2_height_in_inches']
    df['height_advantage_abs'] = abs(df['height_difference'])
    
    # Momentum and activity features
    df['layoff_difference'] = abs(df['fighter1_current_layoff'] - df['fighter2_current_layoff'])
    
    # Experience features
    df['fighter1_total_fights'] = df['fighter1_total_wins'] + df['fighter1_total_losses']
    df['fighter2_total_fights'] = df['fighter2_total_wins'] + df['fighter2_total_losses']
    df['experience_difference'] = df['fighter1_total_fights'] - df['fighter2_total_fights']
    
    # Win rate features
    df['fighter1_win_rate'] = (df['fighter1_total_wins'] / df['fighter1_total_fights']).fillna(0)
    df['fighter2_win_rate'] = (df['fighter2_total_wins'] / df['fighter2_total_fights']).fillna(0)
    df['win_rate_difference'] = df['fighter1_win_rate'] - df['fighter2_win_rate']
    
    # Recent form differences
    df['recent_form_diff_3'] = df['fighter1_recent_win_rate_3fights'] - df['fighter2_recent_win_rate_3fights']
    df['recent_form_diff_5'] = df['fighter1_recent_win_rate_5fights'] - df['fighter2_recent_win_rate_5fights']
    df['recent_form_diff_7'] = df['fighter1_recent_win_rate_7fights'] - df['fighter2_recent_win_rate_7fights']
    
    print(f"✅ Added enhanced features to dataset")
    return df

# Apply feature engineering to master dataset
df = pd.read_csv('data/master_logistic_regression.csv')
df = add_enhanced_features(df)
df.to_csv('data/master_logistic_regression.csv', index=False)

# Create upcoming fights to predict later on
df_events = pd.read_csv('data/master_logistic_regression.csv')
df_fighters = pd.read_csv('data/fighter_info.csv')

# Define the list of upcoming fights (hardcoded)
upcoming_fighters = [
    ('dustin poirier', 'max holloway'),
    ('jamahal hill', 'khalil rountree'),
    ('rafael fiziev', 'ignacio bahamondes'),
    ('curtis blaydes', 'rizvan kuniev'),
    ('tofiq musayev', 'myktybek orolbai'),
    ('nazim sadykhov', 'nikolas motta'),
    ('muhammadjon naimov', 'bogdan grad'),
    ('seok hyeon ko', 'oban elliott'),
    ('ismail naurdiev', 'jun yong park'),
    ('melissa mullins', 'darya zheleznyakova'),
    ('irina alekseeva', 'klaudia sygula'),
    ('tagir ulanbekov', 'azat maksum'),
    ('hamdy abdelwahab', 'mohammed usman')
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

# Function to safely get fighter stats from recent fight data
def get_fighter_stat_from_fight(fighter_name, fight_row, stat_prefix):
    """
    Safely extract fighter stats from fight data, handling the fact that
    the fighter could be in either fighter1 or fighter2 position
    """
    if fight_row is None:
        return None
    
    fighter_name = fighter_name.lower()
    fighter1_name = fight_row['fighter 1'].lower()
    fighter2_name = fight_row['fighter 2'].lower()
    
    if fighter_name == fighter1_name:
        return fight_row.get(f'fighter1_{stat_prefix}', None)
    elif fighter_name == fighter2_name:
        return fight_row.get(f'fighter2_{stat_prefix}', None)
    else:
        return None

# Prepare data for upcoming fights
upcoming_fight_data = []
skipped_fights = []

print(f"\nProcessing {len(upcoming_fighters)} upcoming fights...")

for fighter1, fighter2 in upcoming_fighters:
    # Normalize fighter names
    fighter1 = fighter1.lower()
    fighter2 = fighter2.lower()
    
    print(f"\nProcessing: {fighter1.title()} vs {fighter2.title()}")
    
    # Get fighter details from fighter_info.csv
    fighter1_info = df_fighters[df_fighters['fighter'].str.lower() == fighter1]
    fighter2_info = df_fighters[df_fighters['fighter'].str.lower() == fighter2]
    
    if fighter1_info.empty:
        print(f"  ❌ Missing fighter info for {fighter1}")
        skipped_fights.append((fighter1, fighter2, f"Missing info for {fighter1}"))
        continue
        
    if fighter2_info.empty:
        print(f"  ❌ Missing fighter info for {fighter2}")
        skipped_fights.append((fighter1, fighter2, f"Missing info for {fighter2}"))
        continue
    
    # Calculate fighter age on fight night
    try:
        fighter1_age = calculate_age(fighter1_info.iloc[0]['birth date'])
        fighter2_age = calculate_age(fighter2_info.iloc[0]['birth date'])
    except Exception as e:
        print(f"  ❌ Error calculating ages: {e}")
        skipped_fights.append((fighter1, fighter2, f"Age calculation error: {e}"))
        continue
    
    # Get fighter height in inches
    fighter1_height = fighter1_info.iloc[0].get('height_in_inches', None)
    fighter2_height = fighter2_info.iloc[0].get('height_in_inches', None)
    
    if pd.isna(fighter1_height) or pd.isna(fighter2_height):
        print(f"  ❌ Missing height data")
        skipped_fights.append((fighter1, fighter2, "Missing height data"))
        continue
    
    # Get most recent fight stats for current win streak and layoff
    fighter1_recent_fight = get_most_recent_fight_stats(fighter1, df_events)
    fighter2_recent_fight = get_most_recent_fight_stats(fighter2, df_events)
    
    if fighter1_recent_fight is None:
        print(f"  ❌ No recent fight data for {fighter1}")
        skipped_fights.append((fighter1, fighter2, f"No recent fight data for {fighter1}"))
        continue
        
    if fighter2_recent_fight is None:
        print(f"  ❌ No recent fight data for {fighter2}")
        skipped_fights.append((fighter1, fighter2, f"No recent fight data for {fighter2}"))
        continue
    
    # Extract win streaks using the improved function
    fighter1_win_streak = get_fighter_stat_from_fight(fighter1, fighter1_recent_fight, 'current_win_streak')
    fighter2_win_streak = get_fighter_stat_from_fight(fighter2, fighter2_recent_fight, 'current_win_streak')
    
    if fighter1_win_streak is None or fighter2_win_streak is None:
        print(f"  ❌ Missing win streak data")
        skipped_fights.append((fighter1, fighter2, "Missing win streak data"))
        continue
    
    # Calculate layoff (time since last fight)
    today = datetime.today()
    try:
        fighter1_layoff = (today - parse_event_date(fighter1_recent_fight['event date'])).days
        fighter2_layoff = (today - parse_event_date(fighter2_recent_fight['event date'])).days
    except Exception as e:
        print(f"  ❌ Error calculating layoffs: {e}")
        skipped_fights.append((fighter1, fighter2, f"Layoff calculation error: {e}"))
        continue
    
    # Get additional stats for enhanced features
    fighter1_total_wins = fighter1_info.iloc[0].get('wins', 0)
    fighter1_total_losses = fighter1_info.iloc[0].get('losses', 0)
    fighter2_total_wins = fighter2_info.iloc[0].get('wins', 0)
    fighter2_total_losses = fighter2_info.iloc[0].get('losses', 0)
    
    # Calculate recent win rates (using the same logic as training data)
    fighter1_recent_3 = get_fighter_stat_from_fight(fighter1, fighter1_recent_fight, 'recent_win_rate_3fights') or 0
    fighter1_recent_5 = get_fighter_stat_from_fight(fighter1, fighter1_recent_fight, 'recent_win_rate_5fights') or 0
    fighter1_recent_7 = get_fighter_stat_from_fight(fighter1, fighter1_recent_fight, 'recent_win_rate_7fights') or 0
    fighter2_recent_3 = get_fighter_stat_from_fight(fighter2, fighter2_recent_fight, 'recent_win_rate_3fights') or 0
    fighter2_recent_5 = get_fighter_stat_from_fight(fighter2, fighter2_recent_fight, 'recent_win_rate_5fights') or 0
    fighter2_recent_7 = get_fighter_stat_from_fight(fighter2, fighter2_recent_fight, 'recent_win_rate_7fights') or 0
    
    # Create a new row with all data including enhanced features
    new_row = {
        # Basic features
        'fighter1_age_on_fight_night': fighter1_age,
        'fighter2_age_on_fight_night': fighter2_age,
        'fighter1_height_in_inches': fighter1_height,
        'fighter2_height_in_inches': fighter2_height,
        'fighter1_current_win_streak': fighter1_win_streak,
        'fighter2_current_win_streak': fighter2_win_streak,
        'fighter1_current_layoff': fighter1_layoff,
        'fighter2_current_layoff': fighter2_layoff,
        
        # Recent performance features
        'fighter1_recent_win_rate_3fights': fighter1_recent_3,
        'fighter2_recent_win_rate_3fights': fighter2_recent_3,
        'fighter1_recent_win_rate_5fights': fighter1_recent_5,
        'fighter2_recent_win_rate_5fights': fighter2_recent_5,
        'fighter1_recent_win_rate_7fights': fighter1_recent_7,
        'fighter2_recent_win_rate_7fights': fighter2_recent_7,
        
        # Career statistics
        'fighter1_total_wins': fighter1_total_wins,
        'fighter2_total_wins': fighter2_total_wins,
        'fighter1_total_losses': fighter1_total_losses,
        'fighter2_total_losses': fighter2_total_losses,
        
        # Age difference
        'age_difference': fighter1_age - fighter2_age,
        
        # Fighter names
        'fighter 1': fighter1.title(),
        'fighter 2': fighter2.title()
    }
    
    upcoming_fight_data.append(new_row)
    print(f"  ✅ Successfully processed")

print(f"\n📊 Summary:")
print(f"- Successfully processed: {len(upcoming_fight_data)} fights")
print(f"- Skipped: {len(skipped_fights)} fights")

if skipped_fights:
    print(f"\n❌ Skipped fights:")
    for f1, f2, reason in skipped_fights:
        print(f"  - {f1.title()} vs {f2.title()}: {reason}")

# Convert the list of dictionaries into a DataFrame
if upcoming_fight_data:
    upcoming_fights_df = pd.DataFrame(upcoming_fight_data)
    
    # Apply the same feature engineering as training data
    print(f"\nApplying feature engineering to upcoming fights...")
    upcoming_fights_df = add_enhanced_features(upcoming_fights_df)
    
    upcoming_fights_df.to_csv('data/upcoming_fights.csv', index=False)
    print(f"\n✅ Saved {len(upcoming_fights_df)} upcoming fights with enhanced features to upcoming_fights.csv")
else:
    print(f"\n❌ No upcoming fights data to save!")

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

