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
    st.title("UFC Fight Night March 22 Odds Movement Dashboard")
    
    data = load_and_process_data()
    if data is None:
        return
    
    main_card_df, main_card_matchups = data
    
    # Create tabs for the dashboard
    tabs = st.tabs(["React Dashboard", "Odds Timeline", "Raw Data"])
    
    with tabs[0]:
        st.header("UFC Odds Movement React Dashboard")
        
        # Add controls outside of elements - using Streamlit native components
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_matchup = st.selectbox(
                "Select Fight", 
                main_card_matchups,
                key="react_matchup"
            )
        
        # Get unique sportsbooks for the selected matchup
        available_sportsbooks = ['All'] + list(main_card_df[main_card_df['matchup'] == selected_matchup]['sportsbook'].unique())
        
        with col2:
            selected_sportsbook = st.selectbox(
                "Select Sportsbook", 
                available_sportsbooks,
                key="react_sportsbook"
            )
            
        # Filter data based on selections
        filtered_df = main_card_df[main_card_df['matchup'] == selected_matchup].copy()
        if selected_sportsbook != 'All':
            filtered_df = filtered_df[filtered_df['sportsbook'] == selected_sportsbook].copy()
        
        # Sort by timestamp
        filtered_df = filtered_df.sort_values('timestamp')
        
        # Get unique sportsbooks for the selected matchup
        available_sportsbooks = ['All'] + list(main_card_df[main_card_df['matchup'] == selected_matchup]['sportsbook'].unique())
        
        # Create Plotly chart
        fig = create_odds_chart(filtered_df, selected_matchup)
        
        # Extract fighter names from selected matchup
        fighters = selected_matchup.split(' vs ')
        fighter1 = fighters[0].strip()
        fighter2 = fighters[1].strip() if len(fighters) > 1 else ""
        
        # Calculate movement for selected fighters
        if len(filtered_df) >= 2:
            first_record = filtered_df.iloc[0]
            last_record = filtered_df.iloc[-1]
            
            f1_description, f1_color = get_odds_shift_description(
                first_record['odds_before_f1'], 
                last_record['odds_after_f1']
            )
            
            f2_description, f2_color = get_odds_shift_description(
                first_record['odds_before_f2'], 
                last_record['odds_after_f2']
            )
            
            # Prepare line movement data for each fighter
            f1_movements = []
            f2_movements = []
            prev_f1_odds = first_record['odds_before_f1']
            prev_f2_odds = first_record['odds_before_f2']
            
            # Go through all sorted records to track line movements
            for _, row in filtered_df.iterrows():
                # Only process if we have valid odds
                if row['odds_after_f1'] and row['odds_after_f2']:
                    # For Fighter 1
                    if row['odds_after_f1'] != prev_f1_odds:
                        move_desc, move_color = get_odds_shift_description(prev_f1_odds, row['odds_after_f1'])
                        timestamp = row['timestamp'].strftime('%m/%d %H:%M') if row['timestamp'] else 'Unknown'
                        f1_movements.append({
                            'timestamp': timestamp,
                            'description': move_desc,
                            'color': move_color
                        })
                        prev_f1_odds = row['odds_after_f1']
                    
                    # For Fighter 2
                    if row['odds_after_f2'] != prev_f2_odds:
                        move_desc, move_color = get_odds_shift_description(prev_f2_odds, row['odds_after_f2'])
                        timestamp = row['timestamp'].strftime('%m/%d %H:%M') if row['timestamp'] else 'Unknown'
                        f2_movements.append({
                            'timestamp': timestamp,
                            'description': move_desc,
                            'color': move_color
                        })
                        prev_f2_odds = row['odds_after_f2']
        else:
            f1_description = "Insufficient data"
            f2_description = "Insufficient data"
            f1_color = "gray"
            f2_color = "gray"
            f1_movements = []
            f2_movements = []
        
        # Create reactive elements container for visualization only
        with elements("ufc_odds_dashboard"):
            # Define layout
            layout = [
                {"i": "header", "x": 0, "y": 0, "w": 12, "h": 2, "static": True},
                {"i": "chart", "x": 0, "y": 2, "w": 12, "h": 20, "static": True},
                {"i": "fighter1", "x": 0, "y": 22, "w": 6, "h": 7, "static": True},
                {"i": "fighter2", "x": 6, "y": 22, "w": 6, "h": 7, "static": True},
                {"i": "info", "x": 0, "y": 29, "w": 12, "h": 2, "static": True}
            ]
            
            # Create dashboard with material UI
            with dashboard.Grid(layout=layout, draggableHandle=".draggable", rowHeight=30, containerPadding=[10, 10]):
                # Header card - simplified, no dropdowns
                with mui.Card(key="header", sx={"height": "100%"}):
                    with mui.CardContent(sx={"height": "100%"}):
                        mui.Typography("UFC Fight Night March 22 Odds Movement", 
                                      variant="h5", 
                                      className="draggable", 
                                      sx={"mb": 1, "color": "white"})
                
                # Chart card
                with mui.Card(key="chart", sx={"height": "100%"}):
                    with mui.CardContent(sx={"height": "100%", "pt": 2, "pb": 2}):
                        mui.Typography("Odds Movement Timeline", 
                                      variant="h6", 
                                      className="draggable",
                                      sx={"color": "white", "mb": 1})
                        
                        if fig:
                            html_str = fig.to_html(full_html=False, include_plotlyjs='cdn')
                            with mui.Box(sx={"height": "90%", "overflow": "hidden"}):
                                html.Iframe(
                                    srcDoc=html_str,
                                    style={"width": "100%", "height": "100%", "border": "none", "minHeight": "450px"}
                                )
                        else:
                            mui.Typography("No data available for the selected fight and sportsbook.",
                                          sx={"color": "gray", "textAlign": "center", "mt": 10})
                
                # Fighter 1 stats card
                with mui.Card(key="fighter1", sx={"height": "100%"}):
                    with mui.CardContent:
                        mui.Typography(fighter1, 
                                      variant="h6", 
                                      className="draggable",
                                      sx={"color": "#ff8c00", "mb": 1})
                        
                        mui.Divider(sx={"mb": 2})
                        
                        mui.Typography("Odds Movement:", variant="subtitle2", sx={"color": "white"})
                        
                        mui.Typography(f1_description, 
                                      sx={"color": f1_color, "fontWeight": "bold", "mb": 2})
                        
                        # Show individual line movements if available
                        if selected_sportsbook != 'All' and f1_movements:
                            with mui.Box(sx={"mt": 1, "mb": 2, "maxHeight": 150, "overflow": "auto"}):
                                mui.Typography("Movement Timeline:", variant="subtitle2", sx={"color": "white", "mb": 1})
                                for move in f1_movements:
                                    with mui.Box(sx={"display": "flex", "alignItems": "center", "mb": 1}):
                                        mui.Typography(
                                            move['timestamp'],
                                            variant="caption",
                                            sx={"minWidth": 65, "color": "lightgray"}
                                        )
                                        mui.Typography(
                                            move['description'],
                                            variant="body2",
                                            sx={"color": move['color']}
                                        )
                        elif selected_sportsbook == 'All':
                            mui.Typography(
                                "Select a specific sportsbook to see line movements",
                                variant="body2",
                                sx={"color": "gray", "fontStyle": "italic", "mt": 1}
                            )
                        else:
                            mui.Typography(
                                "No line movements recorded for this fighter",
                                variant="body2",
                                sx={"color": "gray", "fontStyle": "italic", "mt": 1}
                            )
                
                # Fighter 2 stats card
                with mui.Card(key="fighter2", sx={"height": "100%"}):
                    with mui.CardContent:
                        mui.Typography(fighter2, 
                                      variant="h6", 
                                      className="draggable",
                                      sx={"color": "#00bfff", "mb": 1})
                        
                        mui.Divider(sx={"mb": 2})
                        
                        mui.Typography("Odds Movement:", variant="subtitle2", sx={"color": "white"})
                        
                        mui.Typography(f2_description, 
                                      sx={"color": f2_color, "fontWeight": "bold", "mb": 2})
                        
                        # Show individual line movements if available
                        if selected_sportsbook != 'All' and f2_movements:
                            with mui.Box(sx={"mt": 1, "mb": 2, "maxHeight": 150, "overflow": "auto"}):
                                mui.Typography("Movement Timeline:", variant="subtitle2", sx={"color": "white", "mb": 1})
                                for move in f2_movements:
                                    with mui.Box(sx={"display": "flex", "alignItems": "center", "mb": 1}):
                                        mui.Typography(
                                            move['timestamp'],
                                            variant="caption",
                                            sx={"minWidth": 65, "color": "lightgray"}
                                        )
                                        mui.Typography(
                                            move['description'],
                                            variant="body2",
                                            sx={"color": move['color']}
                                        )
                        elif selected_sportsbook == 'All':
                            mui.Typography(
                                "Select a specific sportsbook to see line movements",
                                variant="body2",
                                sx={"color": "gray", "fontStyle": "italic", "mt": 1}
                            )
                        else:
                            mui.Typography(
                                "No line movements recorded for this fighter",
                                variant="body2",
                                sx={"color": "gray", "fontStyle": "italic", "mt": 1}
                            )
                
                # Info footer card
                with mui.Card(key="info", sx={"height": "100%"}):
                    with mui.CardContent(sx={"display": "flex", "justifyContent": "space-between"}):
                        mui.Typography("Developed by Tyler Durette | MMA AI © 2025", 
                                      variant="body2", 
                                      sx={"color": "gray"})
                        
                        mui.Typography("Data source: UFC Odds Movements", 
                                      variant="body2", 
                                      sx={"color": "gray"})

    with tabs[1]:
        st.header("Odds Movement Timeline")
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_matchup = st.selectbox("Select Fight", main_card_matchups)
        available_sportsbooks = ['All'] + list(main_card_df[main_card_df['matchup'] == selected_matchup]['sportsbook'].unique())
        with col2:
            selected_sportsbook = st.selectbox("Select Sportsbook", available_sportsbooks)
        filtered_df = main_card_df[main_card_df['matchup'] == selected_matchup]
        if selected_sportsbook != 'All':
            filtered_df = filtered_df[filtered_df['sportsbook'] == selected_sportsbook]
        filtered_df = filtered_df.sort_values('timestamp')
        fig = create_odds_chart(filtered_df, selected_matchup)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            st.caption("The chart shows American odds movement over time. Negative values (e.g., -150) indicate favorites, while positive values (e.g., +200) indicate underdogs.")
        else:
            st.warning("No odds data available for this selection.")
    with tabs[2]:
        st.header("Raw Data")
        st.write("March 22 Fight Data")
        st.dataframe(main_card_df)
if __name__ == "__main__":
    ufc_odds_dashboard()