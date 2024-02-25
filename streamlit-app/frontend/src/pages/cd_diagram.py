from autorank import autorank, plot_stats
import streamlit as st
import matplotlib.pyplot as plt

from core.data import preprocess_data, get_print_friendly_name

st.write("# CD")
constraint = st.selectbox(
    label="Time",
    options=["1 hour", "4 hours"],
    index=0,
)
constraint = {"1 hour": "1h8c_gp3", "4 hours": "4h8c_gp3"}[constraint]
ttype = st.selectbox(
    label="Task Type",
    options=["Binary", "Multiclass", "Regression", "All"],
    index=0,
)
metric = {"Binary": ["auc"], "Multiclass": ["neg_logloss"], "Regression": ["neg_rmse"], "All": ["auc", "neg_logloss", "neg_rmse"]}[ttype]
mean_results = st.session_state.filtered_results.copy()
mean_results["framework"] = mean_results["framework"].apply(get_print_friendly_name)
mean_results = preprocess_data(mean_results)
frameworks_to_exclude = ["autosklearn2", "NaiveAutoML"]
if "neg_rmse" in metric and constraint == "4h8c_gp3":
    frameworks_to_exclude.extend(["MLJAR(P)", "AutoGluon(HQ)", "AutoGluon(HQIL)"])
mean_results = mean_results[~mean_results["framework"].isin(frameworks_to_exclude)]
mean_results = mean_results[(mean_results["constraint"] == constraint) & (mean_results["metric"].isin(metric))]
mean_results = mean_results[["framework", "task", "result"]]
mean_results = mean_results.pivot(index="task", columns="framework", values="result")
result = autorank(
    mean_results,
)
fig, ax = plt.subplots(1, 1, figsize=(10, 8))
plot_stats(result, ax=ax)
# from pages._copycd import cd_evaluation
# _, fig = cd_evaluation(mean_results, maximize_metric=True)
st.pyplot(fig)
