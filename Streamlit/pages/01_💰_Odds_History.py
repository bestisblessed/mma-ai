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
def load_and_process_data(matchups_to_display=None):
    if 'df_odds_movements' not in st.session_state:
        try:
            df = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data/ufc_odds_movements.csv'))
            st.session_state['df_odds_movements'] = df
        except Exception as e:
            st.error(f"Error loading odds movement data: {e}")
            st.info("Please ensure 'ufc_odds_movements.csv' is in the data directory.")
            return None
    
    df = st.session_state['df_odds_movements']
    
    # Use default matchups if none provided
    if not matchups_to_display:
        matchups_to_display = [
            "Steve Erceg vs  Brandon Moreno",
            "Drew Dober vs  Manuel Torres",
            "Joe Pyfer vs  Kelvin Gastelum",
            "Vince Morales vs  Raul Rosas Jr.",
            "Saimon Oliveira vs  David Martinez",
            "Kevin Borjas vs  Ronaldo Rodriguez",
            "CJ Vergara vs  Edgar Chairez",
            "Ateba Gautier vs  Jose Medina",
            "Melquizael Costa vs  Christian Rodriguez",
            "Julia Polastri vs  Loopy Godinez",
            "Vinc Pichel vs  Rafa Garcia",
            "Gabriel Miranda vs  Jamall Emmers",
            "Austin Hubbard vs  Marquel Mederos"
        ]
    
    # Filter dataframe by matchups instead of by date
    filtered_df = df[df['matchup'].isin(matchups_to_display)]
    
    # If none found, try case-insensitive matching
    if len(filtered_df) == 0:
        filtered_df = df[df['matchup'].str.lower().isin([m.lower() for m in matchups_to_display])]
        if len(filtered_df) == 0:
            st.warning("No matchups found. Please check the matchup names.")
            return None
    
    # Create a copy to avoid SettingWithCopyWarning
    filtered_df = filtered_df.copy()
    
    # Process the data as before
    filtered_df.loc[:, 'timestamp'] = filtered_df['file2'].apply(extract_timestamp)
    filtered_df.loc[:, ['odds_before_f1', 'odds_before_f2']] = filtered_df['odds_before'].apply(parse_odds).tolist()
    filtered_df.loc[:, ['odds_after_f1', 'odds_after_f2']] = filtered_df['odds_after'].apply(parse_odds).tolist()
    
    return filtered_df, matchups_to_display
def create_odds_chart(filtered_df, selected_matchup):
    if filtered_df.empty:
        return None
    fighters = selected_matchup.split(' vs ')
    fighter1 = fighters[0].strip()
    fighter2 = fighters[1].strip() if len(fighters) > 1 else ""
    
    # Get unique sportsbooks
    sportsbooks = filtered_df['sportsbook'].unique()
    
    fig = go.Figure()
    
    # Color maps for each sportsbook
    colors_f1 = ['#ff8c00', '#ff4500', '#ffa500', '#ff6347', '#ff7f50']  # Orange shades
    colors_f2 = ['#00bfff', '#1e90ff', '#87ceeb', '#4169e1', '#0000ff']  # Blue shades
    
    # Add lines for each sportsbook
    for idx, sportsbook in enumerate(sportsbooks):
        book_data = filtered_df[filtered_df['sportsbook'] == sportsbook]
        
        # Skip this sportsbook if either fighter has no valid odds
        if book_data['odds_after_f1'].isna().all() or book_data['odds_after_f2'].isna().all():
            continue
            
        # Filter out rows where either fighter has no odds
        book_data = book_data.dropna(subset=['odds_after_f1', 'odds_after_f2'])
        
        if len(book_data) == 0:
            continue
            
        # Fighter 1
        try:
            fig.add_trace(go.Scatter(
                x=book_data['timestamp'],
                y=book_data['odds_after_f1'].str.replace('+', '').astype(int),
                mode='lines+markers',
                name=f"{fighter1} ({sportsbook})",
                line=dict(color=colors_f1[idx % len(colors_f1)]),
                marker=dict(size=8),
                text=book_data['odds_after_f1'],
                hovertemplate='%{text}<br>%{x}<br>%{text}<extra></extra>'
            ))
            
            # Fighter 2
            fig.add_trace(go.Scatter(
                x=book_data['timestamp'],
                y=book_data['odds_after_f2'].str.replace('+', '').astype(int),
                mode='lines+markers',
                name=f"{fighter2} ({sportsbook})",
                line=dict(color=colors_f2[idx % len(colors_f2)]),
                marker=dict(size=8),
                text=book_data['odds_after_f2'],
                hovertemplate='%{text}<br>%{x}<br>%{text}<extra></extra>'
            ))
        except:
            continue
    
    # If no valid data was plotted, return None
    if not fig.data:
        return None
        
    # Calculate dynamic y-axis range only for valid odds
    valid_odds = []
    for trace in fig.data:
        valid_odds.extend(trace.y)
    
    if valid_odds:
        y_min = min(valid_odds) - 50
        y_max = max(valid_odds) + 50
        
        fig.add_shape(
            type="line",
            x0=filtered_df['timestamp'].min(),
            y0=0,
            x1=filtered_df['timestamp'].max(),
            y1=0,
            line=dict(color="gray", width=1, dash="dash"),
        )
        
        fig.update_layout(
            title=f"Odds Movement: {selected_matchup} (All Sportsbooks)",
            xaxis_title="Time",
            yaxis_title="American Odds",
            yaxis=dict(range=[y_min, y_max]),
            legend_title="Fighter & Sportsbook",
            hovermode="closest",
            height=600,
            margin=dict(l=50, r=50, t=50, b=50),
            template="plotly_dark",
            plot_bgcolor='rgba(30,30,30,1)',
            paper_bgcolor='rgba(30,30,30,1)',
            font=dict(color='white')
        )
        return fig
    return None
def get_odds_shift_description(start_odds, end_odds):
    if not start_odds or not end_odds:
        return "No data", "gray"
    try:
        start_val = int(start_odds.replace('+', ''))
        end_val = int(end_odds.replace('+', ''))
        if start_odds.startswith('-'):
            if end_odds.startswith('-'):
                if end_val > start_val:  
                    return f"↓ Weaker Favorite ({start_odds} → {end_odds})", "red"
                elif end_val < start_val:  
                    return f"↑ Stronger Favorite ({start_odds} → {end_odds})", "green"
                else:
                    return f"No Change ({start_odds} → {end_odds})", "gray"
            else:  
                return f"↔ Changed to Underdog ({start_odds} → {end_odds})", "orange"
        elif start_odds.startswith('+'):
            if end_odds.startswith('+'):
                if end_val > start_val:  
                    return f"↑ Bigger Underdog ({start_odds} → {end_odds})", "red"
                elif end_val < start_val:  
                    return f"↓ Smaller Underdog ({start_odds} → {end_odds})", "green"
                else:
                    return f"No Change ({start_odds} → {end_odds})", "gray"
            else:  
                return f"↔ Changed to Favorite ({start_odds} → {end_odds})", "orange"
    except:
        return "Invalid odds format", "gray"
    return "No change", "gray"
def ufc_odds_dashboard():
    st.title("Odds Tracking & Movement Dashboard")
    
    # Define the matchups you want to display
    matchups_to_display = [
        "Steve Erceg vs  Brandon Moreno",
        "Drew Dober vs  Manuel Torres",
        "Joe Pyfer vs  Kelvin Gastelum",
        "Vince Morales vs  Raul Rosas Jr",
        "Saimon Oliveira vs  David Martinez",
        "Kevin Borjas vs  Ronaldo Rodriguez",
        "CJ Vergara vs  Edgar Chairez",
        "Ateba Gautier vs  Jose Daniel Medina",
        "Melquizael Costa vs  Christian Rodriguez",
        "Julia Polastri vs  Lupita Godinez",
        "Vinc Pichel vs  Rafa Garcia",
        "Gabriel Miranda vs  Jamall Emmers",
        "Austin Hubbard vs  Marquel Mederos"
    ]
        
    data = load_and_process_data(matchups_to_display)
    if data is None:
        return
    
    filtered_df, available_matchups = data
    
    # Create tabs for the dashboard
    tabs = st.tabs(["Odds Timeline", "Raw Data"])
    
    with tabs[0]:
        st.header("UFC Fight Night 255 - Edwards vs. Brady")
        
        # Controls - same as React dashboard
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_matchup = st.selectbox("Select Fight", available_matchups, key="timeline_matchup")
        
        available_sportsbooks = ['Circa'] + [sb for sb in filtered_df[filtered_df['matchup'] == selected_matchup]['sportsbook'].unique() if sb != 'Circa'] + ['All']
        with col2:
            selected_sportsbook = st.selectbox(
                "Select Sportsbook", 
                available_sportsbooks,
                key="timeline_sportsbook"
            )
        
        # Filter data based on selections - same as React dashboard
        filtered_df = filtered_df[filtered_df['matchup'] == selected_matchup].copy()
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
            # st.caption("The chart shows American odds movement over time. Negative values (e.g., -150) indicate favorites, while positive values (e.g., +200) indicate underdogs.")
        else:
            st.warning("No odds data available for this selection.")
    with tabs[1]:
        st.header("Raw Data")
        st.write("March 22 Fight Data")
        st.dataframe(filtered_df)
if __name__ == "__main__":
    ufc_odds_dashboard()