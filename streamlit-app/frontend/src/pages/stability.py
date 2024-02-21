""" "Adapted" from https://github.com/PGijsbers/amlb-results/blob/main/notebooks/error_visualization.ipynb"""
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


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


def generate_error_table():
    import itertools
    import re

    results = st.session_state.filtered_results
    results["framework"] = results["framework"].apply(get_print_friendly_name)
    results = results[results["framework"] != "NaiveAutoML"]

    with_errors = results[~results["info"].isna()][
        ["framework", "task", "fold", "constraint", "info", "metric", "duration"]]

    TIMEOUT_PATTERN = re.compile("Interrupting thread MainThread \[ident=\d+\] after \d+s timeout.")

    def is_timeout(message: str) -> bool:
        if re.search(TIMEOUT_PATTERN, message):
            return True
        return False

    def is_memory(message: str) -> bool:
        if "Cannot allocate memory" in message:
            return True
        if "exit status 134" in message:
            return True
        if "exit status 137" in message:
            return True
        if "exit status 139" in message:
            return True
        if "exit status 143" in message:
            return True
        if "std::bad_alloc" in message:
            return True
        if "Dummy prediction failed with run state StatusType.MEMOUT" in message:
            return True  # autosklearn
        if "This could be caused by a segmentation fault while calling the function or by an excessive memory usage" in message:
            return True  # lightautoml
        if "OutOfMemoryError: GC overhead limit exceeded" in message:
            return True  # H2O
        return False

    def is_data(message: str) -> bool:
        if "NoResultError: y_true and y_pred contain different number of classes" in message:
            return True
        if "The least populated class in y has only 1 member, which is too few." in message:
            return True  # GAMA
        return False

    def is_implementation(message: str) -> bool:
        if "Unsupported metric `auc` for regression problems" in message:
            return True  # FLAML produces NaN predictions
        if "A pipeline has not yet been optimized. Please call fit() first." in message:
            return True  # TPOT
        if message == "NoResultError: probability estimates are not available for loss='hinge'":
            return True  # TPOT
        if "object has no attribute 'predict_proba'" in message:
            return True  # TPOT
        if "'NoneType' object is not iterable" in message:
            return True  # GAMA
        if message == "NoResultError: ":
            return True  # GAMA
        if "Ran out of input" in message:
            return True  # GAMA
        if "Python int too large to convert to C ssize_t" in message:
            return True  # GAMA
        if "invalid load key, " in message:
            return True  # GAMA
        if "Pipeline finished with 0 models for some reason." in message:
            return True  # Light AutoML
        if "No models produced. \nPlease check your data or submit" in message:
            return True  # MLJar
        if "Object of type float32 is not JSON serializable" in message:
            return True  # MLJar
        if "The feature names should match those that were passed during fit" in message:
            return True  # MLJar
        if re.search("At position \d+ should be feature with name", message):
            return True  # MLJar
        if "Ensemble_prediction_0_for_" in message:
            return True  # MLJar
        if "NeuralNetFastAI_BAG_L1'" in message:
            return True  # AutoGluon
        if "No learner was chosen in the initial phase." in message:
            return True  # NaiveAutoML
        return False

    def confirmed_fixed(message: str) -> bool:
        if "'NoneType' object has no attribute 'name'" in message:
            return True  # bug with infer_limit set in 0.8.0, fixed in 0.8.3.
        return False

    checks = dict(
        timeout=is_timeout,
        memory=is_memory,
        data=is_data,
        implementation=is_implementation,
        fixed=confirmed_fixed,
    )

    def classify_error(message: str):
        for type_, check in checks.items():
            if check(message):
                return type_
        return "unknown"

    with_errors["error_type"] = with_errors["info"].apply(classify_error)
    error_counts = with_errors.groupby(["framework", "error_type"], as_index=False).count()
    frameworks = list(with_errors.groupby("framework").count().task.sort_values(ascending=False).index)
    error_types = error_counts["error_type"].unique()

    all_combinations = pd.DataFrame(itertools.product(error_types, frameworks), columns=["error_type", "framework"])
    error_counts = pd.concat([error_counts, all_combinations]).drop_duplicates(subset=["error_type", "framework"],
                                                                               keep='first')
    error_counts = error_counts.fillna(0)
    return error_counts

def plot_error_type_by_framework(error_counts, include_types: list[str]):
    frameworks = error_counts.groupby("framework").sum()["info"].sort_values(ascending=False).index
    error_types = error_counts["error_type"].unique()
    color_by_error_type = {
        "data": "#a6cee3",  # light blue
        "implementation": "#2078b4",  # dark blue
        "memory": "#A7CE85",  # light green
        "timeout": "#32a02d",  # dark green
        "rerun": "#999999",
        "investigate": "#cccccc",
        "fixed": "#fe9900",
    }
    assert all(error in color_by_error_type for error in error_types)

    color_by_error_type = {k: v for k, v in color_by_error_type.items() if k in error_types}

    errors_by_framework = {
        error_type: [
            error_counts[(error_counts["error_type"] == error_type) & (error_counts["framework"] == framework)][
                "info"].iloc[0]
            for framework in frameworks
        ]
        for error_type in color_by_error_type
    }

    fig, ax = plt.subplots()

    bottoms = np.zeros(len(frameworks))
    for error_type, counts in errors_by_framework.items():
        ax.bar(frameworks, counts, label=error_type, bottom=bottoms, width=.6, color=color_by_error_type[error_type])
        bottoms += counts

    ax.set_ylim([0, max(bottoms) + 20])
    ax.set_ylabel("count")
    ax.tick_params(axis="x", which="major", rotation=-90)
    ax.legend(loc="upper right")
    ax.set_title("Error types by framework")
    st.pyplot(fig)


if __name__ == "__main__":
    st.write(
        """
        # Stability
        
        In this page, we take a look at the stability of the AutoML frameworks.
        This corresponds to Section 6.4 from our paper.
        We look at the frequency and type of errors encountered, but also
        evaluate how well the AutoML frameworks observe the provided time constraint.
        """
    )
    with st.expander("Does training time stability matter?"):
        st.write(
            """
            Yes, in some cases having a stable well-behaved AutoML framework matters, in others, not so much.
            For example, if you simply want to build a model once, then it may not matter to you.
            You can invoke the training procedure multiple times, until it runs to completion, or
            evaluate the use of other AutoML framework.
            
            On the other hand, if you want to use the AutoML framework regularly, e.g., to retrain models 
            on a daily basis, or tackle many different problems with them, then it may be very disruptive to
            have a system which is not well-behaved.
            """
        )

    st.write(
        """
        ## Errors
        
        Here, we look at the errors we encounter while running our experiments.
        The logs reveal that the most errors happen during training time, and rarely during inference time.
        """
    )
    with st.expander("What do the categories mean?"):
        st.write("copy from paper")
    with st.expander("Why so many errors?"):
        st.write(
            """
            Engineering a well-behaved AutoML framework is hard for several reasons.
            First, it needs to handle all kind of different input data.
            
            ...
            
            Second, you build on the work of others, ..., which may have different design goals of philosophies.
            
            ...
            
            This makes sense as it is the longest phase with the most components, such as data preprocessing, evaluation of
            various ML pipelines, building ensembles, and more. Many implementations that AutoML frameworks
            build on are not well-behaved themselves: they may freeze, generate segmentation faults, and so on.
            """
        )
    with st.expander("Why are most errors during training?"):
        st.write(
            """
            See "Why so many errors?" for the many reasons making a well-behaved AutoML framework is hard.
            Most of that complexity is encountered during the training phase.
            If an AutoML framework successfully finishes training, it likely already found a pipeline which
            can handle inference on the data: that was already part of the pipeline evaluation process!
            
            Additionally, if an AutoML framework crashes during training it can not also crash during inference, 
            because that is no longer run. So, even if a hypothetical framework would crash 50% of the time during
            training and 50% during inference, you would expect only half as many failures during inference time.
            """
        )

    r = generate_error_table()
    left, right = st.columns([0.7, 0.3])
    with right:
        error_types_bar = st.multiselect(
            label="Include Error Types:",
            options=r["error_type"].unique(),
            default=r["error_type"].unique(),
        )
        frameworks_bar = st.multiselect(
            label="Include Frameworks:",
            options=r["framework"].unique(),
            default=r["framework"].unique(),
        )
    with left:
        r = r[r["error_type"].isin(error_types_bar)]
        r = r[r["framework"].isin(frameworks_bar)]
        plot_error_type_by_framework(r, include_types=error_types_bar)
    st.write(
        """
        ## Training Duration
        
        Here, we look at time the AutoML framework used to build a model.
        Each framework was configured to make the most use of the given time.
        We tested the frameworks at two different time constraints: 1 hour and 4 hours.
        """
    )