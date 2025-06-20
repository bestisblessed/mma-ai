import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from pandas.core.common import random_state
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_curve, roc_auc_score
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier
import os
import shutil

# ---- Loading Data ---- #
base_dir = os.path.dirname(os.path.abspath(__file__))  # This gives you the directory where the script is located
df = pd.read_csv(os.path.join(base_dir, '../data/master_logistic_regression.csv'))

st.title('Predictive Modeling')
st.write("""
In this section, we will develop models to predict the probabilities of fight outcomes. By leveraging key features related to the fighters' attributes and performance, we aim to determine the likelihood of each fighter winning their match.
""")

st.markdown("##### Feature Selection")
st.code('''
# Enhanced feature set for improved model performance
features = [
    # Basic demographics
    'fighter1_age_on_fight_night', 'fighter2_age_on_fight_night',
    
    # Physical attributes
    'fighter1_height_in_inches', 'fighter2_height_in_inches',
    
    # Performance metrics
    'fighter1_current_win_streak', 'fighter2_current_win_streak',
    
    # Activity & timing
    'fighter1_current_layoff', 'fighter2_current_layoff',
    
    # Recent performance (3, 5, 7 fights)
    'fighter1_recent_win_rate_3fights', 'fighter2_recent_win_rate_3fights',
    'fighter1_recent_win_rate_5fights', 'fighter2_recent_win_rate_5fights', 
    'fighter1_recent_win_rate_7fights', 'fighter2_recent_win_rate_7fights',
    
    # Career statistics
    'fighter1_total_wins', 'fighter2_total_wins',
    'fighter1_total_losses', 'fighter2_total_losses',
    
    # Relative advantages
    'age_difference'
]
X = df[features]
y = df['target'] # fighter 1 win = 1, fighter2 win = 0
''')
st.caption("""Enhanced feature set (19 features) - testing showed this performs best. While some features appear redundant, they provide valuable information that improves model performance.""")

# Define the enhanced feature set (keep all 19 features - testing showed this is optimal)
enhanced_features = [
    # Basic demographics
    'fighter1_age_on_fight_night', 'fighter2_age_on_fight_night',
    
    # Physical attributes
    'fighter1_height_in_inches', 'fighter2_height_in_inches',
    
    # Performance metrics
    'fighter1_current_win_streak', 'fighter2_current_win_streak',
    
    # Activity & timing
    'fighter1_current_layoff', 'fighter2_current_layoff',
    
    # Recent performance (3, 5, 7 fights)
    'fighter1_recent_win_rate_3fights', 'fighter2_recent_win_rate_3fights',
    'fighter1_recent_win_rate_5fights', 'fighter2_recent_win_rate_5fights', 
    'fighter1_recent_win_rate_7fights', 'fighter2_recent_win_rate_7fights',
    
    # Career statistics
    'fighter1_total_wins', 'fighter2_total_wins',
    'fighter1_total_losses', 'fighter2_total_losses',
    
    # Relative advantages
    'age_difference'
]

# Function to convert probabilities to american odds
def probability_to_american_odds(prob):
    if prob >= 0.5:
        return round(-prob / (1 - prob) * 100)
    else:
        return f"+{round((1 - prob) / prob * 100)}"

# Logistic Regression
st.markdown("## Enhanced Logistic Regression")
# df = pd.read_csv('data/master_logistic_regression.csv')
df = pd.read_csv(os.path.join(base_dir, '../data/master_logistic_regression.csv'))
df = df.dropna(subset=['fighter2_height_in_inches'])

# Use enhanced feature set
features = enhanced_features
X = df[features]
y = df['target'] # fighter 1 win = 1, fighter2 win = 0
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0) 

# Impute missing values
imputer = SimpleImputer(strategy='mean')
X_train = imputer.fit_transform(X_train)
X_test = imputer.transform(X_test)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)
model = LogisticRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
coefficients = pd.Series(model.coef_[0], index=features)
coefficients = coefficients.sort_values()
intercept = model.intercept_
r_squared_train = model.score(X_train, y_train)
r_squared_test = model.score(X_test, y_test)
report = classification_report(y_test, y_pred, output_dict=True)
conf_matrix = confusion_matrix(y_test, y_pred)
st.markdown(f"**Accuracy:** `{accuracy * 100:.2f}%`")
st.markdown(f"**R-squared (Training Set):** `{r_squared_train:.2f}`")
st.markdown(f"**R-squared (Test Set):** `{r_squared_test:.2f}`")
st.markdown(f"**Intercept:** `{intercept[0]:.2f}`")
st.markdown("###### Confusion Matrix")
st.table(conf_matrix)
st.markdown("###### Classification Report")
st.dataframe(report)
# st.markdown("###### Coefficients")
# st.write(coefficients)
y_probs = model.predict_proba(X_test)[:, 1]
fpr, tpr, thresholds = roc_curve(y_test, y_probs)
roc_auc = roc_auc_score(y_test, y_probs)
# upcoming_fights_df = pd.read_csv('data/upcoming_fights.csv')
upcoming_fights_df = pd.read_csv(os.path.join(base_dir, '../data/upcoming_fights.csv'))
X_upcoming = upcoming_fights_df[features]
X_upcoming = imputer.transform(X_upcoming)
X_upcoming_scaled = scaler.transform(X_upcoming)
st.markdown("###### Upcoming Fights Predictions")
upcoming_fights_df['fighter1_win_probability'] = model.predict_proba(X_upcoming_scaled)[:, 1]
upcoming_fights_df['fighter1_american_odds'] = upcoming_fights_df['fighter1_win_probability'].apply(probability_to_american_odds)
st.write('\n')
st.write(upcoming_fights_df[['fighter 1', 'fighter 2', 'fighter1_win_probability', 'fighter1_american_odds']])
st.divider()





# Predict Upcoming Fights Probabilities
st.markdown("## Evaluate Using Other Models")
st.write("Now evaluate other machine learning models with the same features as logistic regression to compare results.")

# Random Forest
st.markdown("#### Random Forest")
with st.expander("View Random Forest Results"):
    df = pd.read_csv(os.path.join(base_dir, '../data/master_logistic_regression.csv'))
    df = df.dropna(subset=['fighter2_height_in_inches'])
    features = enhanced_features
    X = df[features]
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0) 
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    model = RandomForestClassifier(random_state=0)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    conf_matrix = confusion_matrix(y_test, y_pred)
    st.markdown(f"**Accuracy:** `{accuracy * 100:.2f}%`")
    st.markdown("###### Confusion Matrix")
    st.table(conf_matrix)
    st.markdown("###### Classification Report")
    st.dataframe(pd.DataFrame(report).transpose())
    upcoming_fights_df = pd.read_csv(os.path.join(base_dir, '../data/upcoming_fights.csv'))
    X_upcoming = upcoming_fights_df[features]
    X_upcoming_scaled = scaler.transform(X_upcoming)
    upcoming_fights_df['fighter1_win_probability'] = model.predict_proba(X_upcoming_scaled)[:, 1]
    upcoming_fights_df['fighter1_american_odds'] = upcoming_fights_df['fighter1_win_probability'].apply(probability_to_american_odds)
st.write(upcoming_fights_df[['fighter 1', 'fighter 2', 'fighter1_win_probability', 'fighter1_american_odds']])

# XGBoost
st.markdown("#### XGBoost (Regularized)")
with st.expander("View XGBoost Results"):
    df = pd.read_csv(os.path.join(base_dir, '../data/master_logistic_regression.csv'))
    df = df.dropna(subset=['fighter2_height_in_inches'])
    features = enhanced_features
    X = df[features]
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    
    # Use imputer instead of scaler for XGBoost (tree-based models don't need scaling)
    imputer = SimpleImputer(strategy='mean')
    X_train = imputer.fit_transform(X_train)
    X_test = imputer.transform(X_test)
    
    # Fixed XGBoost with proper regularization to prevent overfitting
    model = XGBClassifier(
        n_estimators=30,        # Fewer trees to prevent overfitting
        max_depth=3,            # Shallow trees
        learning_rate=0.05,     # Slower learning
        reg_alpha=2,            # L1 regularization
        reg_lambda=2,           # L2 regularization
        subsample=0.7,          # Use 70% of samples
        colsample_bytree=0.7,   # Use 70% of features
        min_child_weight=6,     # Require more samples per leaf
        gamma=1,                # Minimum loss reduction
        random_state=0,
        eval_metric='logloss'
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    conf_matrix = confusion_matrix(y_test, y_pred)
    st.markdown(f"**Accuracy:** `{accuracy * 100:.2f}%`")
    st.markdown("###### Confusion Matrix")
    st.table(conf_matrix)
    st.markdown("###### Classification Report")
    st.dataframe(pd.DataFrame(report).transpose())
    upcoming_fights_df = pd.read_csv(os.path.join(base_dir, '../data/upcoming_fights.csv'))
    X_upcoming = upcoming_fights_df[features]
    X_upcoming_imputed = imputer.transform(X_upcoming)
    upcoming_fights_df['fighter1_win_probability'] = model.predict_proba(X_upcoming_imputed)[:, 1]
    upcoming_fights_df['fighter1_american_odds'] = upcoming_fights_df['fighter1_win_probability'].apply(probability_to_american_odds)
st.write(upcoming_fights_df[['fighter 1', 'fighter 2', 'fighter1_win_probability', 'fighter1_american_odds']])

# LightGBM
st.markdown("#### LightGBM")
with st.expander("View LightGBM Results"):
    df = pd.read_csv(os.path.join(base_dir, '../data/master_logistic_regression.csv'))
    df = df.dropna(subset=['fighter2_height_in_inches'])
    features = enhanced_features
    X = df[features]
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    model = LGBMClassifier(random_state=0, verbose=-1)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    conf_matrix = confusion_matrix(y_test, y_pred)
    st.markdown(f"**Accuracy:** `{accuracy * 100:.2f}%`")
    st.markdown("###### Confusion Matrix")
    st.table(conf_matrix)
    st.markdown("###### Classification Report")
    st.dataframe(pd.DataFrame(report).transpose())
    upcoming_fights_df = pd.read_csv(os.path.join(base_dir, '../data/upcoming_fights.csv'))
    X_upcoming = upcoming_fights_df[features]
    X_upcoming_scaled = scaler.transform(X_upcoming)
    upcoming_fights_df['fighter1_win_probability'] = model.predict_proba(X_upcoming_scaled)[:, 1]
    upcoming_fights_df['fighter1_american_odds'] = upcoming_fights_df['fighter1_win_probability'].apply(probability_to_american_odds)
st.write(upcoming_fights_df[['fighter 1', 'fighter 2', 'fighter1_win_probability', 'fighter1_american_odds']])