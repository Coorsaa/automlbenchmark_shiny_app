##### Analysis #####
values = reactiveValues(
  # scores_1h = NULL,
  # scores_4h = NULL,
  # scores_8h = NULL,
  # w_1h = NULL,
  # w_4h = NULL,
  # w_8h = NULL
  show_plotly_overview = TRUE
)

observe({
  values$data = preprocData(read.csv("data/final_results.csv", stringsAsFactors = TRUE))
  values$chars = readRDS("data/task_list.RDS")
  values$overview_plot_data = NULL
  # values$w_1h = readRDS("data/w_1h.RDS")
  # values$w_4h = readRDS("data/w_4h.RDS")
  # values$w_8h = readRDS("data/w_8h.RDS")
})

observeEvent(input$manual_data, {
  data = read.csv(input$manual_data$datapath,
    stringsAsFactors = TRUE
  )

  values$data = preprocData(data)
})

data = reactive({
  reqAndAssign(input$overview_data_select, "time")

  data = values$data %>%
    filter(time == !!time)
  data$id = as.integer(str_replace(data$id, "openml.org/t/", ""))
  return(data)
})

task_names = reactive({
  d = data()
  levels(d$task)
})

regression_tasks = reactive({
  d = data()
  levels(droplevels(d[d$type == "regression", "task"]))
})

multiclass_tasks = reactive({
  d = data()
  levels(droplevels(d[d$type == "multiclass", "task"]))
})

ms_available = reactive({
  # reqAndAssign(input$task, "task")
  task = input$task
  mc = isolate(multiclass_tasks())
  regr = isolate(regression_tasks())
  # reqAndAssign(task_names(), "tn")
  tn = task_names()

  if (task %in% c("Multiclass", mc)) {
    c("acc", "balacc", "logloss")
  } else if (task %in% c("Binary + Multiclass")) {
    c("acc", "balacc", "logloss")
  } else if (task %in% c("Regression", regr)) {
    c("mae", "rmse", "r2")
  } else {
    c("acc", "balacc", "auc", "logloss")
  }
})


output$overview_data_ui = renderUI({
  data = values$data
  list(
    fluidRow(
      column(12,
        sliderTextInput(inputId = "overview_data_select",
          label = "Select Results for (tuning time)",
          choices = levels(data$time),
          selected = levels(data$time)[1]
        )
      )
    )
  )
})

overview_default_measure =  reactive({
  reqAndAssign(input$task, "task_type")
  if (task_type %in% c("Multiclass", "Binary + Multiclass")  | task_type %in% multiclass_tasks()) {
    return("logloss")
  } else if (task_type == "Regression" | task_type %in% regression_tasks()) {
    return("rmse")
  } else {
    return("auc")
  }
})

output$overview_task_ui = renderUI({
  tn = task_names()

  fluidRow(
    column(12, align = "center",
      selectInput("task", "Choose a task",
        choices = c(setdiff(task_types_available(), "All"), tn)
      )
    )
  )
})

output$overview_measure_ui = renderUI({
  ms = ms_available()

  fluidRow(
    column(12, align = "center",
      selectInput("measure", "Choose a measure", choices = ms, selected = overview_default_measure())
    )
  )
})

frameworks_available = reactive({
  d = data()
  levels(d$framework)
})

output$overview_frameworks_ui = renderUI({

  fluidRow(
    column(12, align = "center",
      selectInput("measure", "Choose a measure", choices = ms)
    )
  )
})

output$overview_checkboxes_ui = renderUI({
  fw = frameworks_available()
  list(
    fluidRow(
      column(12, align = "center",
        prettyCheckbox(inputId = "overview_aggregate",
          label = "Aggregate",
          value = isolate(input$overview_aggregate),
          status = "info", shape = "round", animation = "pulse"),
      ),
      column(1),
      column(10, align = "left",
        prettyCheckboxGroup(inputId = "overview_frameworks",
          label = "Frameworks",
          choices = fw,
          selected = fw,
          status = "info", shape = "round", animation = "pulse")
      )
    )
  )
})


use_limits_default = reactiveVal(TRUE)
observeEvent(input$plot_min, ignoreInit = TRUE, {
  use_limits_default(FALSE)
})


output$plot_ranges_ui = renderUI({
  d = values$overview_plot_data
  if (!is.null(d)) {
    min_value = if (use_limits_default()) 0 else isolate(input$plot_min)
    max_value = if (use_limits_default()) max(na.omit(d[, 3])) else isolate(input$plot_max)
    list(
      fluidRow(
        column(6, align = "center",
          numericInput(inputId = "plot_min", label = "min", value = min_value)
        ),
        column(6, align = "center",
          numericInput(inputId = "plot_max", label = "max", value = max_value)
        ),
        column(12, align = "center",
          prettyCheckbox(inputId = "plot_logscale",
            value = isolate(input$plot_logscale),
            label = "logscale (base 10)",
            status = "info", shape = "round", animation = "pulse")
        )
      )
    )
  }
})

observeEvent(input$task, {
  d = overview_plot_data()
  updateNumericInput(session, "plot_min", value = 0)
  updateNumericInput(session, "plot_max", value = max(na.omit(d[, 3])))
})

observeEvent(input$measure, {
  d = overview_plot_data()
  updateNumericInput(session, "plot_min", value = 0)
  updateNumericInput(session, "plot_max", value = max(na.omit(d[, 3])))
})


overview_plot_data = reactive({
  t = input$task
  reqAndAssign(input$measure, "ms")
  mc = multiclass_tasks()
  regr = regression_tasks()
  fw = input$overview_frameworks
  aggregate = input$overview_aggregate
  data = isolate(data())
  if (t == "Multiclass") {
    d = data[data$task %in% mc,]
    # values$show_plotly_overview = TRUE
  } else if (t == "Binary") {
    d = data[data$task %nin% mc,]
    # values$show_plotly_overview = TRUE
  } else if (t == "Binary + Multiclass") {
    d = data
    # values$show_plotly_overview = TRUE
  } else if (t == "Regression") {
    d = data[data$task %in% regr,]
    # values$show_plotly_overview = TRUE
  } else {
    d = data[data$task == t,]
    # values$show_plotly_overview = FALSE
  }

  d = d[d$framework %in% fw,]
  d$framework = droplevels(d$framework)
  d = removeDuplicates(d, ms)

  if (aggregate == TRUE) {
    d = d %>%
      group_by(task, framework) %>%
      summarise(value = mean(get(ms), na.rm = TRUE))
    colnames(d)[3] = ms
  } else {
    d = d %>%
      select(task, framework, one_of(ms))
  }

  values$overview_plot_data = d
  return(d)
})

overview_plot = reactive({
  d = overview_plot_data()
  reqAndAssign(input$measure, "ms")
  reqAndAssign(input$plot_min, "min")
  reqAndAssign(input$plot_max, "max")
  logscale = input$plot_logscale

  p = ggplot(d, aes(x = task, y = get(ms), col = framework)) +
  geom_point(aes(group = framework), position = position_jitterdodge()) + #geom_boxplot() +
  # geom_jitter(aes(group = framework), size = 2, alpha = 0.5, width = 0.2) +
    # ylim(c(0, 1e1)) +
    ylab("Value") +
    theme_minimal() +
    ylim(min, max) +
    coord_flip()

  if (logscale) {
    p = p + scale_y_continuous(trans = "log10")
  }

  if (t %nin% c("Binary", "Multiclass", "Binary + Multiclass", "Regression")) {
    p2 = ggdensity(d, x = ms,
      add = "mean", rug = TRUE,
      color = "framework",
      fill = "framework") +
    # ylim(c(0, 5)) +
    theme_minimal()

    # comparisons = combn(levels(data$framework), 2)
    # comparisons = lapply(apply(comparisons, 2, as.list), unlist)
    p3 = ggboxplot(d,
      x = "framework",
      y = ms,
      color = "framework",
      add = "jitter") +
    # stat_compare_means(comparisons = comparisons) +
    # stat_compare_means() +
    theme_minimal()

    p = p3 + (p / p2)
    # p = p + p2
  }
  return(p)
})

output$overview_plot_all = renderPlotly({
  reqAndAssign(input$task, "t")
  if (t %in% c("Binary", "Multiclass", "Binary + Multiclass", "Regression")) {
    values$show_plotly_overview = TRUE
    p = overview_plot()
    return(ggplotly(p))
  } else {
    values$show_plotly_overview = FALSE
    return(NULL)
  }
})

output$overview_plot_task = renderPlot({
  reqAndAssign(input$task, "t")
  if (t %nin% c("Binary", "Multiclass", "Binary + Multiclass", "Regression")) {
    values$show_plotly_overview = FALSE
    p = overview_plot()
    return(p)
  } else {
    values$show_plotly_overview = TRUE
    return(NULL)
  }
})

show_plotly_overview = reactive({
  return(values$show_plotly_overview)
})

 observe({
    if (show_plotly_overview() == TRUE) {
      shinyjs::show("overview_plot_all")
      shinyjs::hide("overview_plot_task")
    } else {
      shinyjs::show("overview_plot_task")
      shinyjs::hide("overview_plot_all")
    }
  })
