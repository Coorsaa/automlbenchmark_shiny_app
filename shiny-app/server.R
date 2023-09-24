library(DT)
library(dplyr)
library(tidyr)
library(ggplot2)
library(ggpubr)
library(patchwork)
library(OpenML)
library(farff)
library(BBmisc)
library(stringr)
library(data.table)
library(mlr3benchmark)
library(BiocManager)
options(repos = BiocManager::repositories(version = "3.17"))
library(BiocGenerics)
library(Rgraphviz)
library(graph)
library(psychotree)
library(psychotools)
library(partykit)

helper.files = list.files(path = "./helpers", pattern = "*.R")
helper.files = paste0("helpers/", helper.files)

for (i in seq_along(helper.files)) {
  source(helper.files[i], local = TRUE)
}

# By default, the file size limit is 5MB. It can be changed by
# setting this option. Here we'll raise limit to 9MB.
options(shiny.maxRequestSize = 9 * 1024 ^ 2)

shinyServer(function(input, output, session) {
  shinyjs::addClass(id = "mlrlink", class = "navbar-right")

  server.files = list.files(path = "./server", pattern = "*.R")
  server.files = paste0("server/", server.files)
  for (i in seq_along(server.files)) {
    source(server.files[i], local = TRUE)
    updateNavbarPage(session, "top-nav", selected = "Overview")
    hide(id = "loading-content", anim = TRUE, animType = "fade")
    show("app-content")
  }

  session$onSessionEnded(stopApp)
})
