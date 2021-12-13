bttree_paircomp = function (x) {
  comprow = function(x, tri) {
    eq = outer(x, x, "==")[tri]
    g = outer(x, x, ">")[tri]
    r = as.numeric(!eq)
    r[!eq & g] = 1
    r[!eq & !g] = -1
    r
  }
  tri = upper.tri(matrix(nrow = ncol(x), ncol = ncol(x)))
  r = t(apply(x, 1, comprow, tri))
  paircomp(r, labels = colnames(x), mscale = c(-1, 0, 1))
}

getBtTree = function(data, characteristics, measure, maxdepth) {
  comp_data = data %>%
  select(id, task, fold, framework, all_of(measure)) %>%
    removeDuplicates() %>%
    pivot_wider(values_from = !!measure, names_from = framework)

  cd = cbind(id = comp_data[, c(1)], preferences = bttree_paircomp(comp_data[, -c(1:3)]))
  tree_data = cd %>%
    left_join(characteristics[, -c(2, 3)], by = c("id" = "task.id")) %>%
    select(-id)
  bttree(preferences ~ ., data = na.omit(tree_data), maxdepth = maxdepth)
}

node_btplot_angle = function (mobobj, id = TRUE, worth = TRUE, abbreviate = FALSE,
  ref = TRUE, col = "black", refcol = "lightgray",
  bg = "white", cex = 0.5, pch = 19, xscale = NULL, yscale = NULL,
  ylines = 1.5, angle = 30, just = c(1,1)) {
  node = nodeids(mobobj, terminal = FALSE)
  cf = psychotree:::apply_to_models(mobobj, node,
    FUN = function(z) if (worth) worth(z) else coef(z, all = FALSE, ref = TRUE))
  cf = do.call("rbind", cf)
  rownames(cf) = node
  mod = psychotree:::apply_to_models(mobobj, node = 1L, FUN = NULL, drop = TRUE)
  if (!worth) {
    if (is.character(ref) | is.numeric(ref)) {
      reflab = ref
      ref = TRUE
    }
    else {
      reflab = mod$ref
    }
    if (is.character(reflab))
      reflab = match(reflab,
        if (!is.null(mod$labels))
          mod$labels
        else colnames(cf))
    cf = cf - cf[, reflab]
  }
  if (worth) {
    cf_ref = 1/ncol(cf)
  }
  else {
    cf_ref = 0
  }
  if (is.logical(abbreviate)) {
    nlab = max(nchar(colnames(cf)))
    abbreviate = if (abbreviate)
      as.numeric(cut(nlab, c(-Inf, 1.5, 4.5, 7.5, Inf)))
    else nlab
  }
  colnames(cf) = abbreviate(colnames(cf), abbreviate)
  x = 1:NCOL(cf)
  if (is.null(xscale))
    xscale = range(x) + c(-0.1, 0.1) * diff(range(x))
  if (is.null(yscale))
    yscale = range(cf) + c(-0.1, 0.1) * diff(range(cf))

  rval = function(node) {
    idn = id_node(node)
    cfi = cf[idn, ]
    top_vp = viewport(layout = grid.layout(nrow = 2, ncol = 3,
      widths = unit(c(ylines, 1, 1), c("lines", "null",
        "lines")), heights = unit(c(1, 1), c("lines",
        "null"))), width = unit(1, "npc"), height = unit(1,
      "npc") - unit(2, "lines"), name = paste("node_btplot",
      idn, sep = ""))
    pushViewport(top_vp)
    grid.rect(gp = gpar(fill = bg, col = 0))
    top = viewport(layout.pos.col = 2, layout.pos.row = 1)
    pushViewport(top)
    mainlab = paste(ifelse(id, paste("Node", idn, "(n = "),
        ""), info_node(node)$nobs, ifelse(id, ")", ""), sep = "")
    grid.text(mainlab)
    popViewport()
    plot_vpi = viewport(layout.pos.col = 2, layout.pos.row = 2,
      xscale = xscale, yscale = yscale, name = paste("node_btplot",
        idn, "plot", sep = ""))
    pushViewport(plot_vpi)
    grid.lines(xscale, c(cf_ref, cf_ref), gp = gpar(col = refcol),
      default.units = "native")
    grid.lines(x, cfi, gp = gpar(col = col, lty = 2),
      default.units = "native")
    grid.points(x, cfi, gp = gpar(col = col, cex = cex),
      pch = pch, default.units = "native")
    grid.xaxis(at = x, edits = gEdit(gPath="labels", rot = angle, just = just),
      label = names(cfi))
    grid.yaxis(at = c(ceiling(yscale[1] * 100)/100, floor(yscale[2] * 100)/100))
    grid.rect(gp = gpar(fill = "transparent"))
    upViewport(2)
  }
  return(rval)
}


plotBTTree = function (x, main = NULL, terminal_panel = node_btplot_angle, tp_args = list(angle = 70, just = c(1,0)),
  inner_panel = node_inner, ip_args = list(), edge_panel = edge_simple,
  ep_args = list(), drop_terminal = FALSE, tnex = 1.5, newpage = TRUE,
  pop = TRUE, gp = gpar(), margins = c(11, 3.5, -2, 1), ...) {
  node = node_party(x)
  nx = width(node)
  ny = depth(node, root = TRUE)
  if (newpage)
    grid.newpage()
  margins = if (is.null(margins)) {
    c(1, 1, if (is.null(main)) 0 else 3, 1)
  }
  else {
    rep_len(margins, 4L)
  }
  root_vp = viewport(layout = grid.layout(3, 3, heights = unit(c(margins[3L],
    1, margins[1L]), c("lines", "null", "lines")), widths = unit(c(margins[2L],
    1, margins[4L]), c("lines", "null", "lines"))), name = "root",
    gp = gp)
  pushViewport(root_vp)
  if (!is.null(main)) {
    main_vp = viewport(layout.pos.col = 2, layout.pos.row = 1,
      name = "main")
    pushViewport(main_vp)
    grid.text(y = unit(1, "lines"), main, just = "center")
    upViewport()
  }
  tree_vp = viewport(layout.pos.col = 2, layout.pos.row = 2,
    xscale = c(0, nx), yscale = c(0, ny + (tnex - 1)), name = "tree")
  pushViewport(tree_vp)
  terminal_panel = do.call("terminal_panel", c(list(x), as.list(tp_args)))
  inner_panel = do.call("inner_panel", c(list(x), as.list(ip_args)))
  edge_panel = do.call("edge_panel", c(list(x), as.list(ep_args)))
  if ((nx <= 1 & ny <= 1)) {
    if (is.null(margins))
      margins = rep.int(1.5, 4)
    pushViewport(plotViewport(margins = margins, name = paste("Node",
      id_node(node), sep = "")))
    terminal_panel(node)
  }
  else {
    partykit:::.plot_node(node, xlim = c(0, nx), ylim = c(0, ny - 0.5 +
      (tnex - 1)), nx = nx, ny = ny, terminal_panel = terminal_panel,
      inner_panel = inner_panel, edge_panel = edge_panel,
      tnex = tnex, drop_terminal = drop_terminal, debug = FALSE
    )
  }
  upViewport()
  if (pop)
    popViewport()
  else upViewport()
}
