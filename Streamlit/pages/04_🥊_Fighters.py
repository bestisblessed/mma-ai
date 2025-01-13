import streamlit as st
import pandas as pd
import numpy as np

st.title('Fighters')

df_fighter_data = st.session_state['df_fighter_data']
df_event_data = st.session_state['df_event_data']

fighter_names = df_fighter_data['fighter'].unique()
fighter_names_display = [name.title() for name in fighter_names]
selected_fighter = st.selectbox('Select a fighter:', fighter_names_display)
fighter_profile = df_fighter_data[df_fighter_data['fighter'] == selected_fighter.lower()]
# st.write(fighter_profile[['fighter', 'nickname', 'birth date', 'nationality', 'hometown', 'association', 'weight class', 'height', 'wins', 'losses']])
# st.write(fighter_profile)
st.header(f"Profile for {selected_fighter.title()}")  # Capitalize for display
columns_to_display = [
    'fighter', 'nickname', 'birth date', 'nationality', 'hometown', 
    'association', 'weight class', 'reach', 'height_in_inches', 'height', 'wins', 'losses', 'current_layoff',
    'current_win_streak', 'recent_win_rate_7fights', 'recent_win_rate_5fights', 'recent_win_rate_3fights'
]
for column in columns_to_display:
    value = fighter_profile[column].values[0]
    if isinstance(value, str):
        st.write(f"{column.title()}: {value.title()}")  # Capitalize string values
    else:
        st.write(f"{column.title()}: {value}")  # Display non-string values as is
