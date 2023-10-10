from enum import StrEnum

import streamlit as st


class Navigation(StrEnum):
    OVERVIEW: str = "Overview"
    ANALYSIS: str = "Analysis"


def create_sidebar_page_navigation():
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
