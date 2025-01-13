import streamlit as st
import pandas as pd
import numpy as np

st.title('Events')

df_fighter_data = st.session_state['df_fighter_data']
df_event_data = st.session_state['df_event_data']

# Displaying events
event_names = df_event_data['event name'].unique()
# selected_event = st.selectbox('Select an event:', event_names)
event_names_display = [name.title() for name in event_names]  # Capitalize for display
selected_event = st.selectbox('Select an event:', event_names_display)

# Filter event data using the original event name
event_info = df_event_data[df_event_data['event name'] == event_names[event_names_display.index(selected_event)]]

# Check if event_info is not empty
if not event_info.empty:
    # Extract event details
    event_name = event_info['event name'].values[0]
    event_location = event_info['event location'].values[0]
    event_date = event_info['event date'].values[0]

    # Display event details in a more stylish format
    st.write(f"<span style='color: #FF0000; font-size: 24px;'><strong>Event Name:</strong></span> "
              f"<span style='color: #FFFFFF; font-size: 20px;'>{event_name.title()}</span>", unsafe_allow_html=True)
    st.write(f"<span style='color: #FF0000; font-size: 20px;'><strong>Location:</strong></span> "
              f"<span style='color: #FFFFFF; font-size: 18px;'>{event_location.title()}</span>", unsafe_allow_html=True)
    st.write(f"<span style='color: #FF0000; font-size: 20px;'><strong>Date:</strong></span> "
              f"<span style='color: #FFFFFF; font-size: 18px;'>{event_date}</span>", unsafe_allow_html=True)
    st.markdown("---")  # Horizontal line for separation

    # Define basic columns to display
    basic_columns = [
        'fighter 1', 'fighter 2', 
        'weight class', 'winning fighter', 'winning method', 
        'winning round', 'winning time', 'referee',
        'age_difference'
    ]

    # Display all relevant columns for each fight
    st.write(event_info[basic_columns])

    # Checkbox for advanced details
    show_advanced_columns = st.checkbox('Show Advanced Fight Details')

    # Dropdown for selecting a specific fight, only if advanced details are checked
    if show_advanced_columns:
        fight_options = event_info[['fighter 1', 'fighter 2']].apply(lambda x: f"{x[0].title()} vs {x[1].title()}", axis=1)
        # selected_fight = st.selectbox('Select fight:', fight_options)
        selected_fight = st.selectbox('Select fight:', fight_options)
        # selected_fight = st.selectbox(fight_options)
        
        # Filter the selected fight
        fight_info = event_info[event_info[['fighter 1', 'fighter 2']].apply(lambda x: f"{x[0]} vs {x[1]}", axis=1).str.lower() == selected_fight.lower()]

        # If the user wants to see advanced columns
        advanced_columns = [
            'fight type', 'fighter1_age_on_fightnight', 
            'fighter2_age_on_fightnight', 'fighter1_current_win_streak', 
            'fighter2_current_win_streak', 'fighter1_recent_win_rate_7fights', 
            'fighter2_recent_win_rate_7fights', 'fighter1_recent_win_rate_5fights', 
            'fighter2_recent_win_rate_5fights', 'fighter1_recent_win_rate_3fights', 
            'fighter2_recent_win_rate_3fights', 'fighter1_current_layoff', 
            'fighter2_current_layoff', 'fighter1_height_in_inches', 
            'fighter2_height_in_inches', 'fighter1_total_wins', 
            'fighter1_total_losses', 'fighter2_total_wins', 
            'fighter2_total_losses'
        ]

        # # Display advanced columns in a more readable format
        # st.subheader("Advanced Fight Details")
        # for column in advanced_columns:
        #     value = fight_info[column].values[0]
        #     st.markdown(f"**{column.replace('_', ' ').title()}:** {value}")
        st.subheader("Advanced Fight Details")
        for column in advanced_columns:
            value = fight_info[column].values[0]
            formatted_column = column.replace('_', ' ').title()
            if isinstance(value, str):
                value = value.title()  # Convert string values to title case
            elif isinstance(value, (float, np.float64)):
                value = round(value, 2)  # Round floats to 2 decimal places
            st.markdown(f"**{formatted_column}:** {value}")
else:
    st.write("No data available for the selected event.")
