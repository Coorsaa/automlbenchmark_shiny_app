import streamlit as st
import pandas as pd
import requests

from navigation import create_sidebar_page_navigation, Navigation

__version__ = "0.2"
_repository = "https://github.com/Coorsaa/automlbenchmark_shiny_app/"


def configure_streamlit():
    """Sets the streamlit page configuration."""
    st.set_page_config(
        page_title=f"AutoML-Benchmark Analysis App - v{__version__}",
        menu_items={
            "Get help": f"{_repository}",
            "Report a bug": f"{_repository}/issues/new",
        },
    )


def create_file_input():
    """Creates a file input which may store a dataframe under session_state.raw_data."""
    with st.sidebar:
        with st.form("user_inputs"):
            # streamlit side panel (input forms)
            st.markdown("### Data")
            raw_data = st.file_uploader(
                label="Upload your data here:", accept_multiple_files=False
            )
            upload_file = st.form_submit_button("Upload Files")

        if upload_file:
            st.session_state.raw_data = pd.read_csv(raw_data)


def show_overview():
    """Generates content for the overview page."""
    if "raw_data" not in st.session_state:
        st.text("Please upload a result file from the sidebar on the left.")
        return
    st.dataframe(st.session_state.raw_data)


if __name__ == "__main__":
    configure_streamlit()
    tabs = create_sidebar_page_navigation()
    if tabs == Navigation.OVERVIEW:
        create_file_input()
        show_overview()

    if tabs == Navigation.ANALYSIS and "raw_data" in st.session_state:
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