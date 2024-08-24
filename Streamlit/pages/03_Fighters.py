import streamlit as st
import pandas as pd
import numpy as np

st.title('Fighters')

df_fighter_data = st.session_state['df_fighter_data']
df_event_data = st.session_state['df_event_data']

# Displaying fighters
fighter_names = df_fighter_data['Fighter'].unique()
selected_fighter = st.selectbox('Select a fighter:', fighter_names)

# Filter fighter data
fighter_profile = df_fighter_data[df_fighter_data['Fighter'] == selected_fighter]
st.write(fighter_profile[['Fighter', 'Nickname', 'Birth Date', 'Nationality', 'Hometown', 'Association', 'Weight Class', 'Height', 'Wins', 'Losses']])