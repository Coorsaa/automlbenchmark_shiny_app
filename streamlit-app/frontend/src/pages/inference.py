import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn

FRAMEWORK_TO_COLOR = {
    "AutoGluon(B)": '#fe9900',
    "AutoGluon(HQ)": '#fe7700',
    "AutoGluon(HQIL)": '#fe5500',
    "autosklearn": '#009f81',
    "autosklearn2": '#00fccf',
    "flaml": '#ff5aaf',
    "GAMA(B)": '#8400cd',
    "H2OAutoML": '#ffcb15',
    "lightautoml": '#00c2f9',
    "NaiveAutoML": '#c3c995',
    "MLJAR(B)": '#ffb2fd',
    "MLJAR(P)": '#ddb2fd',
    "RandomForest": "#e20134",
    "TPOT": '#9f0162',
    "TunedRandomForest": '#c4a484',
}

def get_print_friendly_name(name: str, extras: dict[str, str] = None) -> str:
    # Copied from https://github.com/PGijsbers/amlb-results/blob/main/notebooks/data_processing.py
    if extras is None:
        extras = {}

    frameworks = {
        "AutoGluon_benchmark": "AutoGluon(B)",
        "AutoGluon_hq": "AutoGluon(HQ)",
        "AutoGluon_hq_il001": "AutoGluon(HQIL)",
        "GAMA_benchmark": "GAMA(B)",
        "mljarsupervised_benchmark": "MLJAR(B)",
        "mljarsupervised_perform": "MLJAR(P)",
    }
    budgets = {
        "1h8c_gp3": "1 hour",
        "4h8c_gp3": "4 hours",
    }
    print_friendly_names = (frameworks | budgets | extras)
    return print_friendly_names.get(name, name)

def add_horizontal_lines(ax, lines: tuple[tuple[float, str], ...]):
    """Draws horizontal lines specified by (y value, color)-pairs."""
    for y, color in lines:
        ax.axhline(y, color=color)


def box_plot(data, metric=None, ylog=False, title="", ylim=None, figsize=(16, 9), with_framework_names=True,
             add_counts=None, color_map=None):
    """Creates a boxplot with data["frameworks"] on the x-axis and data[`metric`] on the y-axis

    The figure's y-axis may be limited by `ylim` and the number of values outside this limit may be shown in the tick labels.
    """
    if add_counts and (add_counts != "outliers" and not isinstance(add_counts, dict)):
        raise ValueError("`add_counts` must be 'outliers' or a dictionary mapping each framework to a number.")
    def is_old(framework: str, constraint: str, metric: str) -> bool:
        """Encodes the table in `raw_to_clean.ipynb`"""
        if framework == "TunedRandomForest":
            return True
        if constraint == "1h8c_gp3":
            return False
        if framework in ["autosklearn2", "GAMA(B)", "TPOT"]:
            return True
        return framework == "MLJAR(B)" and metric != "neg_rmse"
    color_map = color_map or FRAMEWORK_TO_COLOR
    color_map = {k: v for k, v in color_map.items() if k in data["framework"].unique()}
    metric = metric or data.metric.unique()[0]
    if metric.startswith("neg_"):
        pos_metric = metric[len("neg_"):]
        data[pos_metric], metric = -data[metric], pos_metric

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    seaborn.boxplot(
        data=data,
        x="framework",
        y=metric,
        order=color_map,
        hue="framework",
        palette=color_map if data.constraint.nunique() == 1 else None,
        ax=ax,
        fliersize=1,
    )

    if ylog:
        ax.set_yscale("log")

    ax.set_ylabel(metric, size='xx-large')
    ax.set_xlabel("")
    ax.tick_params(axis='both', which='both', labelsize=18)
    ax.tick_params(axis="x", which="major", rotation=-90)

    if title:
        ax.set_title(title, fontsize=18)

    # Dirty hack for displaying outliers, we overlap minor and major tick labels, where
    # minor labels are used to display the number of outliers, and major tick labels may
    # be used to display the framework names.
    constraint = data.constraint.unique()[0]
    smetric = data.metric.unique()[0]
    frameworks = color_map.keys()
    frameworks = [
        f"{fw if with_framework_names else ''}*" if is_old(fw, constraint, smetric) else fw
        for fw in frameworks
    ]
    if add_counts:
        # There will be minor tick labels displayed for outliers,
        # to avoid rendering on top of each other, we offset the label location
        # with a dirty hack of using leading spaces :-)
        frameworks = [f"   {fw}" for fw in frameworks]
    ax.tick_params(axis="x", which="major", rotation=-90)
    ax.set_xticks(*zip(*enumerate(frameworks)))

    if ylim:
        ax.set_ylim(ylim)
        if add_counts != "outliers":
            print("Warning! Ylim is set but outliers are not reported.")

    counts = []
    if add_counts:
        if add_counts == "outliers":
            add_counts = {}
            for framework in color_map:
                framework_outliers = data[(data["framework"] == framework) & (data[metric] < ylim[0])]
                add_counts[framework] = f"{len(framework_outliers)}"

        # We need to offset the minor tick labels, otherwise they won't render.
        ax.set_xticks(
            ticks=[i - 0.01 for i in range(len(color_map))],
            labels=[f"[{add_counts.get(f, 'x')}]" for f in color_map],
            minor=True
        )

    return fig, ax

def plot_inference_barplot(results, constraint, col):
    data = results[results["constraint"] == constraint].copy()
    # data = data[~data["framework"].isin(["constantpredictor", "TPOT"])]

    data["timeout"] = data["info"].apply(lambda msg: isinstance(msg, str) and "Interrupting thread MainThread" in msg)
    data["row/s"] = 10_000 / data[col]

    fig, ax = box_plot(
        data,
        metric="row/s",
        title=f"From-Disk Batch Inference Speed",
        figsize=(6, 3),
        add_counts=False,#timeout_counts,
        with_framework_names=True, # ttype == "regression",
    )
    ax.set_ylabel("rows per second")
    ax.set_yscale("log")
    st.pyplot(fig)

st.write("# Inference Time")
results = st.session_state.filtered_results.copy()
results["framework"] = results["framework"].apply(get_print_friendly_name)
results = results[~results["framework"].isin(["TPOT", "NaiveAutoML", "constantpredictor", "TunedRandomForest"])]
# The framework category still remembers the frameworks were once there in the category metadata
results["framework"] = results["framework"].astype('string').astype('category')
left, right = st.columns([0.8,0.2])
with left:
    plot_inference_barplot(results, constraint="1h8c_gp3", col="infer_batch_size_file_10000")
with right:
    st.write("controls")

left, right = st.columns([0.8,0.2])

with left:
    plot_inference_barplot(results, constraint="1h8c_gp3", col="infer_batch_size_df_1")
with right:
    st.write("controls")
