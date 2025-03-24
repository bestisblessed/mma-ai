import streamlit as st
import openai
from openai import OpenAI
import os
import requests
import time
from dotenv import load_dotenv
from IPython.display import Image

st.title('MMA AI Chatbot')

### Function Version ###
def run_chatbot(OPENAI_API_KEY):
    client = OpenAI(api_key=OPENAI_API_KEY)
    # assistant_mma_handicapper = 'asst_2kHC5LP6HMuDjrNDlUwhNAz2'
    # assistant_mma_handicapper = 'asst_l98W2wkDAwj2yTRFgZmxRb1N'
    assistant_mma_handicapper = 'asst_zahT75OFBs5jgi346C9vuzKa'
    assistant = client.beta.assistants.retrieve(assistant_mma_handicapper)
    if 'thread_id' not in st.session_state:
        thread = client.beta.threads.create()
        st.session_state['thread_id'] = thread.id
        st.write('Thread Info: ', thread)
    else:
        st.write('Continuing conversation in Thread ID: ', st.session_state['thread_id'])
    user_question = st.text_input("Enter your question:", "")
    if user_question:
        message = client.beta.threads.messages.create(
            thread_id=st.session_state['thread_id'],
            role="user",
            content=user_question,
        )
        run = client.beta.threads.runs.create(
            thread_id=st.session_state['thread_id'],
            assistant_id=assistant.id,
        )
        with st.spinner('Processing...'):
            while run.status != "completed":
                time.sleep(10)
                run = client.beta.threads.runs.retrieve(thread_id=st.session_state['thread_id'], run_id=run.id)
        st.success('Done!')
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state['thread_id']
        )
        for message in reversed(messages.data):
            if hasattr(message.content[0], 'text'):
                st.write(message.role + ": " + message.content[0].text.value)
            elif hasattr(message.content[0], 'image_file'):
                st.write(message.role + ": [Image file received]")
            else:
                st.write(message.role + ": [Unsupported content type]")
        if hasattr(message.content[0], 'image_file'):
            new_file = messages.data[0].content[0].image_file.file_id
            image_data = client.files.content(new_file)
            image_data_bytes = image_data.read()
            st.image(image_data_bytes)
        else:
            st.write('No image :(')

# OPENAI_API_KEY = st.sidebar.text_input("Enter your OpenAI API key:", type='password')

# Access the API key from secrets
OPENAI_API_KEY = st.secrets["general"]["OPENAI_API_KEY"]

if OPENAI_API_KEY:
    run_chatbot(OPENAI_API_KEY)
else:
    st.error("Please enter your OpenAI API key in the sidebar.")