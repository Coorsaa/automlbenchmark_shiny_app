library(shiny)
library(shinydashboard)
library(shinyjs)
library(plotly)
library(shinyBS)
library(shinyWidgets)
library(markdown)
library(shinythemes)
library(shinycssloaders)
library(shinybusy)

source("./helpers/helpers_ui.R", local = TRUE)$value

ui.files = list.files(path = "./ui", pattern = "*.R")
ui.files = paste0("ui/", ui.files)

for (i in seq_along(ui.files)) {
  source(ui.files[i], local = TRUE)
}

shinyUI(
  tagList(
    useShinyjs(),
    add_busy_spinner(
      spin = "semipolar",
      color = "#0F82E6",
      position = "top-right",
      margins = c(100, 100),
      onstart = FALSE
    ),
    loading.screens,
    div(id = "app-content",
      navbarPage(title = div(img(src = "openml.png", height = 35)),
        theme = shinytheme("united"), id = "top-nav",
        tabPanel("Info", tabpanel_info,
          icon = icon("info")),
        tabPanel("Overview", tabpanel_overview,
          icon = icon("wrench")),
        navbarMenu("Statistical Analysis", icon = icon("graduation-cap"),
          tabPanel("Data", tabpanel_data),
          tabPanel("Analysis", tabpanel_analysis)
        ),
        tabPanel(title = "hide_me"),
        # tabPanel(title = div(class = "navbarlink-container",
        #   tags$img(height = "20px", alt = "autoxgboost",
        #     src = "hexagon.svg")
        # ), value = "https://github.com/ja-thomas/autoxgboost"),
        tabPanel(title = "", icon = icon("github", "fa-lg"),
          value = "https://github.com"),

        footer = tagList(
          includeScript("scripts/top-nav-links.js"),
          includeScript("scripts/app.js"),
          tags$link(rel = "stylesheet", type = "text/css",
            href = "custom.css"),
          tags$link(rel = "stylesheet", type = "text/css",
            href = "https://fonts.googleapis.com/css?family=Roboto"),
          tags$link(rel = "stylesheet", type = "text/css",
            href = "AdminLTE.css"),
          tags$footer(title = "",
            tags$p(id = "copyright",
              tags$img(icon("copyright")),
              2021,
              tags$a(href = "https://github.com/Coorsaa",
                target = "_blank", "Stefan Coors, "),
              " (Statistical Learning and Data Science, LMU Munich)"
# ),
# tags$p(id = "help_toggler",
#   bsButton(inputId = "show_help", label = "show help",
#     type = "toggle", icon = icon("question-circle"))
            )
          )
        ), windowTitle = "AutoML-Benchmark Analysis"
      )
    )
  )
)
