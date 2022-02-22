tabpanel_overview = fluidPage(theme = shinytheme("united"),
  sidebarLayout(
    sidebarPanel(width = 3,
      div(align = "center",
        fileInput("manual_data", "Choose CSV File",
          multiple = TRUE,
          accept = c("text/csv",
            "text/comma-separated-values,text/plain",
            ".csv")),
        uiOutput("overview_data_ui"),
        uiOutput("overview_task_ui"),
        uiOutput("overview_measure_ui"),
        p("X-Axis limits"),
        uiOutput("plot_ranges_ui"),
        uiOutput("overview_checkboxes_ui")
      )
    ),
    mainPanel(width = 9,
      div(align = "center",
        conditionalPanel(
          condition = "output.overview_plot_type",
          withSpinner(plotlyOutput("overview_plot_all", height = "780px"))
        ),
        conditionalPanel(
          condition = "!output.overview_plot_type",
          withSpinner(plotOutput("overview_plot_task", height = "780px"))
        )
      )
    )
  )
)
