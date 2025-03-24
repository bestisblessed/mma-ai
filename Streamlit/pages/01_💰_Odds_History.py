import streamlit as st
import pandas as pd
from datetime import datetime
import os
import plotly.graph_objects as go
from streamlit_elements import elements, mui, html, dashboard
import numpy as np


st.set_page_config(page_title="UFC Odds Movement", page_icon="🥊", layout="wide")
def extract_timestamp(filename):
    if not isinstance(filename, str):
        return None
    parts = filename.split('_')
    if len(parts) < 5:
        return None
    try:
        date_str = parts[3]  
        time_str = parts[4].split('.')[0]  
        year = date_str[:4]
        month = date_str[4:6]
        day = date_str[6:8]
        hour = time_str[:2]
        minute = time_str[2:4]
        return datetime(int(year), int(month), int(day), int(hour), int(minute))
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
def load_and_process_data():
    if 'df_odds_movements' not in st.session_state:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            df = pd.read_csv(os.path.join(base_dir, 'data/ufc_odds_movements.csv'))
            st.session_state['df_odds_movements'] = df
        except Exception as e:
            st.error(f"Error loading odds movement data: {e}")
            st.info("Please ensure 'ufc_odds_movements.csv' is in the data directory.")
            return None
    df = st.session_state['df_odds_movements']
    march22_fights = df[df['game_date'].str.contains('March 22', na=False, case=False)]
    if len(march22_fights) == 0:
        st.warning("No March 22 fights found in the data. Check the 'game_date' column format.")
        return None
    # march22_fights['timestamp'] = march22_fights.apply(
    #     lambda row: extract_timestamp(row['file2']), 
    #     axis=1
    # )
    # march22_fights[['odds_before_f1', 'odds_before_f2']] = march22_fights['odds_before'].apply(
    #     lambda x: pd.Series(parse_odds(x))
    # )
    # march22_fights[['odds_after_f1', 'odds_after_f2']] = march22_fights['odds_after'].apply(
    #     lambda x: pd.Series(parse_odds(x))
    # )
    march22_fights = march22_fights.copy()  # Create a copy to avoid SettingWithCopyWarning
    march22_fights.loc[:, 'timestamp'] = march22_fights['file2'].apply(extract_timestamp)
    march22_fights.loc[:, ['odds_before_f1', 'odds_before_f2']] = march22_fights['odds_before'].apply(parse_odds).tolist()
    march22_fights.loc[:, ['odds_after_f1', 'odds_after_f2']] = march22_fights['odds_after'].apply(parse_odds).tolist()
    main_card_matchups = [
        "Sean Brady vs  Leon Edwards",  
        "Carlos Ulberg vs  Jan Blachowicz",
        "Kevin Holland vs  Gunnar Nelson",
        "Mick Parkin vs  Marcin Tybura",
        "Morgan Charriere vs  Nathaniel Wood"
    ]
    main_card_df = march22_fights[march22_fights['matchup'].isin(main_card_matchups)]
    if len(main_card_df) == 0:
        main_card_df = march22_fights[march22_fights['matchup'].str.lower().isin([m.lower() for m in main_card_matchups])]
        if len(main_card_df) == 0:
            st.warning("No main card fights found. Showing all March 22 fights instead.")
            main_card_matchups = march22_fights['matchup'].unique().tolist()
            main_card_df = march22_fights
    return main_card_df, main_card_matchups
def create_odds_chart(filtered_df, selected_matchup):
    if filtered_df.empty:
        return None
    fighters = selected_matchup.split(' vs ')
    fighter1 = fighters[0].strip()
    fighter2 = fighters[1].strip() if len(fighters) > 1 else ""
    plot_data = []
    for _, row in filtered_df.iterrows():
        if row['odds_after_f1'] and row['odds_after_f2']:
            try:
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
    if not plot_data:
        return None
    plot_df = pd.DataFrame(plot_data)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=plot_df['timestamp'],
        y=plot_df['fighter1_value'],
        mode='lines+markers',
        name=fighter1,
        line=dict(color='#ff8c00'),
        marker=dict(size=8),
        text=plot_df['fighter1_odds'],
        hovertemplate='%{text}<br>%{x}<br>%{text}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=plot_df['timestamp'],
        y=plot_df['fighter2_value'],
        mode='lines+markers',
        name=fighter2,
        line=dict(color='#00bfff'),
        marker=dict(size=8),
        text=plot_df['fighter2_odds'],
        hovertemplate='%{text}<br>%{x}<br>%{text}<extra></extra>'
    ))
    fig.add_shape(
        type="line",
        x0=plot_df['timestamp'].min(),
        y0=0,
        x1=plot_df['timestamp'].max(),
        y1=0,
        line=dict(color="gray", width=1, dash="dash"),
    )
    y_min = min(plot_df['fighter1_value'].min(), plot_df['fighter2_value'].min()) - 50
    y_max = max(plot_df['fighter1_value'].max(), plot_df['fighter2_value'].max()) + 50
    fig.update_layout(
        title=f"Odds Movement: {selected_matchup}",
        xaxis_title="Time",
        yaxis_title="American Odds",
        yaxis=dict(range=[y_min, y_max]),
        legend_title="Fighter",
        hovermode="closest",
        height=600,
        margin=dict(l=50, r=50, t=50, b=50),
        template="plotly_dark",
        plot_bgcolor='rgba(30,30,30,1)',
        paper_bgcolor='rgba(30,30,30,1)',
        font=dict(color='white')
    )
    return fig
def get_odds_shift_description(start_odds, end_odds):
    if not start_odds or not end_odds:
        return "No data", "gray"
    try:
        start_val = int(start_odds.replace('+', ''))
        end_val = int(end_odds.replace('+', ''))
        if start_odds.startswith('-'):
            if end_odds.startswith('-'):
                if end_val > start_val:  
                    return f"↓ Weaker Favorite ({start_odds} → {end_odds})", "green"
                elif end_val < start_val:  
                    return f"↑ Stronger Favorite ({start_odds} → {end_odds})", "red"
                else:
                    return f"No Change ({start_odds} → {end_odds})", "gray"
            else:  
                return f"↔ Changed to Underdog ({start_odds} → {end_odds})", "orange"
        elif start_odds.startswith('+'):
            if end_odds.startswith('+'):
                if end_val > start_val:  
                    return f"↑ Bigger Underdog ({start_odds} → {end_odds})", "green"
                elif end_val < start_val:  
                    return f"↓ Smaller Underdog ({start_odds} → {end_odds})", "red"
                else:
                    return f"No Change ({start_odds} → {end_odds})", "gray"
            else:  
                return f"↔ Changed to Favorite ({start_odds} → {end_odds})", "orange"
    except:
        return "Invalid odds format", "gray"
    return "No change", "gray"
def ufc_odds_dashboard():
    st.title("Odds Tracking & Movement Dashboard")
    
    data = load_and_process_data()
    if data is None:
        return
    
    main_card_df, main_card_matchups = data
    
    # Create tabs for the dashboard
    tabs = st.tabs(["Odds Timeline", "Raw Data"])
    
    with tabs[0]:
        st.header("UFC Fight Night 255 - Edwards vs. Brady")
        
        # Controls - same as React dashboard
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_matchup = st.selectbox("Select Fight", main_card_matchups, key="timeline_matchup")
        
        available_sportsbooks = ['All'] + list(main_card_df[main_card_df['matchup'] == selected_matchup]['sportsbook'].unique())
        with col2:
            selected_sportsbook = st.selectbox("Select Sportsbook", available_sportsbooks, key="timeline_sportsbook")
        
        # Filter data based on selections - same as React dashboard
        filtered_df = main_card_df[main_card_df['matchup'] == selected_matchup].copy()
        if selected_sportsbook != 'All':
            filtered_df = filtered_df[filtered_df['sportsbook'] == selected_sportsbook].copy()
        
        # Sort by timestamp
        filtered_df = filtered_df.sort_values('timestamp')
        
        # Create Plotly chart
        fig = create_odds_chart(filtered_df, selected_matchup)
        
        # Extract fighter names
        fighters = selected_matchup.split(' vs ')
        fighter1 = fighters[0].strip()
        fighter2 = fighters[1].strip() if len(fighters) > 1 else ""
        
        # Calculate movement for selected fighters - same as React dashboard
        if len(filtered_df) >= 2:
            # Initialize movements lists
            f1_movements = []
            f2_movements = []
            prev_f1_odds = None
            prev_f2_odds = None
            first_f1_odds = None
            first_f2_odds = None
            last_f1_odds = None
            last_f2_odds = None
            
            # Go through all sorted records to track line movements
            for _, row in filtered_df.iterrows():
                if row['odds_after_f1'] and row['odds_after_f2']:
                    # Track first valid odds
                    if first_f1_odds is None:
                        first_f1_odds = row['odds_after_f1']
                        first_f2_odds = row['odds_after_f2']
                    
                    # Update last valid odds
                    last_f1_odds = row['odds_after_f1']
                    last_f2_odds = row['odds_after_f2']
                    
                    # For Fighter 1
                    if prev_f1_odds is None:
                        prev_f1_odds = row['odds_after_f1']
                    elif row['odds_after_f1'] != prev_f1_odds:
                        move_desc, move_color = get_odds_shift_description(prev_f1_odds, row['odds_after_f1'])
                        timestamp = row['timestamp'].strftime('%m/%d %H:%M') if row['timestamp'] else 'Unknown'
                        f1_movements.append({
                            'timestamp': timestamp,
                            'description': move_desc,
                            'color': move_color
                        })
                        prev_f1_odds = row['odds_after_f1']
                    
                    # For Fighter 2
                    if prev_f2_odds is None:
                        prev_f2_odds = row['odds_after_f2']
                    elif row['odds_after_f2'] != prev_f2_odds:
                        move_desc, move_color = get_odds_shift_description(prev_f2_odds, row['odds_after_f2'])
                        timestamp = row['timestamp'].strftime('%m/%d %H:%M') if row['timestamp'] else 'Unknown'
                        f2_movements.append({
                            'timestamp': timestamp,
                            'description': move_desc,
                            'color': move_color
                        })
                        prev_f2_odds = row['odds_after_f2']
            
            # Calculate overall movement using first and last valid odds
            if first_f1_odds and last_f1_odds:
                f1_description, f1_color = get_odds_shift_description(first_f1_odds, last_f1_odds)
            else:
                f1_description, f1_color = "No data", "gray"
            
            if first_f2_odds and last_f2_odds:
                f2_description, f2_color = get_odds_shift_description(first_f2_odds, last_f2_odds)
            else:
                f2_description, f2_color = "No data", "gray"
        else:
            f1_description = "Insufficient data"
            f2_description = "Insufficient data"
            f1_color = "gray"
            f2_color = "gray"
            f1_movements = []
            f2_movements = []
        
        # Display chart
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            
            # Add custom CSS for styling
            st.markdown("""
            <style>
            .fighter-card {
                background-color: rgba(30,30,30,1);
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 20px;
                border: 1px solid rgba(60,60,60,1);
            }
            .fighter-name {
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 10px;
                padding-bottom: 10px;
                border-bottom: 1px solid rgba(60,60,60,1);
            }
            .fighter-1-name { color: #ff8c00; }
            .fighter-2-name { color: #00bfff; }
            .movement-label {
                font-size: 14px;
                margin-bottom: 5px;
                color: white;
            }
            .movement-value {
                font-weight: bold;
                font-size: 16px;
                margin-bottom: 15px;
            }
            .timeline-item {
                display: flex;
                margin-bottom: 8px;
            }
            .timestamp {
                min-width: 80px;
                font-size: 13px;
                color: #aaaaaa;
            }
            .description {
                font-size: 14px;
            }
            .section-title {
                font-size: 15px;
                color: white;
                margin-bottom: 10px;
            }
            .scrollable {
                max-height: 300px;
                overflow-y: auto;
                padding-right: 10px;
            }
            .message {
                font-style: italic;
                color: gray;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Create fighter cards
            fighter_cols = st.columns(2)
            
            # Fighter 1 card - Build the complete HTML string without extra indentation
            f1_html = f"""<div class="fighter-card">
<div class="fighter-name fighter-1-name">{fighter1}</div>
<div class="movement-label">Odds Movement:</div>
<div class="movement-value" style="color: {f1_color};">{f1_description}</div>
<div class="section-title">Movement Timeline:</div>
<div class="scrollable">"""
            
            # Add movement timeline without extra indentation
            if selected_sportsbook != 'All' and f1_movements:
                for move in f1_movements:
                    f1_html += f"""<div class="timeline-item">
<div class="timestamp">{move['timestamp']}</div>
<div class="description" style="color: {move['color']};">{move['description']}</div>
</div>"""
            elif selected_sportsbook == 'All':
                f1_html += '<div class="message">Select a specific sportsbook to see line movements</div>'
            else:
                f1_html += '<div class="message">No line movements recorded for this fighter</div>'
            
            f1_html += '</div></div>'
            
            # Render complete HTML string
            with fighter_cols[0]:
                st.markdown(f1_html, unsafe_allow_html=True)
            
            # Fighter 2 card - Build the complete HTML string
            f2_html = f"""
<div class="fighter-card">
    <div class="fighter-name fighter-2-name">{fighter2}</div>
    <div class="movement-label">Odds Movement:</div>
    <div class="movement-value" style="color: {f2_color};">{f2_description}</div>
    <div class="section-title">Movement Timeline:</div>
    <div class="scrollable">
"""
            
            # Add movement timeline to the HTML string
            if selected_sportsbook != 'All' and f2_movements:
                for move in f2_movements:
                    f2_html += f"""
<div class="timeline-item">
    <div class="timestamp">{move['timestamp']}</div>
    <div class="description" style="color: {move['color']};">{move['description']}</div>
</div>
                    """
            elif selected_sportsbook == 'All':
                f2_html += '<div class="message">Select a specific sportsbook to see line movements</div>'
            else:
                f2_html += '<div class="message">No line movements recorded for this fighter</div>'
            
            # Close the HTML tags
            f2_html += '</div></div>'
            
            # Render complete HTML strings
            with fighter_cols[1]:
                st.markdown(f2_html, unsafe_allow_html=True)
            
            # Caption for chart
            st.caption("The chart shows American odds movement over time. Negative values (e.g., -150) indicate favorites, while positive values (e.g., +200) indicate underdogs.")
        else:
            st.warning("No odds data available for this selection.")
    with tabs[1]:
        st.header("Raw Data")
        st.write("March 22 Fight Data")
        st.dataframe(main_card_df)
if __name__ == "__main__":
    ufc_odds_dashboard()