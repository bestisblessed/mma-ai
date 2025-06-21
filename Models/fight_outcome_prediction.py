import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, log_loss
from xgboost import XGBClassifier

# Load data
fights = pd.read_csv('Scrapers/data/event_data_sherdog.csv')
fighters = pd.read_csv('Scrapers/data/fighter_info.csv')

rand_mask = np.random.rand(len(fights)) < 0.5
cols1 = ["Fighter 1","Fighter 1 ID"]
cols2 = ["Fighter 2","Fighter 2 ID"]
tmp = fights.loc[rand_mask, cols1].copy()
fights.loc[rand_mask, cols1] = fights.loc[rand_mask, cols2].values
fights.loc[rand_mask, cols2] = tmp.values

# Preprocess fighter info
fighters['Birth Date'] = pd.to_datetime(fighters['Birth Date'], errors='coerce')

# convert height like 6'1 to inches
def height_to_inches(h):
    try:
        feet, inch = h.split("'")
        return int(feet)*12 + int(inch)
    except:
        return np.nan

fighters['Height_in'] = fighters['Height'].apply(height_to_inches)
fighters['Reach_in'] = pd.to_numeric(
    fighters['Reach'].str.replace('"', ''), errors='coerce'
)

fighters['Total_Fights'] = fighters['Wins'] + fighters['Losses']
fighters['Win_Pct'] = fighters['Wins'] / fighters['Total_Fights']
fighters['KO_Pct'] = fighters['Win_KO'] / fighters['Wins'].replace(0, np.nan)
fighters['Sub_Pct'] = fighters['Win_Sub'] / fighters['Wins'].replace(0, np.nan)
fighters['Dec_Pct'] = fighters['Win_Decision'] / fighters['Wins'].replace(0, np.nan)

fighters['Birth Date'] = pd.to_datetime(fighters['Birth Date'])

stance_le = LabelEncoder()
fighters['Stance_Enc'] = stance_le.fit_transform(fighters['Stance'].fillna('Unknown'))

# Build mapping from fighter ID to attributes
fighter_dict = fighters.set_index('Fighter_ID').to_dict('index')

# Preprocess event data
fights['Event Date'] = pd.to_datetime(fights['Event Date'])
fights['Event Date'] = fights['Event Date'].dt.tz_localize(None)
fights['Event_Year'] = fights['Event Date'].dt.year
fights['Is_Main_Event'] = fights['Fight Type'].apply(lambda x: 1 if 'Main Event' in str(x) else 0)

# Extract country from location
fights['Event_Country'] = fights['Event Location'].apply(lambda x: str(x).split(',')[-1].strip())

# helper to compute fighter statistics at fight time
fights = fights.sort_values('Event Date')

last_fight_date = {}
recent_results = {}
current_streak = {}
head_to_head = {}

rows = []
for _, row in fights.iterrows():
    f1 = fighter_dict.get(row['Fighter 1 ID'], {})
    f2 = fighter_dict.get(row['Fighter 2 ID'], {})
    if not f1 or not f2:
        continue
    # Basic attributes
    f1_age = (row['Event Date'] - f1['Birth Date']).days/365.25 if pd.notnull(f1['Birth Date']) else np.nan
    f2_age = (row['Event Date'] - f2['Birth Date']).days/365.25 if pd.notnull(f2['Birth Date']) else np.nan
    f1_height = f1.get('Height_in', np.nan)
    f2_height = f2.get('Height_in', np.nan)
    f1_reach = f1.get('Reach_in', np.nan)
    f2_reach = f2.get('Reach_in', np.nan)
    # Experience and ratios
    f1_tot = f1['Total_Fights']
    f2_tot = f2['Total_Fights']
    f1_winpct = f1['Win_Pct']
    f2_winpct = f2['Win_Pct']
    f1_kopct = f1['KO_Pct']
    f2_kopct = f2['KO_Pct']
    f1_subpct = f1['Sub_Pct']
    f2_subpct = f2['Sub_Pct']
    f1_decpct = f1['Dec_Pct']
    f2_decpct = f2['Dec_Pct']
    f1_stance = f1['Stance_Enc']
    f2_stance = f2['Stance_Enc']
    stance_same = int(f1_stance == f2_stance)
    # head to head
    pair = tuple(sorted([row['Fighter 1 ID'], row['Fighter 2 ID']]))
    h2h_f1 = head_to_head.get((pair, row['Fighter 1 ID']), 0)
    h2h_f2 = head_to_head.get((pair, row['Fighter 2 ID']), 0)
    fought_before = int(pair in {(p[0], p[1]) for p,_ in head_to_head.keys()})
    # recent win rates
    recent_f1 = recent_results.get(row['Fighter 1 ID'], [])
    recent_f2 = recent_results.get(row['Fighter 2 ID'], [])
    last5_f1 = recent_f1[-5:]
    last5_f2 = recent_f2[-5:]
    last5_rate1 = sum(last5_f1)/5 if len(last5_f1)==5 else np.nan
    last5_rate2 = sum(last5_f2)/5 if len(last5_f2)==5 else np.nan
    streak1 = current_streak.get(row['Fighter 1 ID'], 0)
    streak2 = current_streak.get(row['Fighter 2 ID'], 0)
    days_since_f1 = (row['Event Date'] - last_fight_date.get(row['Fighter 1 ID'], row['Event Date'])).days
    days_since_f2 = (row['Event Date'] - last_fight_date.get(row['Fighter 2 ID'], row['Event Date'])).days
    last_method_f1 = recent_f1[-1] if recent_f1 else np.nan
    last_method_f2 = recent_f2[-1] if recent_f2 else np.nan

    # Build feature row
    feats = {
        'Age_F1': f1_age,
        'Age_F2': f2_age,
        'Age_Diff': f1_age - f2_age if pd.notnull(f1_age) and pd.notnull(f2_age) else np.nan,
        'Height_F1': f1_height,
        'Height_F2': f2_height,
        'Height_Diff': f1_height - f2_height if pd.notnull(f1_height) and pd.notnull(f2_height) else np.nan,
        'Reach_F1': f1_reach,
        'Reach_F2': f2_reach,
        'Reach_Diff': f1_reach - f2_reach if pd.notnull(f1_reach) and pd.notnull(f2_reach) else np.nan,
        'Total_Fights_F1': f1_tot,
        'Total_Fights_F2': f2_tot,
        'Fights_Diff': f1_tot - f2_tot,
        'Win_Pct_F1': f1_winpct,
        'Win_Pct_F2': f2_winpct,
        'Win_Pct_Diff': f1_winpct - f2_winpct,
        'KO_Pct_F1': f1_kopct,
        'KO_Pct_F2': f2_kopct,
        'KO_Pct_Diff': f1_kopct - f2_kopct,
        'Sub_Pct_F1': f1_subpct,
        'Sub_Pct_F2': f2_subpct,
        'Sub_Pct_Diff': f1_subpct - f2_subpct,
        'Dec_Pct_F1': f1_decpct,
        'Dec_Pct_F2': f2_decpct,
        'Dec_Pct_Diff': f1_decpct - f2_decpct,
        'Stance_F1': f1_stance,
        'Stance_F2': f2_stance,
        'Stance_Same': stance_same,
        'Last5_Win_Rate_F1': last5_rate1,
        'Last5_Win_Rate_F2': last5_rate2,
        'Last5_Rate_Diff': (last5_rate1 - last5_rate2) if pd.notnull(last5_rate1) and pd.notnull(last5_rate2) else np.nan,
        'Current_Streak_F1': streak1,
        'Current_Streak_F2': streak2,
        'Streak_Diff': streak1 - streak2,
        'Days_Since_Last_Fight_F1': days_since_f1,
        'Days_Since_Last_Fight_F2': days_since_f2,
        'HeadToHead_F1': h2h_f1,
        'HeadToHead_F2': h2h_f2,
        'Fought_Before': fought_before,
        'Weight_Class': row['Weight Class'],
        'Event_Year': row['Event_Year'],
        'Is_Main_Event': row['Is_Main_Event'],
        'Event_Country_Match_F1': int(f1.get('Nationality','').strip()==row['Event_Country']),
        'Event_Country_Match_F2': int(f2.get('Nationality','').strip()==row['Event_Country'])
    }
    target = int(row['Winning Fighter'] == row['Fighter 1'])
    feats['target'] = target
    feats['F1_ID'] = row['Fighter 1 ID']
    feats['F2_ID'] = row['Fighter 2 ID']
    rows.append(feats)

    # update trackers
    last_fight_date[row['Fighter 1 ID']] = row['Event Date']
    last_fight_date[row['Fighter 2 ID']] = row['Event Date']
    recent_results.setdefault(row['Fighter 1 ID'], []).append(target)
    recent_results.setdefault(row['Fighter 2 ID'], []).append(1-target)
    current_streak[row['Fighter 1 ID']] = current_streak.get(row['Fighter 1 ID'], 0) + (1 if target==1 else -current_streak.get(row['Fighter 1 ID'], 0))
    current_streak[row['Fighter 2 ID']] = current_streak.get(row['Fighter 2 ID'], 0) + (1 if target==0 else -current_streak.get(row['Fighter 2 ID'], 0))
    head_to_head[(pair, row['Fighter 1 ID'])] = h2h_f1 + (1 if target==1 else 0)
    head_to_head[(pair, row['Fighter 2 ID'])] = h2h_f2 + (1 if target==0 else 0)

feat_df = pd.DataFrame(rows)

# Encode categorical weight class
weight_le = LabelEncoder()
feat_df['Weight_Class_Enc'] = weight_le.fit_transform(feat_df['Weight_Class'].fillna('Unknown'))

feature_cols = [c for c in feat_df.columns if c not in ['target','F1_ID','F2_ID','Weight_Class']]

feat_df = feat_df.dropna(subset=['target'])

X = feat_df[feature_cols]
y = feat_df['target']

# fill missing values with 0
X = X.fillna(0)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = XGBClassifier(n_estimators=300, max_depth=5, learning_rate=0.1, subsample=0.9, colsample_bytree=0.8, eval_metric='logloss')
model.fit(X_train, y_train)

preds = model.predict(X_test)
probs = model.predict_proba(X_test)[:,1]

acc = accuracy_score(y_test, preds)
ll = log_loss(y_test, probs)
print('Accuracy:', acc)
print('Log Loss:', ll)

# Example output probabilities for the first 5 fights
print(feat_df[['F1_ID','F2_ID']].head())
print('Sample probabilities:', model.predict_proba(X.iloc[:5])[:,1])
