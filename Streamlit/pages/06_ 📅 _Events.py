import streamlit as st
import pandas as pd
import numpy as np

st.title('Events')

df_fighter_data = st.session_state['df_fighter_data']
df_event_data = st.session_state['df_event_data']

# Displaying events
event_names = df_event_data['Event Name'].unique()
selected_event = st.selectbox('Select an event:', event_names)

# Filter event data
event_info = df_event_data[df_event_data['Event Name'] == selected_event]
st.write(event_info[['Event Name', 'Event Location', 'Event Date', 'Fighter 1', 'Fighter 2', 'Winning Fighter', 'Winning Method']])