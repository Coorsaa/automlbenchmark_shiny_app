from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit_extras.dataframe_explorer import dataframe_explorer


def initialize_data():
    if "raw_data" not in st.session_state:
        _load_default_results()
    if "metadataset" not in st.session_state:
        _load_default_metadata()


def _load_default_results():
    """Loads the 2023 results file."""
    filepath = Path("/Users/pietergijsbers/repositories/amlb-results/data/amlb_all.csv")
    if filepath.exists():
        categorical_features = {
            feature: "category"
            for feature in [
                "id", "task", "framework", "constraint", "type", "metric", "mode", "app_version"
            ]
        }
        st.session_state.raw_data = pd.read_csv(
            filepath,
            dtype=categorical_features,
        )
        st.session_state.filtered_results = st.session_state.raw_data


def _load_default_metadata():
    filepath = Path("/Users/pietergijsbers/repositories/amlb-results/data/metadata.csv")
    if filepath.exists():
        categorical_features = {
            feature: "category"
            for feature in [
                "name", "status", "format",
            ]
        }
        st.session_state.metadataset = pd.read_csv(
            filepath,
            dtype=categorical_features,
        )
        st.session_state.filtered_metadataset = pd.read_csv(filepath)


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
            # TODO: infer file type: results vs metadata?
            st.session_state.raw_data = pd.read_csv(raw_data)


def show_tables(expanded: bool = False):
    """Generates content for the overview page."""
    if "raw_data" not in st.session_state:
        st.text("Please upload a result file from the sidebar on the left.")
        return

    with st.expander("Filter Results", expanded=expanded):
        df = st.session_state.raw_data
        df['framework'] = df['framework'].astype('category')
        filtered_results = dataframe_explorer(df, case=False, key="results")
        st.dataframe(filtered_results, use_container_width=True)
        st.session_state.filtered_results = filtered_results

    with st.expander("Filter Datasets", expanded=expanded):
        filtered_datasets = dataframe_explorer(st.session_state.metadataset, case=False, key="metadata")
        st.dataframe(filtered_datasets, use_container_width=True)
        st.session_state.filtered_metadataset = filtered_datasets


def get_filtered_results():
    """Combines the filtered datasets with the filtered results."""
    selected_tasks = st.session_state.filtered_results["task"].isin(st.session_state.filtered_metadataset["name"])
    return st.session_state.filtered_results[selected_tasks]
