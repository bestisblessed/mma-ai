import streamlit as st
import pandas as pd
import numpy as np

st.title("Data Overview")

df_fighter_data = st.session_state['df_fighter_data']
df_event_data = st.session_state['df_event_data']

# Dropdown button for datasets 
option = st.selectbox('Choose a DataFrame to display:', ('None', 'Fighters', 'Fights'))

if option == 'Fighters':
    st.header('Fighters DataFrame')
    st.write('First few rows:')
    st.dataframe(df_fighter_data)
    st.write('Column names:')
    st.write(df_fighter_data.columns.tolist())

elif option == 'Fights':
    st.header('Fights DataFrame')
    st.write('First few rows:')
    st.dataframe(df_event_data)
    st.write('Column names:')
    st.write(df_event_data.columns.tolist())
