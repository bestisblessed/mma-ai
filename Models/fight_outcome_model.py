import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
import xgboost as xgb

# Utility functions to parse height and reach

def parse_height(h):
    if pd.isna(h):
        return np.nan
    if isinstance(h, str):
        if "'" in h:
            try:
                feet, inches = h.split("'")
                return int(feet) * 12 + int(inches)
            except Exception:
                pass
    try:
        return float(h)
    except Exception:
        return np.nan


def parse_reach(r):
    if pd.isna(r):
        return np.nan
    if isinstance(r, str):
        r = r.replace('"', '')
    try:
        return float(r)
    except Exception:
        return np.nan


# Load data
fighters = pd.read_csv('Scrapers/data/fighter_info.csv')
events = pd.read_csv('Scrapers/data/event_data_sherdog.csv')

# Preprocess fighters data
fighters['Birth Date'] = pd.to_datetime(fighters['Birth Date'], errors='coerce')
fighters['Height_in'] = fighters['Height'].apply(parse_height)
fighters['Reach_in'] = fighters['Reach'].apply(parse_reach)
fighters['Stance'] = fighters['Stance'].fillna('Unknown')
fighters['Weight Class'] = fighters['Weight Class'].fillna('Unknown')
fighters['Wins'] = pd.to_numeric(fighters['Wins'], errors='coerce')
fighters['Losses'] = pd.to_numeric(fighters['Losses'], errors='coerce')
fighters['Win_Decision'] = pd.to_numeric(fighters['Win_Decision'], errors='coerce')
fighters['Win_KO'] = pd.to_numeric(fighters['Win_KO'], errors='coerce')
fighters['Win_Sub'] = pd.to_numeric(fighters['Win_Sub'], errors='coerce')
fighters['Loss_Decision'] = pd.to_numeric(fighters['Loss_Decision'], errors='coerce')
fighters['Loss_KO'] = pd.to_numeric(fighters['Loss_KO'], errors='coerce')
fighters['Loss_Sub'] = pd.to_numeric(fighters['Loss_Sub'], errors='coerce')

fighters['Total_Fights'] = fighters['Wins'] + fighters['Losses']
fighters['Win_Ratio'] = fighters['Wins'] / fighters['Total_Fights']
fighters['KO_Ratio'] = fighters['Win_KO'] / fighters['Wins']
fighters['Sub_Ratio'] = fighters['Win_Sub'] / fighters['Wins']
fighters['Dec_Ratio'] = fighters['Win_Decision'] / fighters['Wins']
fighters['KO_Loss_Ratio'] = fighters['Loss_KO'] / fighters['Losses']
fighters['Sub_Loss_Ratio'] = fighters['Loss_Sub'] / fighters['Losses']
fighters['Dec_Loss_Ratio'] = fighters['Loss_Decision'] / fighters['Losses']

# Merge fighters info for each fight
f1 = fighters.add_prefix('F1_')
f2 = fighters.add_prefix('F2_')

# Process events
events['Event Date'] = pd.to_datetime(events['Event Date'], errors='coerce')
events['Event Date'] = events['Event Date'].dt.tz_localize(None)

def get_age(event_date, birth_date):
    if pd.isna(event_date) or pd.isna(birth_date):
        return np.nan
    return (event_date - birth_date).days / 365.25

# Join
merged = events.merge(f1, left_on='Fighter 1 ID', right_on='F1_Fighter_ID', how='left')
merged = merged.merge(f2, left_on='Fighter 2 ID', right_on='F2_Fighter_ID', how='left')

# Drop fights without fighter info
merged = merged.dropna(subset=['F1_Birth Date', 'F2_Birth Date'])

# Age features
merged['F1_Age'] = merged.apply(lambda row: get_age(row['Event Date'], row['F1_Birth Date']), axis=1)
merged['F2_Age'] = merged.apply(lambda row: get_age(row['Event Date'], row['F2_Birth Date']), axis=1)

# Difference features
merged['Age_Diff'] = merged['F1_Age'] - merged['F2_Age']
merged['Height_Diff'] = merged['F1_Height_in'] - merged['F2_Height_in']
merged['Reach_Diff'] = merged['F1_Reach_in'] - merged['F2_Reach_in']
merged['WinRatio_Diff'] = merged['F1_Win_Ratio'] - merged['F2_Win_Ratio']
merged['KO_Ratio_Diff'] = merged['F1_KO_Ratio'] - merged['F2_KO_Ratio']
merged['Sub_Ratio_Diff'] = merged['F1_Sub_Ratio'] - merged['F2_Sub_Ratio']
merged['Dec_Ratio_Diff'] = merged['F1_Dec_Ratio'] - merged['F2_Dec_Ratio']
merged['KO_Loss_Diff'] = merged['F1_KO_Loss_Ratio'] - merged['F2_KO_Loss_Ratio']
merged['Sub_Loss_Diff'] = merged['F1_Sub_Loss_Ratio'] - merged['F2_Sub_Loss_Ratio']
merged['Dec_Loss_Diff'] = merged['F1_Dec_Loss_Ratio'] - merged['F2_Dec_Loss_Ratio']
merged['TotalFights_Diff'] = merged['F1_Total_Fights'] - merged['F2_Total_Fights']

# Event features
merged['Event_Year'] = merged['Event Date'].dt.year
merged['Event_Month'] = merged['Event Date'].dt.month
merged['Main_Event'] = (merged['Fight Type'].str.contains('Main Event')).astype(int)
merged['F1_Home'] = merged.apply(
    lambda row: int(pd.notna(row['F1_Nationality']) and pd.notna(row['Event Location']) and row['F1_Nationality'] in row['Event Location']),
    axis=1
)
merged['F2_Home'] = merged.apply(
    lambda row: int(pd.notna(row['F2_Nationality']) and pd.notna(row['Event Location']) and row['F2_Nationality'] in row['Event Location']),
    axis=1
)

# Target - Fighter 1 is always the winner in the raw data.
merged['F1_Win'] = 1

# Create mirrored version where Fighter 2 is treated as Fighter 1 with label 0
swap_cols = {}
for col in merged.columns:
    if col.startswith('F1_'):
        swap_cols[col] = col.replace('F1_', 'F2_')
    elif col.startswith('F2_'):
        swap_cols[col] = col.replace('F2_', 'F1_')

mirrored = merged.rename(columns=swap_cols)
mirrored['F1_Win'] = 0

# Adjust difference features for mirrored dataset
diff_cols = ['Age_Diff','Height_Diff','Reach_Diff','WinRatio_Diff','KO_Ratio_Diff',
             'Sub_Ratio_Diff','Dec_Ratio_Diff','KO_Loss_Diff','Sub_Loss_Diff','Dec_Loss_Diff','TotalFights_Diff']
for d in diff_cols:
    mirrored[d] = -mirrored[d]

# Combine original and mirrored data
dataset = pd.concat([merged, mirrored], ignore_index=True)

# Select feature columns
numeric_features = [
    'F1_Age','F2_Age','F1_Height_in','F2_Height_in','F1_Reach_in','F2_Reach_in',
    'F1_Wins','F2_Wins','F1_Losses','F2_Losses','F1_Win_Ratio','F2_Win_Ratio',
    'F1_KO_Ratio','F2_KO_Ratio','F1_Sub_Ratio','F2_Sub_Ratio','F1_Dec_Ratio','F2_Dec_Ratio',
    'F1_KO_Loss_Ratio','F2_KO_Loss_Ratio','F1_Sub_Loss_Ratio','F2_Sub_Loss_Ratio','F1_Dec_Loss_Ratio','F2_Dec_Loss_Ratio',
    'F1_Total_Fights','F2_Total_Fights',
    'Age_Diff','Height_Diff','Reach_Diff','WinRatio_Diff','KO_Ratio_Diff','Sub_Ratio_Diff',
    'Dec_Ratio_Diff','KO_Loss_Diff','Sub_Loss_Diff','Dec_Loss_Diff','TotalFights_Diff',
    'Event_Year','Event_Month','Main_Event','F1_Home','F2_Home'
]

categorical_features = ['F1_Stance','F2_Stance','F1_Weight Class','F2_Weight Class']

X = dataset[numeric_features + categorical_features]
y = dataset['F1_Win']

# Preprocess: impute numeric with median, categorical with mode, one-hot encode categorical
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median'))
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocess = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ]
)

# Combine with model
clf = Pipeline(steps=[
    ('preprocess', preprocess),
    ('model', xgb.XGBClassifier(
        eval_metric='logloss',
        use_label_encoder=False,
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    ))
])

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Fit model
clf.fit(X_train, y_train)

# Evaluate
y_pred = clf.predict(X_test)
y_prob = clf.predict_proba(X_test)[:,1]
acc = accuracy_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_prob)
print(f"Accuracy: {acc:.3f}")
print(f"AUC: {auc:.3f}")

# Show sample predictions
sample = X_test.head(5)
sample_prob = clf.predict_proba(sample)[:,1]
print("Sample fight probabilities for Fighter 1 winning:")
print(sample_prob)
