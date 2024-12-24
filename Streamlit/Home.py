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
import os

# TO DO
# - get fighter pictures when selected from online

st.set_page_config(page_title="MMA AI", page_icon="🥊", layout="wide")

# ---- Loading Data ---- #
base_dir = os.path.dirname(os.path.abspath(__file__))  # This gives you the directory where the script is located
df_event_data = pd.read_csv(os.path.join(base_dir, 'data/event_data_sherdog.csv'))
df_fighter_data = pd.read_csv(os.path.join(base_dir, 'data/fighter_info.csv'))
dataframes = [df_event_data, df_fighter_data]
st.session_state['df_event_data'] = df_event_data
st.session_state['df_fighter_data'] = df_fighter_data
# Streamlit/Streamlit/
# ---- Loading Data from GitHub URLs ---- #
# event_data_url = 'https://raw.githubusercontent.com/bestisblessed/mma-ai/main/Streamlit/data/event_data_sherdog.csv'
# fighter_data_url = 'https://raw.githubusercontent.com/bestisblessed/mma-ai/main/Streamlit/data/fighter_info.csv'
# df_event_data = pd.read_csv(event_data_url)
# df_fighter_data = pd.read_csv(fighter_data_url)
# st.session_state['df_event_data'] = df_event_data
# st.session_state['df_fighter_data'] = df_fighter_data
df_event_data = df_event_data.map(lambda x: x.lower() if isinstance(x, str) else x)
df_fighter_data = df_fighter_data.map(lambda x: x.lower() if isinstance(x, str) else x)

# ---- Centered Container ---- #
col1, col2, col3 = st.columns([0.1, 1, 0.1])
with col2:
    # ---- Titles ---- #
    # st.title('MMA AI')
    # st.write('Welcome to MMA AI. Time to fucking win.')
    st.markdown("<h1 style='text-align: center;'>MMA AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6c757d; font-style: italic;'>Welcome to MMA AI. Time to win.</p>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background-color: #333333; padding: 20px; border-radius: 10px;">
        <p style='color: white; text-align: center;'>
            Simply select two fighters in an upcoming matchup and provide an OpenAI API key and watch the magic happen.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    # ---- Fighter Selection ---- #
    # st.subheader('Select Fighters')
    st.markdown("<h2 style='text-align: center; color: white; background-color: #d62828; padding: 10px;'>Select Fighters</h2>", unsafe_allow_html=True)
    st.write('')
    fighter_names = df_fighter_data['fighter'].unique()
    col1, col2 = st.columns(2)
    with col1:
        fighter1 = st.selectbox('fighter 1', fighter_names, index=list(fighter_names).index("conor mcgregor"))
    with col2:
        fighter2 = st.selectbox('fighter 2', fighter_names, index=list(fighter_names).index("michael chandler"))
    st.divider()
    # Fight Prediction and Report Assistant GPT
    api_key = st.text_input("Enter your OpenAI API Key", type="password")
    if st.button("Predict Fight and Generate Report"):
        if api_key:
            with st.spinner('Generating prediction and report...'):  # This line was added
                client = OpenAI(api_key=api_key)
                base_dir = os.path.dirname(os.path.abspath(__file__))
                # fighter_info_path = os.path.join(base_dir, 'data/fighter_info.csv')
                # event_data_path = os.path.join(base_dir, 'data/event_data_sherdog.csv')
                # file1 = client.files.create(
                #     file=open(fighter_info_path, "rb"),
                #     purpose='assistants'
                # )
                # file2 = client.files.create(
                #     file=open(event_data_path, "rb"),
                #     purpose='assistants'
                # )
                # assistant = client.beta.assistants.create(
                # name="MMA Handicapper",
                #     instructions="You are an expert MMA/UFC Handicapper & Sport Bettor in Las Vegas. You definitely have the fighters requested general information in fighter_info.csv and all of their UFC fights and details in event_data_sherdog.csv.",
                #     # model="gpt-4o",
                #     model="gpt-4o-mini",
                #     tools=[{"type": "code_interpreter"}],
                #     tool_resources={
                #         "code_interpreter": {
                #         "file_ids": [file1.id, file2.id]
                #         }})
                # assistant_mma_handicapper = 'asst_Qa3dgoxXNz10xEzxWLBLkL0A'
                assistant_mma_handicapper = 'asst_zahT75OFBs5jgi346C9vuzKa'
                assistant = client.beta.assistants.retrieve(assistant_mma_handicapper)
                st.write("Using assistant: ", assistant.id)
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
                        # st.write(f"{run.status}")
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
                        # st.write(f"{run.status}")
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
                        # st.write(f"{run.status}")
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
                report_filename = f"mma_fight_prediction_report_{fighter1}_{fighter2}.txt"
                with open(report_filename, "w") as report_file:
                    for message in reversed(messages.data):
                        if hasattr(message.content[0], 'text'):
                            st.write(message.role + ": " + message.content[0].text.value)
                            report_file.write(message.role + ": " + message.content[0].text.value + "\n")
                st.write(f"Report generated and saved as 'mma_fight_prediction_report_{fighter1}_{fighter2}.txt'")
                with open(report_filename, "r") as file:
                    report_content = file.read()
                st.download_button(
                    label="Download Report",
                    data=report_content,
                    file_name=report_filename,
                    mime="text/plain"
                )
        else:
            st.markdown('<p style="color:orange; font-size:14px;">Must enter OpenAI API Key to Generate Prediction</p>', unsafe_allow_html=True)
    else:
        st.write("")

if fighter1 and fighter2:
    if fighter1 == fighter2:
        st.warning("Please select two different fighters.")
    else:
        fighter1_data = df_fighter_data[df_fighter_data['fighter'] == fighter1]
        fighter2_data = df_fighter_data[df_fighter_data['fighter'] == fighter2]

        # Extract and format the name with nickname
        fighter1_full_name = fighter1_data['fighter'].values[0]
        fighter1_nickname = fighter1_data['nickname'].values[0]
        fighter1_first_name = fighter1_full_name.split()[0]
        fighter1_last_name = " ".join(fighter1_full_name.split()[1:])
        fighter1_formatted_name = f"{fighter1_first_name} '{fighter1_nickname}' {fighter1_last_name}"
        fighter2_full_name = fighter2_data['fighter'].values[0]
        fighter2_nickname = fighter2_data['nickname'].values[0]
        fighter2_first_name = fighter2_full_name.split()[0]
        fighter2_last_name = " ".join(fighter2_full_name.split()[1:])
        fighter2_formatted_name = f"{fighter2_first_name} '{fighter2_nickname}' {fighter2_last_name}"

        # Calculate Fighter 1 and 2 win/loss streak
        fighter1_fights = df_event_data[(df_event_data['fighter 1'] == fighter1) | (df_event_data['fighter 2'] == fighter1)]
        fighter1_fights = fighter1_fights.sort_values(by='event date', ascending=False)
        streak_type1 = None
        streak_count1 = 0
        for _, row in fighter1_fights.iterrows():
            if row['winning fighter'] == fighter1:
                if streak_type1 == 'w' or streak_type1 is None:
                    streak_type1 = 'w'
                    streak_count1 += 1
                else:
                    break
            else:
                if streak_type1 == 'l' or streak_type1 is None:
                    streak_type1 = 'l'
                    streak_count1 += 1
                else:
                    break
        fighter1_streak = f"{streak_count1}{streak_type1}" if streak_type1 else "No Streak"
        fighter2_fights = df_event_data[(df_event_data['fighter 1'] == fighter2) | (df_event_data['fighter 2'] == fighter2)]
        fighter2_fights = fighter2_fights.sort_values(by='event date', ascending=False)
        streak_type2 = None
        streak_count2 = 0
        for _, row in fighter2_fights.iterrows():
            if row['winning fighter'] == fighter2:
                if streak_type2 == 'w' or streak_type2 is None:
                    streak_type2 = 'w'
                    streak_count2 += 1
                else:
                    break
            else:
                if streak_type2 == 'l' or streak_type2 is None:
                    streak_type2 = 'l'
                    streak_count2 += 1
                else:
                    break
        fighter2_streak = f"{streak_count2}{streak_type2}" if streak_type2 else "No Streak"

        col1, col2 = st.columns(2)
        with col1:
            # st.write(f"### {fighter1_formatted_name}")
            st.write(f"### '{fighter1_nickname}' {fighter1}")
            st.markdown(f"""
            - **Nickname**: {fighter1_data['nickname'].values[0]}
            - **Birth Date**: {fighter1_data['birth date'].values[0]}
            - **Nationality**: {fighter1_data['nationality'].values[0]}
            - **Association**: {fighter1_data['association'].values[0]}
            - **Weight Class**: {fighter1_data['weight class'].values[0]}
            - **Height**: {fighter1_data['height'].values[0]}
            - **Wins**: {fighter1_data['wins'].values[0]}
            - **Losses**: {fighter1_data['losses'].values[0]}
            - **Wins by Decision**: {fighter1_data['win_decision'].values[0]}
            - **Wins by KO**: {fighter1_data['win_ko'].values[0]}
            - **Wins by Submission**: {fighter1_data['win_sub'].values[0]}
            - **Losses by Decision**: {fighter1_data['loss_decision'].values[0]}
            - **Losses by KO**: {fighter1_data['loss_ko'].values[0]}
            - **Losses by Submission**: {fighter1_data['loss_sub'].values[0]}
            - **Fighter ID**: {fighter1_data['fighter_id'].values[0]}
            - **Current Streak**: {fighter1_streak}
            """)
            # Most Recent 5 Fights for Fighter 1
            st.markdown("<h5 style='text-align: center; color: grey;'>Most Recent 5 Fights</h5>", unsafe_allow_html=True)
            fighter1_fights = df_event_data[(df_event_data['fighter 1'] == fighter1) | (df_event_data['fighter 2'] == fighter1)]
            fighter1_fights = fighter1_fights.sort_values(by='event date', ascending=False).head(5)
            fighter1_styled = fighter1_fights[['event name', 'event date', 'fighter 1', 'fighter 2', 'winning fighter', 'winning method', 'winning round']].style.apply(
                lambda row: ['background-color: lightgreen' if row['winning fighter'] == fighter1 else 'background-color: lightcoral'] * len(row),
                axis=1
            )
            st.dataframe(fighter1_styled)
            # Fighter 1 Pie Chart
            labels1 = ['KO', 'Submission', 'Decision']
            values1 = [fighter1_data['win_ko'].values[0], fighter1_data['win_sub'].values[0], fighter1_data['win_decision'].values[0]]
            fig1 = px.pie(values=values1, names=labels1, title=f"{fighter1} Winning Methods")
            st.plotly_chart(fig1, theme="streamlit")

        with col2:
            st.write(f"### '{fighter2_nickname}' {fighter2}")
            st.markdown(f"""
            - **Nickname**: {fighter2_data['nickname'].values[0]}
            - **Birth Date**: {fighter2_data['birth date'].values[0]}
            - **Nationality**: {fighter2_data['nationality'].values[0]}
            - **Association**: {fighter2_data['association'].values[0]}
            - **Weight Class**: {fighter2_data['weight class'].values[0]}
            - **Height**: {fighter2_data['height'].values[0]}
            - **Wins**: {fighter2_data['wins'].values[0]}
            - **Losses**: {fighter2_data['losses'].values[0]}
            - **Wins by Decision**: {fighter2_data['win_decision'].values[0]}
            - **Wins by KO**: {fighter2_data['win_ko'].values[0]}
            - **Wins by Submission**: {fighter2_data['win_sub'].values[0]}
            - **Losses by Decision**: {fighter2_data['loss_decision'].values[0]}
            - **Losses by KO**: {fighter2_data['loss_ko'].values[0]}
            - **Losses by Submission**: {fighter2_data['loss_sub'].values[0]}
            - **Fighter ID**: {fighter2_data['fighter_id'].values[0]}
            - **Current Streak**: {fighter2_streak}
            """)
            # Most Recent 5 Fights for Fighter 2
            st.markdown("<h5 style='text-align: center; color: grey;'>Most Recent 5 Fights</h5>", unsafe_allow_html=True)
            fighter2_fights = df_event_data[(df_event_data['fighter 1'] == fighter2) | (df_event_data['fighter 2'] == fighter2)]
            fighter2_fights = fighter2_fights.sort_values(by='event date', ascending=False).head(5)
            fighter2_styled = fighter2_fights[['event name', 'event date', 'fighter 1', 'fighter 2', 'winning fighter', 'winning method', 'winning round']].style.apply(
                lambda row: ['background-color: lightgreen' if row['winning fighter'] == fighter2 else 'background-color: lightcoral'] * len(row),
                axis=1
            )
            st.dataframe(fighter2_styled)
            # Fighter 2 Pie Chart   
            labels2 = ['KO', 'Submission', 'Decision']
            values2 = [fighter2_data['win_ko'].values[0], fighter2_data['win_sub'].values[0], fighter2_data['win_decision'].values[0]]
            fig2 = px.pie(values=values2, names=labels2, title=f"{fighter2} Winning Methods")
            st.plotly_chart(fig2, theme="streamlit")
        

else:
    st.write("Select both fighters to begin analysis.")


# Generate and Download Report
# if st.button("Generate Report"):
#     with open(f"mma_fight_prediction_report_{fighter1}_{fighter2}.txt", "w") as report_file:
#         for message in reversed(messages.data):
#             if hasattr(message.content[0], 'text'):
#                 st.write(message.role + ": " + message.content[0].text.value)
#                 report_file.write(message.role + ": " + message.content[0].text.value + "\n")
#     st.write(f"Report generated and saved as 'mma_fight_prediction_report_{fighter1}_{fighter2}.txt'")
# else:
#     st.write("")




# ---- Contact Me ---- #
st.divider()
st.markdown('###### Created By Tyler Durette')
st.markdown("MMA AI © 2024 | [GitHub](https://github.com/bestisblessed) | [Contact Me](mailto:tyler.durette@gmail.com)")