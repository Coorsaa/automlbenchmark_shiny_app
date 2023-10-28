from typing import NamedTuple
import streamlit as st
from data_input import show_tables, initialize_data
from sidebar import create_sidebar
from pages.datasets import show_figure, picker

__version__ = "0.2"
_repository = "https://github.com/Coorsaa/automlbenchmark_shiny_app/"


class Container(NamedTuple):
    window: "st.DeltaGenerator"
    name: str


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
            kind = st.selectbox(
                label="Kind",
                options=["Histogram", "Bar", "Scatter", "Preset"],
                key=f"kind_{column}",
            )
        with right:
            if kind.casefold() == "preset":
                _ = st.selectbox(
                    label="Figure",
                    options=["1", "2"],
                    key=f"preset_{column}",
                    # help="hello\n**markdown**\nbullet list\n * hello\n * boo\n\ngoobye",
                )
            else:
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

    initialize_data()
    show_tables(expanded=True)

    containers = []
    for i, column in enumerate(columns):
        with column:
            container = create_visualization_container(i)
            containers.append(Container(window=container, name=f"container_{i}"))
            # visualization_function = ... if ... if ...
            # data  = ... if source ...
            plot_container = st.container()
            with st.expander("Plot Options", expanded=True):
                picker(name=f"container_{i}")
            show_figure(
                st.session_state.filtered_metadataset,
                container,
          )

