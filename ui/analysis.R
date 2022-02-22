tabpanel_data = fluidPage(theme = shinytheme("united"),
  mainPanel(width = 12,
    fluidRow(
      dataTableOutput("analysis_data")
    )
  )
)

tabpanel_analysis = fluidPage(theme = shinytheme("united"),
  sidebarLayout(
    sidebarPanel(width = 3,
      div(align = "center",
        selectInput("analysis_method", "Choose Method", choices = c("Critical Difference Tests" = "tests", "Bradley Terry Trees" = "trees"),
          selected = "Critical Difference Tests"),
        uiOutput("analysis_task_type_ui"),
        uiOutput("analysis_measure_ui"),
        conditionalPanel(
          condition = "input.analysis_method == 'tests'",
            #selectInput("analysis_test", "Choose Test", choices = c(
          # "Friedman test" = "friedman",
          # "Bonferroni - Dunn test" = "bonferroni",
          #  "Bayesian Hierarchical test" = "bayes",
          #  "Nemenyi test" = "nemenyi"
          #), selected = "nemenyi"),
          sliderInput("test_alpha", "Significance Level", min = 0.01, max = 0.2, step = 0.01, value = 0.05)
        ),
        conditionalPanel(
          condition = "input.analysis_method == 'trees'",
          uiOutput("analysis_tree_ui"),
          uiOutput("selected_chars")
        ),
        uiOutput("analysis_checkboxes_ui"),
        downloadButton("download_cd_plot")
      )
    ),
    mainPanel(width = 9,
      fluidRow(
        #conditionalPanel(
        #  condition = "input.analysis_method == 'models'",
        #  plotOutput("analysis_models_plot", height = "780px")
        #),
        conditionalPanel(
          condition = "input.analysis_method == 'tests'",
          # dataTableOutput("analysis_test_table"),
          #conditionalPanel(
          #  condition = "input.analysis_test == 'nemenyi'",
          withSpinner(plotOutput("analysis_cd_plot", height = "780px")),
          #),
          # conditionalPanel(
          #   condition = "input.analysis_test == 'bayes'",
          #   tableOutput("analysis_bayes_test")
          # )
        ),
        conditionalPanel(
          condition = "input.analysis_method == 'trees'",
          plotOutput("tree_plot", height = "780px")
        )
      )
    )
  )
)
