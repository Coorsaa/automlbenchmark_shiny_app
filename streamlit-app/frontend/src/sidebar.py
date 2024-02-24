from enum import StrEnum

import pandas as pd
import streamlit as st


class Navigation(StrEnum):
    OVERVIEW: str = "Overview"
    ANALYSIS: str = "Analysis"


def create_sidebar():
    create_file_input()

def create_page_navigation():
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
    return tabs


def create_file_input():
    """Creates a file input which may store a dataframe under session_state.raw_data."""
    with st.sidebar:
        # streamlit side panel (input forms)
        raw_data = st.file_uploader(
            label='Select a results file:',
            # label_visibility='collapsed',
            accept_multiple_files=False,
            type="csv",
            help="Any results file produced by AMLB 2.1 or later.",
        )

        if raw_data:
            st.session_state.raw_data = pd.read_csv(raw_data)