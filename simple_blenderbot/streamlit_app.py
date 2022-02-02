import streamlit as st
from streamlit_chat import message
import requests
import random
import json

# setting page title and favicon
st.set_page_config(page_title="Blenderbot chatbot", page_icon="\U0001F916")

# valid list of avatar styles for chatbot
avatar_list = [
    "adventurer",
    "adventurer-neutral",
    "avataaars",
    "big-ears",
    "big-ears-neutral",
    "big-smile",
    "croodles",
    "croodles-neutral",
    "female",
    "gridy",
    "human",
    "identicon",
    "initials",
    "jdenticon",
    "male",
    "micah",
    "miniavs",
    "pixel-art",
    "pixel-art-neutral",
    "personas",
    "bottts",
]

user_avatar_list = avatar_list[:-1]  # all of avatars except bottts which will be used for the bot

# mapping of model size to model names
model_dict = {
    "large": "facebook/blenderbot-3B",
    "medium": "facebook/blenderbot-400M-distill",
    "small": "facebook/blenderbot_small-90M",
}


def initialize():
    """Initialize some session states"""
    if "generated" not in st.session_state:
        st.session_state["generated"] = []

    if "past" not in st.session_state:
        st.session_state["past"] = []

    if "bot" not in st.session_state:
        st.session_state["bot"] = {
            "bot_avatar": avatar_list.pop(),
            "bot_seed": random.randint(1, 9999),
        }

    if "user" not in st.session_state:
        st.session_state["user"] = {
            "user_avatar": random.choice(avatar_list),
            "user_seed": random.randint(1, 9999),
        }


def query(payload):
    '''Send post request to api and fetch and process response. The payload is a json 
    serializable object. The required inputs are specified by the api.'''
    data = json.dumps(payload)
    response = requests.post(API_URL, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))


def change_model():
    '''resetting some session states when the model is changed'''
    st.session_state["generated"] = []
    st.session_state["past"] = []
    st.session_state["bot"] = {
        "bot_avatar": "bottts",
        "bot_seed": random.randint(1, 9999),
    }
    st.session_state["input"] = ""


def change_avatar():
    '''Set the user session state once the avatar has been changed'''
    st.session_state["user"] = {
        "user_avatar": st.session_state.user_avatar,
        "user_seed": random.randint(1, 9999),
    }


initialize()

st.title("\U0001F916 Blender Bot")

st.header("Chat with Facebook Blender Bot")
st.markdown(
    """
Blender Bot is an open source chatbot that builds long-term memory and searches the internet. Its quite fun talking 
to the chatbot. Just type what you want to say in the text box below and press **Enter**.

You can also choose from different sized models to use. The large model gives better performance 
but is slower. The small model is faster but has poorer performance. Overall, the medium 
sized model gives the optimal performance and speed.

You can also change the user avatar using the drop down list.

*For advanced users:*  
The model was deployed using [Streamlit](https://streamlit.io/) and deployed on 
[Streamlit Cloud](https://streamlit.io/cloud). The chatbot interface was made using 
[streamlit-chat](https://pypi.org/project/streamlit-chat/). Instructions on how to make a chatbot using streamlit-chat 
were found from the [example app](https://github.com/AI-Yash/st-chat/tree/main/examples) by streamlit-chat. For the 
chatbot responses, the [blenderbot-400M-distill by facebook](https://huggingface.co/facebook/blenderbot-400M-distill) was
used via the [huggingface inference api](https://huggingface.co/inference-api). The code for this project can be found in 
this [Github](https://github.com/AhmedFahim-git/chbt_deploy) repo.

**P.S.** The initial chatbot avatars are chosen randomly.
"""
)

# Selectbox for selecting model
selected_model = st.selectbox(
    "Select model size:",
    model_dict.keys(),
    index=1,
    on_change=change_model,
    help='Select model to use for inference. The large model has better performance bus is slower. If unsure, use "medium" for optimal speed and performance.',
)

API_URL = f"https://api-inference.huggingface.co/models/{model_dict[selected_model]}"
headers = {"Authorization": f"Bearer { st.secrets['huggingface_api_key'] } "}

# Selectbox for selecting user's avatar
st.selectbox(
    "Select your avatar:",
    user_avatar_list,
    index=user_avatar_list.index(st.session_state["user"]["user_avatar"]),
    key="user_avatar",
    on_change=change_avatar,
    help="Select your avatar. The avatar is used to identify you in the chatbot.",
)

# Text box for user input
user_input = st.text_input("You: ", "", key="input")

# After the user enters input use it to retrieve response from api and append to session state
if user_input:
    # retrieve response from user input using api
    output = query(
        {
            "inputs": {
                "past_user_inputs": st.session_state.past,
                "generated_responses": st.session_state.generated,
                "text": user_input,
            },
            "options": {"wait_for_model": True},
        }
    )
    # append the user input and generated text to their respective session state
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output["generated_text"])

# once the response is retrieved from the api, display the messages on the screen
if st.session_state["generated"]:

    for i in range(len(st.session_state["generated"]) - 1, -1, -1):
        message(
            st.session_state["generated"][i],
            key=str(i),
            avatar_style=st.session_state.bot["bot_avatar"],
            seed=st.session_state.bot["bot_seed"],
        )
        message(
            st.session_state["past"][i],
            is_user=True,
            key=str(i) + "_user",
            avatar_style=st.session_state.user["user_avatar"],
            seed=st.session_state.user["user_seed"],
        )
