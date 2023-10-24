from pathlib import Path
import streamlit as st
import pandas as pd

from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from streamlit_extras.dataframe_explorer import dataframe_explorer

from navigation import create_sidebar_page_navigation, Navigation
from shiny import display_shiny_app
import seaborn
from error_plot import plot_errors
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
        layout="wide",
    )

def load_default_dataset():
    """Loads the 2023 results file."""
    filepath = Path("/data/amlb_all.csv")
    if filepath.exists():
        st.session_state.raw_data = pd.read_csv(filepath)


def show_seaborn_plot():
    """Demo"""
    import matplotlib.pyplot as plt
    xs=list(range(10))
    ys=list(x**2 for x in xs)
    fig, ax = plt.subplots()
    seaborn.lineplot(x=xs, y=ys, ax=ax)
    st.pyplot(fig)

def show_error_plot():
    # if any(st.session_state.filtered_data["source"] == "2021Q3"):
    #     st.text("The error graph only works with 2023Q2 data.")
    #     return
    fig = plot_errors(st.session_state.filtered_data)
    st.pyplot(fig)

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


def show_table():
    """Generates content for the overview page."""
    if "raw_data" not in st.session_state:
        st.text("Please upload a result file from the sidebar on the left.")
        return

    df = st.session_state.raw_data
    with st.expander("Filter Results"):
        df['framework'] = df['framework'].astype('category')
        filtered_df = dataframe_explorer(df, case=False)
        st.dataframe(filtered_df, use_container_width=True)
        st.session_state.filtered_data = filtered_df

if __name__ == "__main__":
    configure_streamlit()
    load_default_dataset()
    tabs = create_sidebar_page_navigation()
    if tabs == Navigation.OVERVIEW:
        create_file_input()
        show_table()
        show_error_plot()

    if tabs == Navigation.ANALYSIS and "raw_data" in st.session_state:
        display_shiny_app()
