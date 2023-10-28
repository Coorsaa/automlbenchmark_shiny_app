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


def create_visualization_container(column: int):
    # the column is needed to ensure consistent but unique keys, which are required for
    # the statefulness of the widgets.
    container = st.container()
    with container:
        left, right, _ = st.columns(3)
        with left:
            _ = st.selectbox(
                label="Kind",
                options=["HISTOGRAM", "BAR", "SCATTER"],
                key=f"kind_{column}",
            )
        with right:
            _ = st.selectbox(
                label="Source",
                options=["RESULTS", "DATA"],
                key=f"source_{column}",
                # help="hello\n**markdown**\nbullet list\n * hello\n * boo\n\ngoobye",
            )
    return container


if __name__ == "__main__":
    configure_streamlit()
    create_sidebar()

    columns = st.columns(2, gap="medium")
    containers = []
    for i, column in enumerate(columns):
        with column:
            container = create_visualization_container(i)
            containers.append(container)

    initialize_data()
    show_tables(expanded=True)
    picker()
    show_figure(st.session_state.filtered_metadataset, containers[0])
    show_figure(st.session_state.filtered_metadataset, containers[1])
