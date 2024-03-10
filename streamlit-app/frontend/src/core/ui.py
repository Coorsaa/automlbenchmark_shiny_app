from pathlib import Path
from typing import NamedTuple, Tuple

import streamlit as st

class Filter(NamedTuple):
    constraints: list[str]
    metrics: list[str]
    task_type: str
    instance_range: Tuple[int, int]
    feature_range: Tuple[int, int]


def filters() -> Filter:
    left, right = st.columns([0.5, 0.5])
    with left:
        constraint = st.selectbox(
            label="Time",
            options=["1 hour", "4 hours"],
            index=0,
        )
        constraint = {"1 hour": "1h8c_gp3", "4 hours": "4h8c_gp3"}[constraint]

    with right:
        ttype = st.selectbox(
            label="Task Type",
            options=["Binary", "Multiclass", "Regression"],
            index=0,
        )

    metric = {"Binary": ["auc"], "Multiclass": ["neg_logloss"], "Regression": ["neg_rmse"],
              "All": ["auc", "neg_logloss", "neg_rmse"]}[ttype]
    is_selected_ttype = st.session_state.raw_data["metric"].isin(metric)
    selected_tasks = st.session_state.raw_data[is_selected_ttype]["task"]

    meta = st.session_state.metadataset.copy()
    keep = meta[meta.name.isin(selected_tasks)]
    with left:
        n_range = (
            keep["Number of Instances"].min(),
            keep["Number of Instances"].max()
        )
        # We use a select slider since scaling is hard to get right
        # with continuous values, and this is equally expressive.
        min_n, max_n = st.select_slider(
            "Number of Instances",
            options=sorted(keep["Number of Instances"].unique()),
            value=n_range
        )

    with right:
        n_range = (
            keep["Number of Features"].min(),
            keep["Number of Features"].max()
        )
        min_p, max_p = st.select_slider(
            "Number of Features",
            options=sorted(keep["Number of Features"].unique()),
            value=n_range
        )

    # It's important that users understand how much (or little) data is left after filters, so they can
    # weight the results.
    in_instance_range = (min_n <= keep["Number of Instances"]) & (keep["Number of Instances"] <= max_n)
    in_feature_range = (min_p <= keep["Number of Features"]) & (keep["Number of Features"] <= max_p)
    selected = keep[in_feature_range & in_instance_range]
    st.write(f"Based on above criteria {len(selected)} datasets are selected.")
    return Filter(
        constraints=[constraint],
        task_type=ttype,
        metrics=metric,
        instance_range=(min_n, max_n),
        feature_range=(min_p, max_p),
    )


def write_card(body: str, header: str = "Important", icon: str="⚠️"):
    with open(Path(__file__).parent.parent / "html" / "card.html", 'r') as fh:
        card_html = fh.read()

    warning_html = card_html.replace(
        "ICON", icon
    ).replace(
        "HEADER", header
    ).replace(
        "BODY", body
    )
    st.markdown(
        warning_html,
        unsafe_allow_html=True,
    )
