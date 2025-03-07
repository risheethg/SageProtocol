import streamlit as st
import tempfile  # To save temporary files
from inference_sdk import InferenceHTTPClient,InferenceConfiguration
from llm_chains import load_normal_chain
import yaml
import json  # To format data as JSON

# Open config.yaml
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Initialize the inference client
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="Xqu1B5tB0s3Di5Kpqi5N"
)

# Utility Functions
def clear_input_field():
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
        st.session_state.user_input = ""

    st.title("Food Scanner")

    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"], on_change=set_send_input, key="callback")

    if uploaded_file is not None:
        # Display uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(uploaded_file.read())  # Save image bytes
            temp_file_path = temp_file.name  # Get file path

        # Perform inference using the saved file path
        custom_configuration = InferenceConfiguration(confidence_threshold=0.3, iou_threshold=0.5)

# Perform inference with the custom configuration
        with CLIENT.use_configuration(custom_configuration):
            result = CLIENT.infer(temp_file_path, model_id="calorie-tracker-pmuck/4")

        # Extract all detected food items
        predictions = result["predictions"]
        
        if not predictions:
            st.error("No food detected in the image. Please try another image.")
            return

        # Format detected food items into a structured list
        food_items = [pred["class"] for pred in predictions]  # Extract food names only
        
        # Display detected food items (only names)
        st.subheader("Detected Food Items:")
        st.write(", ".join(food_items))
        st.session_state.user_input=food_items

        # Send extracted food names to LLM
        llm_chain = load_chain()
        llm_response = llm_chain.run(st.session_state.user_input)
# Pass as string

        # Display AI response (only the result, no JSON)
        st.subheader("Nutritional Information:")
        st.write(llm_response)  # Show only LLM output

if __name__ == "__main__":
    main()
