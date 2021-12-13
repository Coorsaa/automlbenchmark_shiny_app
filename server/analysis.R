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

# model_plot = reactive({
#   # reqAndAssign(input$task_type, "type")
#   reqAndAssign(input$analysis_measure, "ms")
#   reqAndAssign(input$drop_framework, "drop")
#   reqAndAssign(input$model_type, "mt")
#   reqAndAssign(data(), "data")

#   if ("None" %in% drop) {
#     d = getFilteredData(data, ms)
#   } else {
#     d = getFilteredData(data, ms, drop)
#   }

  #if (mt == "bttree") {
  #  d_wide = pivot_wider(d, names_from = "framework", values_from = ms)
  #  model = bttree(as.formula(paste0(ms, " ~ .")), d)
  #  plot(model)
  #} # else if (mt == "rpart") {
  #   task = TaskRegr$new("regression_task", backend = d, target = ms)
  #   learner = lrn("regr.rpart")
  #   learner$train(task)
  #   model = learner$model
  #   d$node = model$where
  #   table(d$node, d$framework)
  #   # rpart.plot(learner$model, roundint = FALSE)
  # }
# })

# output$drop_framework_text = renderText({
#   reqAndAssign(input$drop_framework, "drop")
#   drop
# })

output$analysis_models_plot = renderPlot({
  model_plot()
}, res = 300)


### 'Hypothesis Tests' part
### includes several tests on average ranks
### - Friedman test
### - Nemenyi test
# output$analysis_test_table = renderDataTable({

# })

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
    summarize(mean_measure = mean(get(ms))) %>%
    pivot_wider(names_from = "framework", values_from = mean_measure) %>%
    as.data.frame()
  rownames(data_CD_plot) = as.character(data_CD_plot$task)
  data_CD_plot = dropNamed(data_CD_plot, "task")

  par(mar = rep(0, 4))
  if (ms %in% c("logloss", "mae", "rmse")) {
    p = plotCD(data_CD_plot, alpha = alpha, decreasing = FALSE, cex = 1.5)
  } else {
    p = plotCD(data_CD_plot, alpha = alpha, cex = 1.5)
  }
  return(p)
})

output$analysis_cd_plot = renderPlot({
  analysis_cdp()
}, res = 46)

# output$analysis_bayes_test = renderTable({
#   # reqAndAssign(input$analysis_measure, "ms")
#   # reqAndAssign(input$test_alpha, "alpha")
#   # data_bayes = data %>%
#   # group_by(framework, task) %>%
#   # summarize(measure = mean(get(ms))) %>%
#   # as.data.frame()
#   # colnames(data_bayes)[1] = "algorithm"
#   # b_hierarchical_test(data_bayes, baseline = "constantpredictor")
# })

output$analysis_tree_ui = renderUI({
  list(
    sliderTextInput(inputId = "analysis_time_select",
      label = "Select Results for (tuning time)",
      choices = levels(values$data$time),
      selected = levels(values$data$time)[1]
    ),
    sliderInput("analysis_tree_maxdepth", "Choose max depth of tree", min = 2L, max = 5L, value = 3L, step = 1L)
  # br(),
  # tags$hr(),
  # bsButton("train_model", "Analyse!", icon = icon("diagnoses"))
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

output$tree_plot = renderPlot({
  reqAndAssign(input$analysis_measure, "ms")
  reqAndAssign(input$analysis_tree_maxdepth, "maxdepth")

  cd = task_char_data()
  data = cd$data
  chars = cd$chars
  bt = getBtTree(data, chars, ms, maxdepth)
  plotBTTree(bt, terminal_panel = node_btplot_angle)
})