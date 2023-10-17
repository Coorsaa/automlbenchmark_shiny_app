from pathlib import Path
import streamlit as st
import pandas as pd

from navigation import create_sidebar_page_navigation, Navigation
from shiny import display_shiny_app
from pareto import inference_vs_performance_pareto

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

def load_default_dataset():
    """Loads the 2023 results file."""
    filepath = Path("/data/amlb_all.csv")
    if filepath.exists():
        st.session_state.raw_data = pd.read_csv(filepath)


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
    load_default_dataset()
    tabs = create_sidebar_page_navigation()
    if tabs == Navigation.OVERVIEW:
        create_file_input()
        show_overview()

    if tabs == Navigation.ANALYSIS and "raw_data" in st.session_state:
        display_shiny_app()
