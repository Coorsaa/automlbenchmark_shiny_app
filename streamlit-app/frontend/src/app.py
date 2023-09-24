import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title=f"AutoML-Benchmark Analysis App - v0.2",
    menu_items={
        "Get help": "https://github.com/",
        "Report a bug": "https://github.com/",
    },
)

### UI ###
with st.sidebar:
    st.title("AutoML-Benchmark Analysis App")
    st.write("---")
    tabs = st.radio(
        label="Page Navigation",
        options=(
            "Overview",
            "Analysis",
        ),
        horizontal=True,
    )
    st.write("---")
    st.markdown("## Parameters")

if tabs == "Overview":
    with st.sidebar:
        with st.form("user_inputs"):
            # streamlit side panel (input forms)
            st.markdown("### Data")
            raw_data = st.file_uploader(
                label = "Upload your data here:", accept_multiple_files = False
            )
            upload_file = st.form_submit_button("Upload Files")

        if upload_file:
            st.session_state.raw_data = pd.read_csv(raw_data)

    if "raw_data" in st.session_state:
        st.dataframe(st.session_state.raw_data)


if tabs == "Analysis" and "raw_data" in st.session_state:
    frameworks = st.session_state.raw_data.framework.unique()
    with st.sidebar:
        selected_frameworks = st.multiselect(
            label = "Choose Frameworks",
            options = frameworks,
            default = frameworks
        )
        col1, col2 = st.columns(2)
        with col1:
            input_min = st.slider(
                label = "Minimum",
                min_value = 0,
                max_value = 100,
                value = 0
            )
        with col2:
            input_max = st.slider(
                label = "Maximum",
                min_value = 0,
                max_value = 100,
                value = 100
            )
    
    # Define the REST API URL
    api_url = "http://backend:8080/api/bt_tree"  # Use the service name as the hostname
    test_url = "http://backend:8080/api/test"  # Use the service name as the hostname

    # payload
    payload = {
        "text": "Hello World!",
        "min": input_min,
        "max": input_max
    }

    # Make a request to the REST API
    response = requests.post(test_url, data = payload)

    # Check if the request was successful
    if response.status_code == 200:
        # Display the PNG image from the API response
        st.image(response.content)
    else:
        st.error("Failed to fetch image from the REST API")