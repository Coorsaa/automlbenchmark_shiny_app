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