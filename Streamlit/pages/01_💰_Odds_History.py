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

def get_odds_shift_description(start_odds, end_odds):
    if not start_odds or not end_odds:
        return "No data", "gray"
    try:
        # Note: odds are now numeric values, not strings
        start_val = start_odds
        end_val = end_odds
        
        # Format for display (add + for positive values)
        start_display = f"+{start_val}" if start_val > 0 else str(start_val)
        end_display = f"+{end_val}" if end_val > 0 else str(end_val)
        
        if start_val < 0:  # Fighter was favorite
            if end_val < 0:  # Still favorite
                if end_val > start_val:  # e.g., -200 to -180
                    return f"↓ Weaker Favorite ({start_display} → {end_display})", "red"
                elif end_val < start_val:  # e.g., -180 to -200
                    return f"↑ Stronger Favorite ({start_display} → {end_display})", "green"
                else:
                    return f"No Change ({start_display} → {end_display})", "gray"
            else:  # Changed to underdog
                return f"↔ Changed to Underdog ({start_display} → {end_display})", "orange"
        elif start_val > 0:  # Fighter was underdog
            if end_val > 0:  # Still underdog
                if end_val > start_val:  # e.g., +180 to +200
                    return f"↑ Bigger Underdog ({start_display} → {end_display})", "red"
                elif end_val < start_val:  # e.g., +200 to +180
                    return f"↓ Smaller Underdog ({start_display} → {end_display})", "green"
                else:
                    return f"No Change ({start_display} → {end_display})", "gray"
            else:  # Changed to favorite
                return f"↔ Changed to Favorite ({start_display} → {end_display})", "orange"
    except:
        return "Invalid odds format", "gray"
    return "No change", "gray"

def load_and_process_data(matchups_to_display=None):
    # Clear existing session state to force reload with new filters
    if 'df_odds_movements' in st.session_state:
        del st.session_state['df_odds_movements']
        
    if 'df_odds_movements' not in st.session_state:
        try:
            df = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                          'data/ufc_odds_movements_fightoddsio.csv'))
            
            # Exclude unwanted sportsbooks
            excluded_books = ['4casters', 'cloudbet', 'jazz-sports', 'espn-bet', 'betway', 'betrivers', 'sx-bet', 'bet105', 'betanysports']
            df = df[~df['sportsbook'].isin(excluded_books)]
            
            st.session_state['df_odds_movements'] = df
        except Exception as e:
            st.error(f"Error loading odds movement data: {e}")
            st.info("Please ensure 'ufc_odds_movements_fightoddsio.csv' is in the data directory.")
            return None
    
    df = st.session_state['df_odds_movements']
    
    # Extract timestamps from filenames
    df.loc[:, 'timestamp'] = df['file2'].apply(extract_timestamp)
    
    # Use default matchups if none provided
    if not matchups_to_display:
        matchups_to_display = [
            "Steve Erceg vs Brandon Moreno",
            "Drew Dober vs Manuel Torres",
            "Joe Pyfer vs Kelvin Gastelum",
            "Vince Morales vs Raul Rosas Jr.",
            "Saimon Oliveira vs David Martinez",
            "Kevin Borjas vs Ronaldo Rodriguez",
            "CJ Vergara vs Edgar Chairez",
            "Ateba Gautier vs Jose Daniel Medina",
            "Melquizael Costa vs Christian Rodriguez",
            "Julia Polastri vs Lupita Godinez",
            "Vinc Pichel vs Rafa Garcia",
            "Gabriel Miranda vs Jamall Emmers",
            "Austin Hubbard vs Marquel Mederos"
        ]
    
    # Filter fighters based on matchups
    all_fighters = set()
    for matchup in matchups_to_display:
        fighters = [f.strip() for f in matchup.split(' vs ')]
        all_fighters.update(fighters)
    
    # Filter dataframe for these fighters (case-insensitive)
    filtered_df = df[df['fighter'].str.lower().isin([f.lower() for f in all_fighters])]
    
    if len(filtered_df) == 0:
        st.warning("No fighters found. Please check the fighter names.")
        return None
    
    return filtered_df, matchups_to_display

def create_odds_chart(filtered_df, selected_matchup):
    if filtered_df.empty:
        return None
    
    # Extract fighter names from the matchup
    fighters = selected_matchup.split(' vs ')
    fighter1 = fighters[0].strip()
    fighter2 = fighters[1].strip() if len(fighters) > 1 else ""
    
    # Filter data for the selected fighters
    f1_data = filtered_df[filtered_df['fighter'] == fighter1]
    f2_data = filtered_df[filtered_df['fighter'] == fighter2]
    
    # Get unique sportsbooks
    sportsbooks = list(set(f1_data['sportsbook'].unique().tolist() + f2_data['sportsbook'].unique().tolist()))
    
    fig = go.Figure()
    
    # Color maps for each sportsbook
    colors_f1 = ['#ff8c00', '#ff4500', '#ffa500', '#ff6347', '#ff7f50']  # Orange shades
    colors_f2 = ['#00bfff', '#1e90ff', '#87ceeb', '#4169e1', '#0000ff']  # Blue shades
    
    # Add lines for each sportsbook
    for idx, sportsbook in enumerate(sportsbooks):
        # Fighter 1
        book_f1_data = f1_data[f1_data['sportsbook'] == sportsbook]
        if not book_f1_data.empty:
            try:
                fig.add_trace(go.Scatter(
                    x=book_f1_data['timestamp'],
                    y=book_f1_data['odds_after'],
                    mode='lines+markers',
                    name=f"{fighter1} ({sportsbook})",
                    line=dict(color=colors_f1[idx % len(colors_f1)]),
                    marker=dict(size=8),
                    text=[f"+{odds}" if odds > 0 else str(odds) for odds in book_f1_data['odds_after']],
                    hovertemplate='%{text}<br>%{x}<br>%{text}<extra></extra>'
                ))
            except:
                continue
                
        # Fighter 2
        book_f2_data = f2_data[f2_data['sportsbook'] == sportsbook]
        if not book_f2_data.empty:
            try:
                fig.add_trace(go.Scatter(
                    x=book_f2_data['timestamp'],
                    y=book_f2_data['odds_after'],
                    mode='lines+markers',
                    name=f"{fighter2} ({sportsbook})",
                    line=dict(color=colors_f2[idx % len(colors_f2)]),
                    marker=dict(size=8),
                    text=[f"+{odds}" if odds > 0 else str(odds) for odds in book_f2_data['odds_after']],
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
            # title=f"  {selected_matchup}",
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

def ufc_odds_dashboard():
    st.title("Odds Tracking & Movement Dashboard")
    
    # Define the matchups you want to display
    matchups_to_display = [
        "Steve Erceg vs Brandon Moreno",
        "Drew Dober vs Manuel Torres",
        "Joseph Pyfer vs Kelvin Gastelum",
        "Vince Morales vs Raul Rosas Jr.",
        "David Martinez vs Saimon Oliveira",  # Fighters reversed from original order
        "Luis Rodríguez vs Kevin Borjas",  # "Luis" not "Ronaldo"
        "Edgar Chairez vs Carlos Vergara",  # "Carlos" not "CJ"
        "Ateba Abega Gautier vs José Daniel Medina",  # Full name with accents
        "Christian Rodriguez vs Melquizael Costa",
        "Lupita Godinez vs Julia Polastri",  # "Lupita" not "Loopy"
        "Rafa Garcia vs Vinc Pichel",
        "Jamall Emmers vs Gabriel Miranda",
        "Marquel Mederos vs Austin Hubbard"  # Regular "q" not "Q", names reversed
    ]
    #     "Saimon Oliveira vs David Martinez",
    #     "Kevin Borjas vs Ronaldo Rodriguez",
    #     "CJ Vergara vs Edgar Chairez",
    #     "Ateba Gautier vs Jose Daniel Medina",
    #     "Melquizael Costa vs Christian Rodriguez",
    #     "Julia Polastri vs Lupita Godinez",
    #     "Vinc Pichel vs Rafa Garcia",
    #     "Gabriel Miranda vs Jamall Emmers",
    #     "Austin Hubbard vs Marquel Mederos"
    # ]
        
    data = load_and_process_data(matchups_to_display)
    if data is None:
        return
    
    filtered_df, available_matchups = data
    
    # Create tabs for the dashboard
    tabs = st.tabs(["Odds Timeline", "Raw Data"])
    
    with tabs[0]:
        st.header("UFC Fight Night - Moreno vs. Erceg - Mexico City")
        
        # Controls - same as React dashboard
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_matchup = st.selectbox("Select Fight", available_matchups, key="timeline_matchup")
        
        # Extract fighter names from the matchup
        fighters = selected_matchup.split(' vs ')
        fighter1 = fighters[0].strip()
        fighter2 = fighters[1].strip() if len(fighters) > 1 else ""
        
        # Get available sportsbooks for these fighters
        f1_data = filtered_df[filtered_df['fighter'] == fighter1]
        f2_data = filtered_df[filtered_df['fighter'] == fighter2]
        
        all_sportsbooks = set(f1_data['sportsbook'].unique().tolist() + f2_data['sportsbook'].unique().tolist())
        
        # Put Circa first if available, then others, then All
        available_sportsbooks = []
        if 'Circa' in all_sportsbooks:
            available_sportsbooks.append('Circa')
            all_sportsbooks.remove('Circa')
        
        available_sportsbooks.extend(sorted(all_sportsbooks))
        available_sportsbooks.append('All')
        
        with col2:
            selected_sportsbook = st.selectbox(
                "Select Sportsbook", 
                available_sportsbooks,
                key="timeline_sportsbook"
            )
        
        # Filter data based on selected fighters
        f1_data = filtered_df[filtered_df['fighter'] == fighter1].copy()
        f2_data = filtered_df[filtered_df['fighter'] == fighter2].copy()
        
        # Further filter by sportsbook if not 'All'
        if selected_sportsbook != 'All':
            f1_data = f1_data[f1_data['sportsbook'] == selected_sportsbook].copy()
            f2_data = f2_data[f2_data['sportsbook'] == selected_sportsbook].copy()
        
        # Sort by timestamp
        f1_data = f1_data.sort_values('timestamp')
        f2_data = f2_data.sort_values('timestamp')
        
        # Create Plotly chart
        matchup_df = pd.concat([f1_data, f2_data])
        fig = create_odds_chart(matchup_df, selected_matchup)
        
        # Calculate movement for both fighters
        def calculate_fighter_movements(fighter_data):
            if len(fighter_data) < 2:
                return [], None, None, "Insufficient data", "gray"
                
            # Group by sportsbook to track movements
            movements = []
            
            # Track first and last valid odds for overall movement
            first_odds = None
            last_odds = None
            
            # Process each sportsbook separately
            for sportsbook, group in fighter_data.groupby('sportsbook'):
                # Sort by timestamp
                group = group.sort_values('timestamp')
                
                # Update first/last odds
                if first_odds is None and not group.empty:
                    first_odds = group['odds_after'].iloc[0]
                
                if not group.empty:
                    last_odds = group['odds_after'].iloc[-1]
                
                # Track movements within this sportsbook
                prev_odds = None
                for _, row in group.iterrows():
                    if prev_odds is not None and row['odds_after'] != prev_odds:
                        move_desc, move_color = get_odds_shift_description(prev_odds, row['odds_after'])
                        timestamp = row['timestamp'].strftime('%m/%d %H:%M') if row['timestamp'] else 'Unknown'
                        movements.append({
                            'timestamp': timestamp,
                            'sportsbook': sportsbook,
                            'description': move_desc,
                            'color': move_color
                        })
                    prev_odds = row['odds_after']
            
            # Calculate overall movement
            if first_odds is not None and last_odds is not None:
                overall_desc, overall_color = get_odds_shift_description(first_odds, last_odds)
            else:
                overall_desc, overall_color = "No data", "gray"
                
            return movements, first_odds, last_odds, overall_desc, overall_color
        
        # Calculate movements for both fighters
        f1_movements, f1_first, f1_last, f1_description, f1_color = calculate_fighter_movements(f1_data)
        f2_movements, f2_first, f2_last, f2_description, f2_color = calculate_fighter_movements(f2_data)
        
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
            .sportsbook {
                min-width: 80px;
                font-size: 13px;
                color: #cccccc;
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
            
            # Fighter 1 card
            f1_html = f"""<div class="fighter-card">
<div class="fighter-name fighter-1-name">{fighter1}</div>
<div class="movement-label">Odds Movement:</div>
<div class="movement-value" style="color: {f1_color};">{f1_description}</div>
<div class="section-title">Movement Timeline:</div>
<div class="scrollable">"""
            
            # Add movement timeline
            if selected_sportsbook != 'All' and f1_movements:
                for move in f1_movements:
                    f1_html += f"""<div class="timeline-item">
<div class="timestamp">{move['timestamp']}</div>
<div class="description" style="color: {move['color']};">{move['description']}</div>
</div>"""
            elif selected_sportsbook == 'All' and f1_movements:
                for move in f1_movements:
                    f1_html += f"""<div class="timeline-item">
<div class="timestamp">{move['timestamp']}</div>
<div class="sportsbook">{move['sportsbook']}</div>
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
            
            # Fighter 2 card
            f2_html = f"""<div class="fighter-card">
<div class="fighter-name fighter-2-name">{fighter2}</div>
<div class="movement-label">Odds Movement:</div>
<div class="movement-value" style="color: {f2_color};">{f2_description}</div>
<div class="section-title">Movement Timeline:</div>
<div class="scrollable">"""
            
            # Add movement timeline
            if selected_sportsbook != 'All' and f2_movements:
                for move in f2_movements:
                    f2_html += f"""<div class="timeline-item">
<div class="timestamp">{move['timestamp']}</div>
<div class="description" style="color: {move['color']};">{move['description']}</div>
</div>"""
            elif selected_sportsbook == 'All' and f2_movements:
                for move in f2_movements:
                    f2_html += f"""<div class="timeline-item">
<div class="timestamp">{move['timestamp']}</div>
<div class="sportsbook">{move['sportsbook']}</div>
<div class="description" style="color: {move['color']};">{move['description']}</div>
</div>"""
            elif selected_sportsbook == 'All':
                f2_html += '<div class="message">Select a specific sportsbook to see line movements</div>'
            else:
                f2_html += '<div class="message">No line movements recorded for this fighter</div>'
            
            f2_html += '</div></div>'
            
            # Render complete HTML string
            with fighter_cols[1]:
                st.markdown(f2_html, unsafe_allow_html=True)
            
        else:
            st.warning("No odds data available for this selection.")
    
    with tabs[1]:
        st.header("Raw Data")
        st.write("Fighter Odds Data")
        st.dataframe(filtered_df)

if __name__ == "__main__":
    ufc_odds_dashboard()