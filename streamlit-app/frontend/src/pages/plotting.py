task_type_colormap = {
    "Regression": "#2ba02b",
    "Multiclass Classification": "#fa7f12",
    "Binary Classification": "#1f77b4"
}


def with_large_text(ax, xlabel: str, ylabel: str, title: str):
    ax.set_title(title, size='xx-large')
    ax.set_ylabel(ylabel, size='xx-large')
    ax.set_xlabel(xlabel, size='xx-large')
    ax.tick_params(axis='both', which='both', labelsize=18)
