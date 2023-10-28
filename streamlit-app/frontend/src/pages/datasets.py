import re
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn



color_map = {"Regression": "#2ba02b", "Multiclass Classification": "#fa7f12", "Binary Classification": "#1f77b4"}


def with_large_text(ax, xlabel: str, ylabel: str, title: str):
    ax.set_title(title, size='xx-large')
    ax.set_ylabel(ylabel, size='xx-large')
    ax.set_xlabel(xlabel, size='xx-large')
    ax.tick_params(axis='both', which='both', labelsize=18)


def histplot(data: pd.DataFrame, column: str, log_scale: int = 10):
    multiple_types = data["type"].nunique() > 1
    ax = seaborn.histplot(
        data,
        x=column,
        hue="type",
        multiple="stack",
        log_scale=log_scale,
        hue_order=["Regression", "Multiclass Classification", "Binary Classification"],
        palette=color_map,
        shrink=0.8,  # allow some horizontal space between bars
        linewidth=0,  # don't draw lines on edges
        bins=10,
    )
    with_large_text(ax, xlabel=column, ylabel="Datasets", title=f"Datasets by {column}")

    if legend := ax.get_legend():
        if multiple_types:
            legend.set_title("")
        else:
            legend.remove()

    return ax


def picker(dataset: pd.DataFrame, name: str):
    left, right = st.columns(2)
    with left:
        st.session_state.datasets_x_axis = st.selectbox(
            'X-axis',
            dataset.select_dtypes(include="number").columns,
            key=f"x_axis_{name}",
        )
    with right:
        st.session_state.datasets_y_axis = st.selectbox(
            'Y-axis',
            dataset.select_dtypes(include="number").columns,
            key=f"y_axis_{name}",
        )


def scatter_plot(data, x, y, hue: str | None = None, hue_order: list[str] | None = None):
    fig = plt.figure()
    ax = seaborn.scatterplot(
        data,
        x=x,
        y=y,
        hue=hue,
        hue_order=hue_order,
        palette=color_map,
        s=60,
    )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title("Datasets by Data Dimensions", size='xx-large')
    ax.legend().set_title("")
    with_large_text(
        ax,
        xlabel=x,
        ylabel=y,
        title=f"Datasets by {x} and {y}",
    )
    return fig


def show_histogram(dataset: pd.DataFrame, x: str):
    fig = plt.figure()
    ax = histplot(dataset, column=x)
    return fig


def show_figure(data, window):
    if st.session_state.datasets_y_axis == "Count":
        fig = show_histogram(
            data,
            x=st.session_state.datasets_x_axis,
        )
    else:
        fig = scatter_plot(
            data,
            x=st.session_state.datasets_x_axis,
            y=st.session_state.datasets_y_axis,
        )
    window.pyplot(fig)
