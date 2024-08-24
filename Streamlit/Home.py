import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_lottie import st_lottie
from PIL import Image
import plotly.express as px
from datetime import datetime
from openai import OpenAI
import time

st.set_page_config(page_title="MMA AI", page_icon="🥊", layout="wide")

# ---- Titles ---- #
st.title('MMA AI')
st.write('Welcome to MMA AI. Time to fucking win.')
st.divider()

import os
st.write("Current working directory:", os.getcwd())
st.write("Files in current directory:", os.listdir(os.getcwd()))

# ---- Loading Data ---- #
# df_event_data = pd.read_csv('Streamlit/data/event_data_sherdog.csv')
# df_fighter_data = pd.read_csv('Streamlit/data/fighter_info.csv')
# Streamlit/Streamlit/
base_dir = os.path.dirname(os.path.abspath(__file__))  # This gives you the directory where the script is located
df_event_data = pd.read_csv(os.path.join(base_dir, 'Streamlit/data/event_data_sherdog.csv'))
df_fighter_data = pd.read_csv(os.path.join(base_dir, 'Streamlit/data/fighter_info.csv'))
dataframes = [df_event_data, df_fighter_data]
st.session_state['df_event_data'] = df_event_data
st.session_state['df_fighter_data'] = df_fighter_data


# ---- Loading Data from GitHub URLs ---- #
# event_data_url = 'https://raw.githubusercontent.com/bestisblessed/mma-ai/main/Streamlit/Streamlit/data/event_data_sherdog.csv'
# fighter_data_url = 'https://raw.githubusercontent.com/bestisblessed/mma-ai/main/Streamlit/Streamlit/data/fighter_info.csv'
# df_event_data = pd.read_csv(event_data_url)
# df_fighter_data = pd.read_csv(fighter_data_url)
# st.session_state['df_event_data'] = df_event_data
# st.session_state['df_fighter_data'] = df_fighter_data

# Convert all text data to lowercase
df_event_data = df_event_data.map(lambda x: x.lower() if isinstance(x, str) else x)
df_fighter_data = df_fighter_data.map(lambda x: x.lower() if isinstance(x, str) else x)

# ---- Fighter Selection ---- #
st.subheader('Select Fighters to Research & Predict')
fighter_names = df_fighter_data['Fighter'].unique()
col1, col2 = st.columns(2)
with col1:
    fighter1 = st.selectbox('Fighter 1', fighter_names, index=list(fighter_names).index("conor mcgregor"))
with col2:
    fighter2 = st.selectbox('Fighter 2', fighter_names, index=list(fighter_names).index("michael chandler"))
st.divider()

if fighter1 and fighter2:
    if fighter1 == fighter2:
        st.warning("Please select two different fighters.")
    else:
        fighter1_data = df_fighter_data[df_fighter_data['Fighter'] == fighter1]
        fighter2_data = df_fighter_data[df_fighter_data['Fighter'] == fighter2]

        # Extract and format the name with nickname
        fighter1_full_name = fighter1_data['Fighter'].values[0]
        fighter1_nickname = fighter1_data['Nickname'].values[0]
        fighter1_first_name = fighter1_full_name.split()[0]
        fighter1_last_name = " ".join(fighter1_full_name.split()[1:])
        fighter1_formatted_name = f"{fighter1_first_name} '{fighter1_nickname}' {fighter1_last_name}"
        fighter2_full_name = fighter2_data['Fighter'].values[0]
        fighter2_nickname = fighter2_data['Nickname'].values[0]
        fighter2_first_name = fighter2_full_name.split()[0]
        fighter2_last_name = " ".join(fighter2_full_name.split()[1:])
        fighter2_formatted_name = f"{fighter2_first_name} '{fighter2_nickname}' {fighter2_last_name}"

        # Calculate Fighter 1 and 2 win/loss streak
        fighter1_fights = df_event_data[(df_event_data['Fighter 1'] == fighter1) | (df_event_data['Fighter 2'] == fighter1)]
        fighter1_fights = fighter1_fights.sort_values(by='Event Date', ascending=False)
        streak_type1 = None
        streak_count1 = 0
        for _, row in fighter1_fights.iterrows():
            if row['Winning Fighter'] == fighter1:
                if streak_type1 == 'W' or streak_type1 is None:
                    streak_type1 = 'W'
                    streak_count1 += 1
                else:
                    break
            else:
                if streak_type1 == 'L' or streak_type1 is None:
                    streak_type1 = 'L'
                    streak_count1 += 1
                else:
                    break
        fighter1_streak = f"{streak_count1}{streak_type1}" if streak_type1 else "No Streak"
        fighter2_fights = df_event_data[(df_event_data['Fighter 1'] == fighter2) | (df_event_data['Fighter 2'] == fighter2)]
        fighter2_fights = fighter2_fights.sort_values(by='Event Date', ascending=False)
        streak_type2 = None
        streak_count2 = 0
        for _, row in fighter2_fights.iterrows():
            if row['Winning Fighter'] == fighter2:
                if streak_type2 == 'W' or streak_type2 is None:
                    streak_type2 = 'W'
                    streak_count2 += 1
                else:
                    break
            else:
                if streak_type2 == 'L' or streak_type2 is None:
                    streak_type2 = 'L'
                    streak_count2 += 1
                else:
                    break
        fighter2_streak = f"{streak_count2}{streak_type2}" if streak_type2 else "No Streak"

        col1, col2 = st.columns(2)
        with col1:
            # st.write(f"### {fighter1_formatted_name}")
            st.write(f"### '{fighter1_nickname}' {fighter1}")
            st.markdown(f"""
            - **Nickname**: {fighter1_data['Nickname'].values[0]}
            - **Birth Date**: {fighter1_data['Birth Date'].values[0]}
            - **Nationality**: {fighter1_data['Nationality'].values[0]}
            - **Association**: {fighter1_data['Association'].values[0]}
            - **Weight Class**: {fighter1_data['Weight Class'].values[0]}
            - **Height**: {fighter1_data['Height'].values[0]}
            - **Wins**: {fighter1_data['Wins'].values[0]}
            - **Losses**: {fighter1_data['Losses'].values[0]}
            - **Wins by Decision**: {fighter1_data['Win_Decision'].values[0]}
            - **Wins by KO**: {fighter1_data['Win_KO'].values[0]}
            - **Wins by Submission**: {fighter1_data['Win_Sub'].values[0]}
            - **Losses by Decision**: {fighter1_data['Loss_Decision'].values[0]}
            - **Losses by KO**: {fighter1_data['Loss_KO'].values[0]}
            - **Losses by Submission**: {fighter1_data['Loss_Sub'].values[0]}
            - **Fighter ID**: {fighter1_data['Fighter_ID'].values[0]}
            - **Current Streak**: {fighter1_streak}
            """)
            # Most Recent 5 Fights for Fighter 1
            st.markdown("<h5 style='text-align: center; color: grey;'>Most Recent 5 Fights</h5>", unsafe_allow_html=True)
            fighter1_fights = df_event_data[(df_event_data['Fighter 1'] == fighter1) | (df_event_data['Fighter 2'] == fighter1)]
            fighter1_fights = fighter1_fights.sort_values(by='Event Date', ascending=False).head(5)
            fighter1_styled = fighter1_fights[['Event Name', 'Event Date', 'Fighter 1', 'Fighter 2', 'Winning Fighter', 'Winning Method', 'Winning Round']].style.apply(
                lambda row: ['background-color: lightgreen' if row['Winning Fighter'] == fighter1 else 'background-color: lightcoral'] * len(row),
                axis=1
            )
            st.dataframe(fighter1_styled)
            # Fighter 1 Pie Chart
            labels1 = ['KO', 'Submission', 'Decision']
            values1 = [fighter1_data['Win_KO'].values[0], fighter1_data['Win_Sub'].values[0], fighter1_data['Win_Decision'].values[0]]
            fig1 = px.pie(values=values1, names=labels1, title=f"{fighter1} Winning Methods")
            st.plotly_chart(fig1, theme="streamlit")

        with col2:
            st.write(f"### '{fighter2_nickname}' {fighter2}")
            st.markdown(f"""
            - **Nickname**: {fighter2_data['Nickname'].values[0]}
            - **Birth Date**: {fighter2_data['Birth Date'].values[0]}
            - **Nationality**: {fighter2_data['Nationality'].values[0]}
            - **Association**: {fighter2_data['Association'].values[0]}
            - **Weight Class**: {fighter2_data['Weight Class'].values[0]}
            - **Height**: {fighter2_data['Height'].values[0]}
            - **Wins**: {fighter2_data['Wins'].values[0]}
            - **Losses**: {fighter2_data['Losses'].values[0]}
            - **Wins by Decision**: {fighter2_data['Win_Decision'].values[0]}
            - **Wins by KO**: {fighter2_data['Win_KO'].values[0]}
            - **Wins by Submission**: {fighter2_data['Win_Sub'].values[0]}
            - **Losses by Decision**: {fighter2_data['Loss_Decision'].values[0]}
            - **Losses by KO**: {fighter2_data['Loss_KO'].values[0]}
            - **Losses by Submission**: {fighter2_data['Loss_Sub'].values[0]}
            - **Fighter ID**: {fighter2_data['Fighter_ID'].values[0]}
            - **Current Streak**: {fighter2_streak}
            """)
            # Most Recent 5 Fights for Fighter 2
            st.markdown("<h5 style='text-align: center; color: grey;'>Most Recent 5 Fights</h5>", unsafe_allow_html=True)
            fighter2_fights = df_event_data[(df_event_data['Fighter 1'] == fighter2) | (df_event_data['Fighter 2'] == fighter2)]
            fighter2_fights = fighter2_fights.sort_values(by='Event Date', ascending=False).head(5)
            fighter2_styled = fighter2_fights[['Event Name', 'Event Date', 'Fighter 1', 'Fighter 2', 'Winning Fighter', 'Winning Method', 'Winning Round']].style.apply(
                lambda row: ['background-color: lightgreen' if row['Winning Fighter'] == fighter2 else 'background-color: lightcoral'] * len(row),
                axis=1
            )
            st.dataframe(fighter2_styled)
            # Fighter 2 Pie Chart   
            labels2 = ['KO', 'Submission', 'Decision']
            values2 = [fighter2_data['Win_KO'].values[0], fighter2_data['Win_Sub'].values[0], fighter2_data['Win_Decision'].values[0]]
            fig2 = px.pie(values=values2, names=labels2, title=f"{fighter2} Winning Methods")
            st.plotly_chart(fig2, theme="streamlit")
        

else:
    st.write("Select both fighters to begin analysis.")




# def generate_prediction(fighter1, fighter2):

api_key = st.text_input("Enter your OpenAI API Key", type="password")

if st.button("Predict the Fight"):
    if api_key:
        st.markdown('<p style="color:blue; font-size:14px;">Generating</p>', unsafe_allow_html=True)
        client = OpenAI(api_key=api_key)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        fighter_info_path = os.path.join(base_dir, 'Streamlit/data/fighter_info.csv')
        event_data_path = os.path.join(base_dir, 'Streamlit/data/event_data_sherdog.csv')
        file1 = client.files.create(
            file=open(fighter_info_path, "rb"),
            purpose='assistants'
        )
        file2 = client.files.create(
            file=open(event_data_path, "rb"),
            purpose='assistants'
        )
        assistant = client.beta.assistants.create(
            name="MMA Handicapper",
            instructions="You are an expert MMA/UFC Handicapper & Sport Bettor in Las Vegas. You definitely have the fighters requested general information in fighter_info.csv and all of their UFC fights and details in event_data_sherdog.csv.",
            # model="gpt-4o",
            model="gpt-4o-mini",
            tools=[{"type": "code_interpreter"}],
            tool_resources={
                "code_interpreter": {
                "file_ids": [file1.id, file2.id]
                }})
        # assistant_mma_handicapper = 'asst_Qa3dgoxXNz10xEzxWLBLkL0A'
        # assistant = client.beta.assistants.retrieve(assistant_mma_handicapper)
        st.write(assistant)
        thread = client.beta.threads.create()
        message1 = f"""Research {fighter1}"""
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=message1
        )
        run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
        )
        while True:
            if run.status == 'completed':
                break
            elif run.status == 'failed':
                st.write("Run failed.")
                break
            else:
                st.write(f"{run.status}")
                run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
                )
                time.sleep(10)
        messages = client.beta.threads.messages.list(
        thread_id=thread.id
        )
        # for message in reversed(messages.data):
        #     if hasattr(message.content[0], 'text'):
        #         st.write(message.role + ": " + message.content[0].text.value)
        #     elif hasattr(message.content[0], 'image_file'):
        #         st.write(message.role + ": [Image file received]")
        message2 = f"""Research {fighter2}"""
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=message2
        )
        run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
        )
        while True:
            if run.status == 'completed':
                break
            elif run.status == 'failed':
                st.write("Run failed.")
                break
            else:
                st.write(f"{run.status}")
                run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
                )
                time.sleep(10)
        messages = client.beta.threads.messages.list(
        thread_id=thread.id
        )
        # for message in reversed(messages.data):
        #     if hasattr(message.content[0], 'text'):
        #         st.write(message.role + ": " + message.content[0].text.value)
        #     elif hasattr(message.content[0], 'image_file'):
        #         st.write(message.role + ": [Image file received]")
        message3=f"Now predict the outcome of a potential fight between {fighter1} and {fighter2}. You must provide who you think will win, the method and time of victory, and a detailed explanation why you think that is likely."
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=message3
        )
        run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
        )
        while True:
            if run.status == 'completed':
                break
            elif run.status == 'failed':
                st.write("Run failed.")
                break
            else:
                st.write(f"{run.status}")
                run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
                )
                time.sleep(10)
        messages = client.beta.threads.messages.list(
        thread_id=thread.id
        )
        for message in reversed(messages.data):
            if hasattr(message.content[0], 'text'):
                st.write(message.role + ": " + message.content[0].text.value)
            elif hasattr(message.content[0], 'image_file'):
                st.write(message.role + ": [Image file received]")
    else:
        st.markdown('<p style="color:orange; font-size:14px;">Must enter OpenAI API Key to Generate Prediction</p>', unsafe_allow_html=True)

else:
    st.write("")
st.divider()


# Generate and Download Report
if st.button("Generate Report"):
    with open(f"mma_fight_prediction_report_{fighter1}_{fighter2}.txt", "w") as report_file:
        for message in reversed(messages.data):
            if hasattr(message.content[0], 'text'):
                st.write(message.role + ": " + message.content[0].text.value)
                report_file.write(message.role + ": " + message.content[0].text.value + "\n")
    st.write(f"Report generated and saved as 'mma_fight_prediction_report_{fighter1}_{fighter2}.txt'")
else:
    st.write("")




# ---- Contact Me ---- #
st.divider()
st.markdown('###### Created By Tyler Durette')
st.markdown("MMA AI © 2024 | [GitHub](https://github.com/bestisblessed) | [Contact Me](mailto:tyler.durette@gmail.com)")