import streamlit as st
import pandas as pd

st.title("Data Overview")

df_fighter_data = st.session_state['df_fighter_data']
df_event_data = st.session_state['df_event_data']

# Create two columns
col1, col2 = st.columns(2)

# Display Fighters DataFrame
with col1:
    st.header('Fighters DataFrame')
    st.write('First few rows:')
    st.dataframe(df_fighter_data)
    st.write('Column names:')
    st.write(", ".join(df_fighter_data.columns))  # Print column names in a readable way

# Display Fights DataFrame
with col2:
    st.header('Fights DataFrame')
    st.write('First few rows:')
    st.dataframe(df_event_data)
    st.write('Column names:')
    st.write(", ".join(df_event_data.columns))  # Print column names in a readable way
