source("utils/helpers.R")

#* @post /api/test
#* @serializer png
function(min, max, text) {
    plot(min:max, main = text)
}

#* @post /api/bt_tree
#* param data Data containing 'id', 'task', 'fold', 'framework' and scores
#* param characteristics Data containing dataset characteristics
#* param maxdepth Maximal depth of BT tree
#* param min_nodesize Minimum of nodes required in a leaf
#* @serializer png
function(data, characteristics, measure, maxdepth, min_nodesize) {
    bt_tree = getBtTree(data, characteristics, measure, maxdepth, min_nodesize)
    plotBTTree(bt_tree)
}
