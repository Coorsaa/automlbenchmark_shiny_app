import streamlit as st
from data_input import show_tables, initialize_data
from sidebar import create_sidebar
from pages.datasets import show_figure, picker

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

    left, right = st.columns(2)
    with left:
        left_container = st.container()
    with right:
        chart_container = st.container()
    initialize_data()
    show_tables(expanded=True)
    picker()
    show_figure(st.session_state.filtered_metadataset, chart_container)
    show_figure(st.session_state.filtered_metadataset, left_container)
