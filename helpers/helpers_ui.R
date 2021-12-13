makeSidebar = function(..., bar.height = 500) {
  args = list(...)
  div(class = "sidebarbox",
    box(width = NULL, height = bar.height, args)
  )
}
