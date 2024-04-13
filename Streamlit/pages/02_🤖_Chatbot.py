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
def run_chatbot(OPEN_AI_API_KEY):
    client = OpenAI(api_key=OPEN_AI_API_KEY)
    # assistant_mma_handicapper = 'asst_2kHC5LP6HMuDjrNDlUwhNAz2'
    assistant_mma_handicapper = 'asst_DqzNKHovo9ryalNPK9Nlh1IU' # GPT-3.5-Turbo
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


OPEN_AI_API_KEY = st.sidebar.text_input("Enter your OpenAI API key:", type='password')

if OPEN_AI_API_KEY:
    run_chatbot(OPEN_AI_API_KEY)
else:
    st.error("Please enter your OpenAI API key in the sidebar.")









# load_dotenv()
# OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
# client = OpenAI(api_key=OPEN_AI_API_KEY)

# assistant_mma_handicapper = 'asst_2kHC5LP6HMuDjrNDlUwhNAz2' # gpt-4
# assistant = client.beta.assistants.retrieve(assistant_mma_handicapper)
# st.title('MMA AI Chatbot')







### --- CHAT ---- ###

# # Create thread
# thread = client.beta.threads.create()
# st.write('Thread Info: ', thread)

# user_question = st.text_input("Enter your question:", "")

# if user_question:

#     # Add message to thread
#     message = client.beta.threads.messages.create(
#         thread_id=thread.id,
#         role="user",
#         content=user_question,
#     )

#     # Run it 
#     run = client.beta.threads.runs.create(
#     thread_id=thread.id,
#     assistant_id=assistant.id,
#     )

#     # st.write('Processing..')
#     processing_message = st.empty()
#     # processing_message.write('Processing...')
#     # loading_symbol = st.spinner('Processing...')
#     # processing_message.write('Processing...')

#     with st.spinner('Processing...'):
#         # Wait for completion 
#         while run.status != "completed":
#             time.sleep(2)
#             run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
#             # st.write(run.status)

#     # Remove or update the processing message
#     # processing_message.write('Done!')
#     st.success('Done!')

#     # Display assistant response
#     messages = client.beta.threads.messages.list(
#         thread_id=thread.id
#     )
#     # st.write('messages: ', messages)

#     # Print last message
#     st.write('Last Message: ', messages.data[0].content[0])

#     # Print all messages
#     st.write('All Messages: ')
#     for message in reversed(messages.data):
#         if hasattr(message.content[0], 'text'):
#             st.write(message.role + ": " + message.content[0].text.value)
#         elif hasattr(message.content[0], 'image_file'):
#             st.write(message.role + ": [Image file received]")
#         else:
#             st.write(message.role + ": [Unsupported content type]")

#     # Check if an image file is available
#     if hasattr(message.content[0], 'image_file'):
#         # Print and get any new files file_id
#         new_file = messages.data[0].content[0].image_file.file_id
#         # st.write(new_file)

#         # Download files created by assistant
#         image_data = client.files.content(new_file)
#         image_data_bytes = image_data.read()

#         # Display images and files downloaded
#         # st.write(image_data_bytes)
#         st.image(image_data_bytes)
#         # with open("./my-image.png", "wb") as file:
#         #     file.write(image_data_bytes)
#         #     Image(filename="./my-image.png")
#     else:
#         st.write('No image :(')







### Session State Version

# # Check if 'thread_id' is already stored in session state (i.e., a thread has been created)
# if 'thread_id' not in st.session_state:
#     # If not, create a new thread and store its ID in session state
#     thread = client.beta.threads.create()
#     st.session_state['thread_id'] = thread.id
#     st.write('Thread Info: ', thread)
# else:
#     # If a thread ID exists in session state, use it to indicate an ongoing conversation
#     st.write('Continuing conversation in Thread ID: ', st.session_state['thread_id'])

# user_question = st.text_input("Enter your question:", "")

# if user_question:
#     # Add message to the existing thread
#     message = client.beta.threads.messages.create(
#         thread_id=st.session_state['thread_id'],
#         role="user",
#         content=user_question,
#     )

#     # Run it 
#     run = client.beta.threads.runs.create(
#         thread_id=st.session_state['thread_id'],
#         assistant_id=assistant.id,
#     )

#     with st.spinner('Processing...'):
#         # Wait for completion 
#         while run.status != "completed":
#             time.sleep(2)
#             run = client.beta.threads.runs.retrieve(thread_id=st.session_state['thread_id'], run_id=run.id)

#     st.success('Done!')

#     # Display assistant response
#     messages = client.beta.threads.messages.list(
#         thread_id=st.session_state['thread_id']
#     )

#     st.write('Last Message: ', messages.data[0].content[0])

#     # Optionally, print all messages
#     st.write('All Messages: ')
#     for message in reversed(messages.data):
#         if hasattr(message.content[0], 'text'):
#             st.write(message.role + ": " + message.content[0].text.value)
#         elif hasattr(message.content[0], 'image_file'):
#             st.write(message.role + ": [Image file received]")
#         else:
#             st.write(message.role + ": [Unsupported content type]")

#     # Check if an image file is available
#     if hasattr(message.content[0], 'image_file'):
#         # Print and get any new files file_id
#         new_file = messages.data[0].content[0].image_file.file_id
#         # st.write(new_file)

#         # Download files created by assistant
#         image_data = client.files.content(new_file)
#         image_data_bytes = image_data.read()

#         # Display images and files downloaded
#         # st.write(image_data_bytes)
#         st.image(image_data_bytes)
#         # with open("./my-image.png", "wb") as file:
#         #     file.write(image_data_bytes)
#         #     Image(filename="./my-image.png")
#     else:
#         st.write('No image :(')







### No Comments Version ###

# import streamlit as st
# import openai
# from openai import OpenAI
# import os
# import requests
# import time
# from dotenv import load_dotenv
# from IPython.display import Image

# load_dotenv()
# OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
# client = OpenAI(api_key=OPEN_AI_API_KEY)
# assistant_football_buddy_GPT_3_Turbo_IMAGE = 'asst_n32qD42kWDFtEx4uQ2G59vRA'
# assistant = client.beta.assistants.retrieve(assistant_football_buddy_GPT_3_Turbo_IMAGE)

# st.title('NFL Chatbot')

# user_question = st.text_input("Enter your question:", "")

# if user_question:
#     thread = client.beta.threads.create()
#     st.write('Thread Info: ', thread)
#     message = client.beta.threads.messages.create(
#         thread_id=thread.id,
#         role="user",
#         content=user_question,
#     )
#     run = client.beta.threads.runs.create(
#     thread_id=thread.id,
#     assistant_id=assistant.id,
#     )

#     with st.spinner('Processing...'):
#         while run.status != "completed":
#             time.sleep(2)
#             run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

#     st.success('Done!')

#     messages = client.beta.threads.messages.list(
#         thread_id=thread.id
#     )
#     st.write('Last Message: ', messages.data[0].content[0])

#     st.write('All Messages: ')
#     for message in reversed(messages.data):
#         if hasattr(message.content[0], 'text'):
#             st.write(message.role + ": " + message.content[0].text.value)
#         elif hasattr(message.content[0], 'image_file'):
#             st.write(message.role + ": [Image file received]")
#         else:
#             st.write(message.role + ": [Unsupported content type]")

#     if hasattr(message.content[0], 'image_file'):
#         new_file = messages.data[0].content[0].image_file.file_id
#         image_data = client.files.content(new_file)
#         image_data_bytes = image_data.read()
#         st.image(image_data_bytes)
#     else:
#         st.write('No image :(')
