### show data in 'Data' panel
output$analysis_data = renderDataTable({
  reqAndAssign(data(), "d")
  colnames(d) = make.names(colnames(d))
  d
}, options = list(lengthMenu = c(15, 30, 50), pageLength = 15, scrollX = TRUE)
)

task_types_available = reactive({
  d = data()
  lvl = levels(d$type)
  types = character(0L)
  if ("regression" %in% lvl)
    types = c(types, "Regression")
  if ("binary" %in% lvl)
    types = c(types, "Binary")
  if ("multiclass" %in% lvl)
    types = c(types, "Multiclass")
  if ("binary" %in% lvl & "multiclass" %in% lvl)
    types = c(types, "Binary + Multiclass")
  if (length(types > 1) & "Regression" %in% types)
    types = c(types, "All")
  return(types)
})

output$analysis_task_type_ui = renderUI({
  selectInput("task_type", "Choose task type", choices = task_types_available())
})

analysis_measures = reactive({
  if (input$task_type == "Multiclass") {
    c("acc", "balacc", "logloss")
  } else if (input$task_type == "Binary + Multiclass") {
    c("mixed (auc + logloss)" = "result", "acc", "balacc", "logloss")
  } else if (input$task_type == "Regression") {
    c("mae", "rmse", "r2")
  } else if (input$task_type == "All") {
    c("mixed (auc + logloss + rmse)" = "result")
  } else {
    c("acc", "balacc", "auc", "logloss")
  }
})

analysis_default_measure = reactive({
  reqAndAssign(input$task_type, "task_type")
  if (task_type == "Binary") {
    return("auc")
  } else if (task_type == "Regression") {
    return("rmse")
  } else if (task_type == "Binary + Multiclass") {
    return(c("mixed (auc + logloss + rmse)" = "result"))
  } else {
    return("logloss")
  }
})

output$analysis_measure_ui = renderUI({
  selectInput("analysis_measure", "Choose a measure", choices = analysis_measures(), selected = analysis_default_measure())
})

output$analysis_checkboxes_ui = renderUI({
  fw = frameworks_available()
  list(
    fluidRow(
      column(1),
      column(10, align = "left",
        prettyCheckboxGroup(inputId = "analysis_frameworks",
          label = "Frameworks",
          choices = fw,
          selected = fw,
          status = "info", shape = "round", animation = "pulse")
      )
    )
  )
})


output$analysis_models_plot = renderPlot({
  model_plot()
}, res = 300)


### 'Hypothesis Tests' part
### - Nemenyi test


analysis_cdp = reactive({
  reqAndAssign(input$analysis_measure, "ms")
  reqAndAssign(input$test_alpha, "alpha")
  reqAndAssign(input$task_type, "tt")
  reqAndAssign(input$analysis_frameworks, "fw")
  mc = multiclass_tasks()
  regr = regression_tasks()

  data_CD_plot = data()

  data_CD_plot = data_CD_plot[data_CD_plot$framework %in% fw,]
  data_CD_plot$framework = droplevels(data_CD_plot$framework)

  if (tt == "Binary") {
    data_CD_plot = data_CD_plot %>%
      filter(task %nin% c(mc, regr))
  } else if (tt == "Multiclass") {
    data_CD_plot = data_CD_plot %>%
      filter(task %in% mc)
  } else if (tt == "Regression") {
    data_CD_plot = data_CD_plot %>%
      filter(task %in% regr)
  } else if (tt == "Binary + Multiclass") {
    data_CD_plot = data_CD_plot %>%
      filter(task %nin% regr)
  }

  data_CD_plot = removeDuplicates(data_CD_plot, ms)

  data_CD_plot = data_CD_plot %>%
    group_by(framework, task) %>%
    summarize(!!ms := mean(get(ms), na.rm = TRUE)) %>%
    pivot_wider(names_from = "task", values_from = !!ms) %>%
    pivot_longer(cols = !contains("framework"), names_to = "task", values_to = ms, values_drop_na = FALSE) %>%
    droplevels()

  data_CD_plot$task = as.factor(data_CD_plot$task)

  ba = mlr3benchmark::BenchmarkAggr$new(data_CD_plot, "task", "framework")

  par(mar = rep(0, 4))
  if (ms %in% c("logloss", "mae", "rmse")) {
    p = cd_plot(ba$rank_data(minimize = TRUE), meas = ms, p.value = alpha)
  } else {
    p = cd_plot(ba$rank_data(minimize = FALSE), meas = ms, p.value = alpha)
  }
  return(p)
})

output$analysis_cd_plot = renderPlot({
  return(analysis_cdp())
})


output$download_cd_plot = downloadHandler(
  filename = function() {
    if (input$analysis_method == "tests") {
      paste0("cd_plot_", input$task_type, "_", input$analysis_measure, ".pdf")
    } else {
      paste0("bratley_terry_tree", input$task_type, "_", input$analysis_measure, "_depth_", input$analysis_tree_maxdepth, ".pdf")
    }
  },
  content = function(file) {
    if (input$analysis_method == "tests") {
      ggsave(file, plot = analysis_cdp(), device = "pdf", width = 15, height = 10)
    } else {
      pdf(file)
      plotBTTree(bttree(), terminal_panel = node_btplot_angle)
      dev.off()
    }
  }
)


output$analysis_tree_ui = renderUI({
  list(
    sliderTextInput(inputId = "analysis_time_select",
      label = "Select Results for (tuning time)",
      choices = levels(values$data$time),
      selected = levels(values$data$time)[1]
    ),
    sliderInput("analysis_tree_maxdepth", "Choose max depth of tree", min = 2L, max = 5L, value = 3L, step = 1L)
  )
})

task_char_data = reactive({
  reqAndAssign(input$analysis_time_select, "time")
  reqAndAssign(tolower(input$task_type), "type")

  data = values$data %>%
    filter(time == !!time)

  # negate logloss for preference directions
  data$logloss = -data$logloss
  data$rmse = -data$rmse
  data$mae = -data$mae
  if (type %nin% c("binary + multiclass", "all")) {
    data = data %>%
      filter(type == !!type)
  } else if (type == "binary + multiclass") {
    data = data %>%
      filter(type == "binary" | type == "multiclass")
  }

  data$id = as.integer(str_replace(data$id, "openml.org/t/", ""))

  reqAndAssign(input$analysis_frameworks, "fw")
  data = data[data$framework %in% fw, ]
  data$framework = droplevels(data$framework)

  chars = values$chars %>%
    # filter(task.id %in% unique(data$id)) %>%
    droplevels() %>%
    select(-status, - format, - estimation.procedure, -target.feature,
      - evaluation.measures, - cost.matrix, - source.data.labeled,
      - target.feature.event, - target.feature.left, - target.feature.right,
      - quality.measure) %>%
    mutate(
      rel.majority.class.size = majority.class.size / number.of.instances,
      rel.minority.class.size = minority.class.size / number.of.instances,
      ratio.of.instances.with.missing.values = number.of.instances.with.missing.values / number.of.instances,
      ratio.of.missing.values = number.of.missing.values / (as.numeric(number.of.instances) * as.numeric(number.of.features)),
      ratio.of.numeric.features = number.of.numeric.features / number.of.features,
      ratio.nominal.att.distinct.values = max.nominal.att.distinct.values / number.of.instances,
      imbalance.ratio = majority.class.size / minority.class.size
    ) %>%
    select(
      - majority.class.size,
      - minority.class.size,
      - number.of.instances.with.missing.values,
      - number.of.missing.values,
      - number.of.numeric.features,
      - number.of.symbolic.features,
      - max.nominal.att.distinct.values
    )

    if (type %in% c("regression", "all")) {
      chars = chars %>% select(
        - rel.majority.class.size,
          - rel.minority.class.size,
          - imbalance.ratio,
          - number.of.classes
      )
    }

    if (type != "all") {
    chars = chars %>% select(
      - task.type
    )
  }

    list(data = data, chars = chars)
})

bttree = reactive({
  reqAndAssign(input$analysis_measure, "ms")
  reqAndAssign(input$analysis_tree_maxdepth, "maxdepth")
  cd = task_char_data()
  data = cd$data
  chars = cd$chars
  bt = getBtTree(data, chars, ms, maxdepth)
  return(bt)
})

output$tree_plot = renderPlot({
  plotBTTree(bttree(), terminal_panel = node_btplot_angle)
})