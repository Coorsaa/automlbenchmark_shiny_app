### modified from mlr3benchmark
critical_differences = function(rank_data, minimize, meas, p.value) {
  checkmate::assertNumeric(p.value, lower = 0, upper = 1, len = 1)

  # Get Rankmatrix, transpose and get mean ranks
  mean_rank = rowMeans(rank_data)
  # Gather Info for plotting the descriptive part.
  df = data.frame(mean_rank,
    learner_id = names(mean_rank),
    rank = rank(mean_rank, ties.method = "average"))
  colnames(df)[2] = "framework"
  # Orientation of descriptive lines yend(=y-value of horizontal line)
  right = df$rank > stats::median(df$rank)
  # Better learners are ranked ascending
  df$yend[!right] = rank(df$rank[!right], ties.method = "first") + 1
  # Worse learners ranked descending
  df$yend[right] = rank(-df$rank[right], ties.method = "first") + 1
  # Better half of learner have lines to left / others right.
  df$xend = ifelse(!right, 0L, max(df$rank) + 1L)
  # Save orientation, can be used for vjust of text later on
  df$right = as.numeric(right)

  # calculate critical difference(s)
  cd = (stats::qtukey(1 - p.value, nrow(rank_data), 1e+06) / sqrt(2L)) *
    sqrt(nrow(rank_data) * (nrow(rank_data) + 1L) / (6L * ncol(rank_data)))

  out = list(data = df, test = "Nemenyi", cd = cd)

  # Create data for connecting bars (only nemenyi test)
  sub = sort(df$mean_rank)
  # Compute a matrix of all possible bars
  mat = apply(t(outer(sub, sub, `-`)), c(1, 2),
    FUN = function(x) ifelse(x > 0 && x < cd, x, 0))
  # Get start and end point of all possible bars
  xstart = round(apply(mat + sub, 1, min), 3)
  xend = round(apply(mat + sub, 1, max), 3)
  nem_df = data.table(xstart, xend, "diff" = xend - xstart) # nolint
  # For each unique endpoint of a bar keep only the longest bar
  nem_df = nem_df[, .SD[which.max(.SD$diff)], by = "xend"] # nolint
  # Take only bars with length > 0
  nem_df = nem_df[nem_df$diff > 0, ] # nolint
  # Descriptive lines for learners start at 0.5, 1.5, ...
  rank_y = rank(c(seq.int(length.out = sum(nem_df$xstart <= stats::median(df$mean_rank))),
    seq.int(length.out = sum(nem_df$xstart > stats::median(df$mean_rank)))),
    ties.method = "first")
  nem_df$y = seq.int(from = 0.3, to = 1.8, length.out = nrow(nem_df))[rank_y]
  out$nemenyi_data = as.data.frame(nem_df) # nolint
  return(out)
}


cd_plot = function(rank_data, minimize, meas, p.value) { # nolint
  cd = critical_differences(rank_data, minimize = minimize, meas = meas, p.value = p.value)

  # Plot descriptive lines and learner names
  p = ggplot(cd$data)
  # Point at mean rank
  p = p + geom_point(aes_string("mean_rank", 0), size = 3)
  # Horizontal descriptive bar
  p = p + geom_segment(aes_string("mean_rank", 0, xend = "mean_rank", yend = "yend"), size = 0.8)
  # Vertical descriptive bar
  p = p + geom_segment(aes_string("mean_rank", "yend", xend = "xend",
    yend = "yend"), size = 0.8)
  # Plot Learner name
  p = p + geom_text(aes_string("xend", "yend", label = "framework",
    hjust = "right"), vjust = -1, size = 7)

  p = p + xlab("Average Rank")
  # Change appearance
  p = p + scale_x_continuous(breaks = c(0:max(cd$data$xend)))
  p = p + theme(
    text = element_text(size = 20),
    axis.text.y = element_blank(),
    axis.text.x = element_text(size =15),
    axis.ticks.y = element_blank(),
    axis.ticks.x = element_line(size = 1),
    axis.ticks.length=unit(.25, "cm"),
    axis.title.y = element_blank(),
    legend.position = "none",
    panel.background = element_blank(),
    panel.border = element_blank(),
    axis.line = element_line(size = 1),
    axis.line.y = element_blank(),
    panel.grid.major = element_blank(),
    plot.background = element_blank())

  # Add crit difference test (descriptive)
  p = p + annotate("text",
    label = paste("Critical Difference =", round(cd$cd, 2), sep = " "),
    y = max(cd$data$yend) + 0.8, x = mean(cd$data$mean_rank), size = 7)
  # Add bar (descriptive)
  p = p + annotate("segment",
    x = mean(cd$data$mean_rank) - 0.5 * cd$cd,
    xend = mean(cd$data$mean_rank) + 0.5 * cd$cd,
    y = max(cd$data$yend) + 0.5,
    yend = max(cd$data$yend) + 0.5,
    size = 1.3, alpha = 0.9)

  nemenyi_data = cd$nemenyi_data # nolint
  if (!(nrow(nemenyi_data) == 0L)) {
    # Add connecting bars
    p = p + geom_segment(aes_string("xstart", "y", xend = "xend", yend = "y"),
      data = nemenyi_data, size = 1.3, color = "dimgrey", alpha = 0.9,
    )
  } else {
    message("No connecting bars to plot!")
  }

  return(p)
}

# cd_plot2 = function(rank_data, minimize, meas, p.value, ratio = 1) { # nolint
#   cd = critical_differences(rank_data, minimize = minimize, meas = meas, p.value = p.value)

#   # Plot descriptive lines and learner names
#   cd$data$yend = -cd$data$yend
#   p = ggplot(cd$data)

#   # visible binding hack
#   x = NULL

#   # Add bar (descriptive)
#   p = p + annotate("segment",
#                    x = mean(cd$data$mean_rank) - 0.5 * cd$cd,
#                    xend = mean(cd$data$mean_rank) + 0.5 * cd$cd,
#                    y = 1.5,
#                    yend = 1.5,
#                    size = 1)

#   # Add crit difference test (descriptive)
#   p = p + annotate("text",
#                    label = paste("Critical Difference =", round(cd$cd, 2), sep = " "),
#                    y = 2, x = mean(cd$data$mean_rank))

#   # manually build axis
#   p = p + geom_segment(aes(x = 0, xend = max(rank) + 1, y = 0, yend = 0)) +
#     geom_text(data = data.frame(x = seq.int(0, max(cd$data$rank) + 1)),
#               aes(x = x, label = x, y = 0.7)) +
#     geom_segment(data = data.frame(x = seq.int(0, max(cd$data$rank) + 1)),
#                  aes(x = x, xend = x, y = 0, yend = 0.3))

#   # Horizontal descriptive bar
#   p = p + geom_segment(aes_string("mean_rank", 0, xend = "mean_rank", yend = "yend"))
#   # Vertical descriptive bar
#   p = p + geom_segment(aes_string("mean_rank", "yend", xend = "xend", yend = "yend"))
#   # Plot Learner name
#   p = p + geom_text(aes_string("xend", "yend", label = "framework",
#     hjust = "right"), vjust = -1)

#   p = p + xlab("Average Rank")
#   # Change appearance
#   p = p + theme(axis.text = element_blank(),
#     axis.ticks = element_blank(),
#     axis.title = element_blank(),
#     legend.position = "none",
#     panel.background = element_blank(),
#     panel.border = element_blank(),
#     axis.line = element_blank(),
#     panel.grid.major = element_blank(),
#     plot.background = element_blank())

#   # Plot the critical difference bars
#   nemenyi_data = cd$nemenyi_data # nolint
#   if (!(nrow(nemenyi_data) == 0L)) {
#     # Add connecting bars
#     nemenyi_data$y = -nemenyi_data$y
#     p = p + geom_segment(aes_string("xstart", "y", xend = "xend", yend = "y"),
#                          data = nemenyi_data, size = 1.3)
#   } else {
#     message("No connecting bars to plot!")
#   }

#   p = p + coord_fixed(ratio = ratio, ylim = c(min(cd$data$yend), 2))

#   return(p)
# }

