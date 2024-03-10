import streamlit as st
import matplotlib.pyplot as plt
import seaborn
from core.data import get_print_friendly_name, preprocess_data, impute_results, is_old
from core.visualization import FRAMEWORK_TO_COLOR, box_plot
from core.ui import write_card, filters


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
st.write(
    """
    Inference time denotes the time the model built by the AutoML framework takes to generate predictions.
    How long inference takes depends on a lot of different factors, such as complexity of the models
    (as a rule, large ensembles take more time than a linear model) as well as the underlying machine learning
    libraries the different AutoML frameworks use.
    """
)
write_card(
    body="Many frameworks support optimizing models for inference speed before deployment. This functionality is "
         "not used in this benchmark. Results are meant as a proxy and to demonstrate wide difference beyond just"
         "model performance."
)

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
