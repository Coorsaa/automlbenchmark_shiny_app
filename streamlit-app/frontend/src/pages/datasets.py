import re
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn

features = ["NumberOfClasses", "NumberOfFeatures", "NumberOfInstances",
            "NumberOfInstancesWithMissingValues", "NumberOfMissingValues",
            "NumberOfSymbolicFeatures"]

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


def name_with_space(name: str) -> str:
    words = re.findall(r"([A-Z][a-z]+)", name)
    return ' '.join(
        word if word not in ['Of', 'With'] else word.lower() for word in words)


def determine_task_type(number_of_classes: int) -> str:
    if number_of_classes == 2:
        return "Binary Classification"
    if number_of_classes > 2:
        return "Multiclass Classification"
    return "Regression"


def picker():
    left, right = st.columns(2)
    with left:
        st.session_state.datasets_x_axis = st.selectbox(
            'X-axis',
            (
                'Number of Classes',
                'Number of Instances',
                'Number of Features',
            )
        )
    with right:
        st.session_state.datasets_y_axis = st.selectbox(
            'Y-axis',
            (
                'Count',
                'Number of Classes',
                'Number of Instances',
                'Number of Features',
            )
        )


def scatter_plot(data, x, y):
    datasets = data[features].rename(
        columns={feature: name_with_space(feature) for feature in features}
    )

    datasets["type"] = datasets["Number of Classes"].apply(determine_task_type)
    datasets["Percentage of Categorical Features"] = (datasets[
                                                          "Number of Symbolic Features"] /
                                                      datasets["Number of Features"]) * 100
    datasets["Percentage of Missing Values"] = (datasets["Number of Missing Values"] / (
                datasets["Number of Instances"] * datasets["Number of Features"])) * 100
    fig = plt.figure()
    ax = seaborn.scatterplot(
        datasets,
        x=x,
        y=y,
        hue="type",
        hue_order=["Regression", "Multiclass Classification", "Binary Classification"],
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


def show_histogram(metadata: pd.DataFrame, x: str):
    datasets = metadata[features].rename(
        columns={feature: name_with_space(feature) for feature in features}
    )

    datasets["type"] = datasets["Number of Classes"].apply(determine_task_type)
    datasets["Percentage of Categorical Features"] = (datasets[
                                                          "Number of Symbolic Features"] /
                                                      datasets["Number of Features"]) * 100
    datasets["Percentage of Missing Values"] = (datasets["Number of Missing Values"] / (
                datasets["Number of Instances"] * datasets["Number of Features"])) * 100

    fig = plt.figure()
    ax = histplot(datasets, column=x)
    return fig


def show_figure(data):
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
    st.pyplot(fig)


picker()
show_figure(st.session_state.filtered_metadataset)