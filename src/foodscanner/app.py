import streamlit as st
import tempfile  # To save temporary files
from inference_sdk import InferenceHTTPClient
from llm_chains import load_normal_chain
import yaml
#import json

#Open config.yaml
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)


# Initialize the inference client
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="ES7YaZPAEOgwO3jbxG2u"
)

#Utlity Functions
def clear_input_field():
    if st.session_state.user_question == "":
        st.session_state.user_question = st.session_state.user_input
        st.session_state.user_input = ""

def set_send_input():
    st.session_state.send_input = True
    clear_input_field()

def load_chain():
    return load_normal_chain()

# File uploader (accept only images)

def main():

    if "send_input" not in st.session_state:
        st.session_state.send_input = False
        st.session_state.user_question = ""
    if "user_input" not in st.session_state:
        st.session_state.user_input = []

    st.title("Food Scanner")
    chat_container = st.container()

    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"], on_change = set_send_input, key = "callback")

    if uploaded_file is not None:
        # Display uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(uploaded_file.read())  # Save image bytes
            temp_file_path = temp_file.name  # Get file path

        # Perform inference using the saved file path
        result = CLIENT.infer(temp_file_path, model_id="calorie-tracker-pmuck/4")

        #Display the result
        predictions = result["predictions"]
        foods = []
        for i in range(len(predictions)):
            foods.append(predictions[i]["class"])
        #food = predictions[0]["class"]
        st.session_state.user_input = foods

        voice_rec, send_button_column = st.columns(2)
        with send_button_column:
            send_button = st.button("Send", key="send_button", on_click=clear_input_field)

        llm_chain = load_chain()
        
        if send_button or st.session_state.send_input:
            if st.session_state.user_question != "":
                with chat_container:
                    st.chat_message("User").write(f"{food} calories..." for food in foods)
                    llm_response = llm_chain.run(st.session_state.user_input)
                    st.chat_message("ai").write(llm_response)
                    st.session_state.user_question = ""

if __name__ == "__main__":
    main() 