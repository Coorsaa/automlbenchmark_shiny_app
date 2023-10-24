from pathlib import Path
import streamlit as st
import pandas as pd

from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from streamlit_extras.dataframe_explorer import dataframe_explorer

from data_input import show_tables, initialize_data
from sidebar import Navigation, create_sidebar
from shiny import display_shiny_app
import seaborn
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


if __name__ == "__main__":
    configure_streamlit()
    create_sidebar()
    initialize_data()
    show_tables()

    # if tabs == Navigation.ANALYSIS and "raw_data" in st.session_state:
    #     display_shiny_app()
