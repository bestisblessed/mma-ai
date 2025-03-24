import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import datetime
import numpy as np
import os

st.set_page_config(page_title="UFC Odds Movement", page_icon="🥊", layout="wide")

def extract_timestamp(filename):
    if not isinstance(filename, str):
        return None
    
    parts = filename.split('_')
    if len(parts) < 5:
        return None
    
    try:
        date_str = parts[3]  # 20250227
        time_str = parts[4].split('.')[0]  # 1406
        
        year = date_str[:4]
        month = date_str[4:6]
        day = date_str[6:8]
        
        hour = time_str[:2]
        minute = time_str[2:4]
        
        return datetime.datetime(int(year), int(month), int(day), int(hour), int(minute))
    except (IndexError, ValueError):
        return None

def parse_odds(odds_string):
    if not isinstance(odds_string, str):
        return None, None
    
    if '|' not in odds_string or odds_string == "- | -":
        return None, None
    
    try:
        parts = odds_string.split('|')
        return parts[0].strip(), parts[1].strip()
    except:
        return None, None

def get_odds_shift_description(start_odds, end_odds):
    if not start_odds or not end_odds:
        return "No data", "gray"
    
    try:
        # Convert string odds to integers
        start_val = int(start_odds.replace('+', ''))
        end_val = int(end_odds.replace('+', ''))
        
        # For negative odds (favorites)
        if start_odds.startswith('-'):
            if end_odds.startswith('-'):
                if end_val > start_val:  # Less negative
                    return f"↓ Weaker Favorite ({start_odds} → {end_odds})", "green"
                elif end_val < start_val:  # More negative
                    return f"↑ Stronger Favorite ({start_odds} → {end_odds})", "red"
                else:
                    return f"No Change ({start_odds} → {end_odds})", "gray"
            else:  # Changed to underdog
                return f"↔ Changed to Underdog ({start_odds} → {end_odds})", "orange"
        
        # For positive odds (underdogs)
        elif start_odds.startswith('+'):
            if end_odds.startswith('+'):
                if end_val > start_val:  # More positive
                    return f"↑ Bigger Underdog ({start_odds} → {end_odds})", "green"
                elif end_val < start_val:  # Less positive
                    return f"↓ Smaller Underdog ({start_odds} → {end_odds})", "red"
                else:
                    return f"No Change ({start_odds} → {end_odds})", "gray"
            else:  # Changed to favorite
                return f"↔ Changed to Favorite ({start_odds} → {end_odds})", "orange"
    except:
        return "Invalid odds format", "gray"
    
    return "No change", "gray"

# Main dashboard function
def create_ufc_odds_dashboard():
    st.title("UFC Fight Night March 22 Odds Movement Dashboard")
    
    # First check if data is in session state
    if 'df_odds_movements' not in st.session_state:
        # Try to load directly if not in session state
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            df = pd.read_csv(os.path.join(base_dir, 'data/ufc_odds_movements.csv'))
            st.session_state['df_odds_movements'] = df
        except Exception as e:
            st.error(f"Error loading odds movement data: {e}")
            st.info("Please ensure 'ufc_odds_movements.csv' is in the data directory.")
            return
    
    # Get data from session state
    df = st.session_state['df_odds_movements']
    
    # Display raw data in an expander for debugging
    with st.expander("Debug: View Raw Data"):
        st.dataframe(df.head(10))
        st.write(f"Total rows: {len(df)}")
        st.write(f"Columns: {df.columns.tolist()}")
    
    # Filter for March 22 fights
    march22_fights = df[df['game_date'].str.contains('March 22', na=False, case=False)]
    
    if len(march22_fights) == 0:
        st.warning("No March 22 fights found in the data. Check the 'game_date' column format.")
        st.stop()
    
    # Extract timestamp from filenames
    march22_fights['timestamp'] = march22_fights.apply(
        lambda row: extract_timestamp(row['file2']), 
        axis=1
    )
    
    # Parse odds
    march22_fights[['odds_before_f1', 'odds_before_f2']] = march22_fights['odds_before'].apply(
        lambda x: pd.Series(parse_odds(x))
    )
    
    march22_fights[['odds_after_f1', 'odds_after_f2']] = march22_fights['odds_after'].apply(
        lambda x: pd.Series(parse_odds(x))
    )
    
    # Define main card matchups
    main_card_matchups = [
        "Sean Brady vs  Leon Edwards",  # Main event
        "Carlos Ulberg vs  Jan Blachowicz",
        "Kevin Holland vs  Gunnar Nelson",
        "Mick Parkin vs  Marcin Tybura",
        "Morgan Charriere vs  Nathaniel Wood"
    ]
    
    # Filter for main card fights
    main_card_df = march22_fights[march22_fights['matchup'].isin(main_card_matchups)]
    
    if len(main_card_df) == 0:
        # If no matches found with exact names, try case-insensitive matching
        main_card_df = march22_fights[march22_fights['matchup'].str.lower().isin([m.lower() for m in main_card_matchups])]
        
        if len(main_card_df) == 0:
            st.warning("No main card fights found. Showing all March 22 fights instead.")
            # Use all matchups instead
            main_card_matchups = march22_fights['matchup'].unique().tolist()
            main_card_df = march22_fights
    
    # Create tabs for different views
    tab2, tab1, tab3 = st.tabs(["Odds Timeline", "Significant Odds Movements", "Odds Change Summary"])
    
    with tab1:
        st.header("Significant Odds Movements")
        st.markdown("<h1 style='text-align: center;'>SOON</h1>", unsafe_allow_html=True)
    
    with tab2:
        st.header("Odds Movement Timeline")
        
        # Create selectboxes for fight and sportsbook
        selected_matchup = st.selectbox(
            "Select Fight", 
            main_card_matchups
        )
        
        # Get unique sportsbooks for the selected matchup
        available_sportsbooks = ['All'] + list(main_card_df[main_card_df['matchup'] == selected_matchup]['sportsbook'].unique())
        
        # Set default selection to "Circa" if available, otherwise default to "All"
        default_sportsbook = "Circa" if "Circa" in available_sportsbooks else "All"
        
        selected_sportsbook = st.selectbox("Select Sportsbook", available_sportsbooks, index=available_sportsbooks.index(default_sportsbook))
        
        # Filter data based on selections
        filtered_df = main_card_df[main_card_df['matchup'] == selected_matchup]
        if selected_sportsbook != 'All':
            filtered_df = filtered_df[filtered_df['sportsbook'] == selected_sportsbook]
        
        # Sort by timestamp
        filtered_df = filtered_df.sort_values('timestamp')
        
        if not filtered_df.empty:
            # Extract fighter names for the plot labels
            fighters = selected_matchup.split(' vs ')
            fighter1 = fighters[0].strip()
            fighter2 = fighters[1].strip() if len(fighters) > 1 else ""
            
            # Prepare data for plotting
            plot_data = []
            
            for _, row in filtered_df.iterrows():
                if row['odds_after_f1'] and row['odds_after_f2']:
                    try:
                        # Convert odds strings to numbers for plotting
                        f1_odds = int(row['odds_after_f1'].replace('+', ''))
                        f2_odds = int(row['odds_after_f2'].replace('+', ''))
                        
                        plot_data.append({
                            'timestamp': row['timestamp'],
                            'time': row['timestamp'].strftime('%H:%M') if row['timestamp'] else 'Unknown',
                            'fighter1_odds': row['odds_after_f1'],
                            'fighter2_odds': row['odds_after_f2'],
                            'fighter1_value': f1_odds,
                            'fighter2_value': f2_odds,
                            'sportsbook': row['sportsbook']
                        })
                    except (ValueError, AttributeError):
                        continue
            
            if plot_data:
                # Create dataframe for plotting
                plot_df = pd.DataFrame(plot_data)
                
                # Create interactive chart with Plotly
                fig = go.Figure()
                
                # Add traces for each fighter
                fig.add_trace(go.Scatter(
                    x=plot_df['timestamp'],
                    y=plot_df['fighter1_value'],
                    mode='lines+markers',
                    name=fighter1,
                    line=dict(color='#ff8c00', width=2),
                    marker=dict(size=8),
                    text=plot_df['fighter1_odds'],
                    hovertemplate='%{text}<br>%{x}<br>%{text}<extra></extra>'
                ))
                
                fig.add_trace(go.Scatter(
                    x=plot_df['timestamp'],
                    y=plot_df['fighter2_value'],
                    mode='lines+markers',
                    name=fighter2,
                    line=dict(color='#00bfff', width=2),
                    marker=dict(size=8),
                    text=plot_df['fighter2_odds'],
                    hovertemplate='%{text}<br>%{x}<br>%{text}<extra></extra>'
                ))
                
                # Add reference line at y=0
                fig.add_shape(
                    type="line",
                    x0=plot_df['timestamp'].min(),
                    y0=0,
                    x1=plot_df['timestamp'].max(),
                    y1=0,
                    line=dict(color="gray", width=1, dash="dash"),
                )
                
                # Calculate dynamic y-axis range
                y_min = min(plot_df['fighter1_value'].min(), plot_df['fighter2_value'].min()) - 50
                y_max = max(plot_df['fighter1_value'].max(), plot_df['fighter2_value'].max()) + 50
                
                # Update layout
                fig.update_layout(
                    title=f"Odds Movement: {selected_matchup}",
                    xaxis_title="Time",
                    yaxis_title="American Odds",
                    yaxis=dict(range=[y_min, y_max]),
                    legend_title="Fighter",
                    hovermode="closest",
                    height=600,
                    margin=dict(l=50, r=50, t=50, b=50),
                    template="plotly_dark"
                )
                
                # Display the chart
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.warning("No odds data available for this selection.")
        else:
            st.warning("No data available for the selected fight.")
    
    with tab3:
        st.header("Total Odds Change by Fight")
        st.markdown("<h1 style='text-align: center;'>SOON</h1>", unsafe_allow_html=True)

# Main execution
if __name__ == "__main__":
    create_ufc_odds_dashboard()