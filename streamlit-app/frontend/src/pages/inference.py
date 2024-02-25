import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn
from core.data import get_print_friendly_name, preprocess_data, impute_results, is_old

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
        figsize=(8, 4),
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

st.write("Inference and Performance")
def calculate_pareto(xs, ys) -> list[tuple[float, float]]:
    pairs = set(zip(xs, ys))
    return [
        (x, y)
        for x, y in pairs
        # check below is only correct because `pairs` is a set, so never x==x2 *and* y==y2
        if not any((x2>=x and y2 >=y) and (x!=x2 or y!=y2) for x2, y2 in pairs)
    ]

def plot_pareto(data, x, y, ax, color="#cccccc"):
    pareto = sorted(calculate_pareto(data[x], data[y]))
    for opt, next_opt in zip(pareto, pareto[1:]):
        ax.plot([opt[0], opt[0], next_opt[0]], [opt[1],next_opt[1], next_opt[1]], color=color, zorder=0)

def plot_scatter(mean_results, constraint, metric, time_budget):
    ttype = {"neg_rmse": "regression", "auc": "binary classification", "neg_logloss": "multiclass classification"}[metric]
    exclude = ["constantpredictor", "RandomForest", "TunedRandomForest", "TPOT"]
    if ttype == "regression":
        exclude += ["autosklearn2"]

    data = mean_results[~mean_results["framework"].isin(exclude)]
    data = data[(data["constraint"] == constraint)  & (data["metric"] == metric)]
    data = data.groupby(["framework", "constraint", "metric"])[["infer_batch_size_file_10000", "scaled"]].median()
    data["row_per_s"] = 10_000. / data["infer_batch_size_file_10000"]
    color_map = {k: v for k, v in FRAMEWORK_TO_COLOR.items() if k not in exclude}

    fig, ax = plt.subplots(1, 1, figsize=(8,8))
    ax = seaborn.scatterplot(
        data,
        x="row_per_s",
        y="scaled",
        hue="framework",
        palette=color_map,
        s=70,  # marker size
        ax=ax,
    )
    plot_pareto(data, x="row_per_s", y="scaled", ax=ax)
    ax.set_title(f"{ttype} {time_budget}")
    ax.set_xscale('log')
    ax.set_xlabel('median rows per second')
    ax.set_ylabel('median scaled performance')
    seaborn.move_legend(ax, "upper right", bbox_to_anchor=(1.6, 1))
    st.pyplot(fig)

results = st.session_state.filtered_results.copy()
results["framework"] = results["framework"].apply(get_print_friendly_name)
mr = preprocess_data(results)
metric=st.selectbox(
    label="metric",
    options=["neg_rmse", "neg_logloss", "auc"],
    index=0,
)
plot_scatter(mr, "1h8c_gp3",metric, "1 hour")
