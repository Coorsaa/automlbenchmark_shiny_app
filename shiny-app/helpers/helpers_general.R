reqAndAssign = function(obj, name) {
  req(obj)
  assign(name, obj, pos = 1L)
}

getFilteredData = function(data, measure, drop_framework = character(0L)) {
  comp = which(complete.cases(data[, measure]))
  fw = which(data$framework %nin% drop_framework)
  rows = intersect(comp, fw)
  features = setdiff(colnames(data), c("acc", "balacc", "auc", "logloss", "mae", "r2", "rmse"))
  droplevels(data[rows, c(features, measure)])
}

preprocData = function(data) {
  data$time = as.factor(str_sub(data$constraint, 1, 2))
  data = data %>%
    filter(constraint != "test")
  data = droplevels(data[!grepl(pattern = "Error", x = data$info), ])
  return(data)
}


removeDuplicates = function(data, measure) {
  data %>%
    distinct(id, task, framework, fold, .keep_all = TRUE)
}


replaceMissingsByConstantPredictor = function(data, ms) {

  # x <<- data

  # fw = levels(droplevels(data$framework))
  # impute_scores = data %>%
  #   pivot_wider(id_cols = c(id, task, fold, type), names_from = framework, values_from = !!ms)

  # for (f in fw) {
  #   impute_scores[is.na(impute_scores[[f]]), f] = impute_scores[is.na(impute_scores[[f]]), "constantpredictor"]
  # }

  # data = impute_scores %>%
  #   pivot_longer(cols = fw, names_to = "framework", values_to = ms, values_drop_na = FALSE)
  # data$framework = as.factor(data$framework)

  # return(data)
}