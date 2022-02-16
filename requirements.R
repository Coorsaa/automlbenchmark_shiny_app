packages = c(
  "shiny",
  "shinydashboard",
  "shinyjs",
  "plotly",
  "shinyBS",
  "shinyWidgets",
  "markdown",
  "shinythemes",
  "DT",
  "dplyr",
  "tidyr",
  "ggplot2",
  "ggpubr",
  "patchwork",
  "OpenML",
  "farff",
  "BBmisc",
  "stringr",
  # "scmamp",
  "partykit",
  "data.table",
  "mlr3benchmark"
)

for (p in packages) {
  if (!requireNamespace(p, quietly = TRUE))
    install.packages(p)
}

bioc_packages = c(
  "BiocManager",
  "BiocGenerics",
  "Rgraphviz",
  "graph",
  "psychotree",
  "psychotools"
)

for (p in bioc_packages) {
  if (!requireNamespace(p, quietly = TRUE))
    BiocManager::install(p)
}
