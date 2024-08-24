import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from streamlit_lottie import st_lottie
from PIL import Image

# ---- Dig Deep ---- #
# st.dataframe(df_event_data.head())
# st.write("Basic Statistics for Event Data:")
# st.write(df_event_data.describe())

# st.dataframe(df_fighter_data.head())
# st.write("Basic Statistics for Fighter Data:")
# st.write(df_fighter_data.describe())

# ---- Loading Other Files ---- #
### Lottie 1
def load_lottie_pictures(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()
lottie_picture1 = load_lottie_pictures("https://lottie.host/9501172e-b94f-441d-a10d-406d7536663c/510yizrK3A.json")

picture1 = Image.open('./images/pereira-adesanya-faceoff.jpeg') # Picture 1
picture2 = Image.open('./images/ferg.jpg') # Picture 2

# ---- Introduction and Bio ---- #
# st.write('---')
st.divider()
st.header('Introduction')
left_column, right_column = st.columns(2)
with left_column:
    st.write('##')
    st.write('''
             I predict winners. Simple as that. All I do is win.
             - Predictive modeling
             - Game outcomes
             - Player performances
             - Arbitrage opportunities
             - Random shit

             If this all interests you, this is your lucky day. Nobody is better than us.
             ''')
with right_column:
    st_lottie(lottie_picture1, height=400, width=400, key='lottie1')


# ---- Some Samples ---- #
# st.write('---')
st.divider()
st.header('Some Samples')

### Sample Code
st.write('##')
st.code('''
        import numpy as np
        import streamlit as st
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        import requests
        from streamlit_lottie import st_lottie
        from PIL import Image
        ''', language='python'
        )

### Sample 1
st.write('##')
image_column_left, text_column_right = st.columns((1, 2)) ### 2nd column twice as big as 1st
with image_column_left:
    st.image(picture1, use_column_width=True, caption="UFC 287")
with text_column_right:
    st.markdown('#### Sample 1')
    st.write('''
            Here is one of my examples, this is what it does:
            1. Uses my unique and confidential mma dataset to analyze 
            2. Finds outlying trends
            3. Makes game and player predictions
             ''')

### Sample 2
st.write('##')
text_column_left, image_column_right = st.columns((2, 1)) ### 2nd column twice as big as 1st
with text_column_left:
    st.markdown('#### Sample 2')
    st.write('''
            Here is one of my examples, this is what it does:
            1. Uses my unique and confidential mma dataset to analyze 
            2. Finds outlying trends
            3. Makes game and player predictions
             ''')
with image_column_right:
    st.image(picture2, use_column_width=True, caption="Before the crash")

# ---- Galleria ---- #
# Images
st.divider()
st.header('Galleria')
image1list = Image.open('./images/friends.jpg')
image2list = Image.open('./images/holloway1.jpeg')
image3list = Image.open('./images/jonesgustaffson.jpg')
col1, col2, col3 = st.columns(3)  # Creates three columns
with col1:
    st.image(image1list, use_column_width=True, caption="Image 1")
with col2:
    st.image(image2list, use_column_width=True, caption="Image 2")
with col3:
    st.image(image3list, use_column_width=True, caption="Image 3")

# Video
video1 = 'https://www.youtube.com/watch?v=KxeQHTyfbc0&list=PL3HhsOxjnSwLz4DnP7jQxk8BnvvanToll&index=7&ab_channel=UFC'
st.write('##')
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.video(video1)
    st.caption("To get hyped")


# ---- Contact Me ---- #
st.divider()
st.markdown("MMA AI © 2024 | [GitHub](https://github.com/bestisblessed) | [Contact](https://twitter.com/Drtyyy_)")


# # Data Display Functions
# st.dataframe(data)  # Display a dataframe
# st.table(data)  # Display a static table
# st.json(data)  # Display JSON content

# # Input Widgets
# st.button("Click Me")  # Display a button
# st.checkbox("Check me out")  # Display a checkbox
# st.radio("Choose one", options=['Option 1', 'Option 2'])  # Display radio buttons
# st.selectbox("Pick one:", options=['Option 1', 'Option 2'])  # Display a select box
# st.multiselect("Pick several:", options=['Option 1', 'Option 2'])  # Display a multiselect box
# st.slider("Slide me", min_value=0, max_value=10)  # Display a slider
# st.select_slider("Slide to select", options=['Option 1', 'Option 2'])  # Display a select slider
# st.text_input("Enter something")  # Display a text input box
# st.number_input("Enter a number")  # Display a number input box
# st.text_area("Area for textual entry")  # Display a text area
# st.date_input("Pick a date")  # Display a date input
# st.time_input("Pick a time")  # Display a time input
# st.file_uploader("Upload a file")  # Display a file uploader
# st.color_picker("Pick a color")  # Display a color picker

# # Display Text
# st.title("This is a title")  # Display a title
# st.header("This is a header")  # Display a header
# st.subheader("This is a subheader")  # Display a subheader
# st.text("This is some text")  # Display text
# st.markdown("This is **markdown**")  # Display markdown
# st.caption("This is a caption")  # Display a caption
# st.code("for i in range(10): pass", language='python')  # Display code

# # Layouts and Containers
# st.columns([1, 2, 3])  # Display columns for layout
# st.expander("See explanation")  # Display an expander
# st.container()  # Create a container
# st.empty()  # Create an empty slot

# # Media and Static Elements
# st.image(image, caption="This is an image")  # Display an image
# st.audio(data)  # Display audio
# st.video(data)  # Display video
