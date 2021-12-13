# A Statistical Analysis of the OpenML-AutoML-Benchmark

This shiny app contains a statistical analysis of the OpenML AutoML-Benchmark.
The Benchmark includes the performances of state-of-the-art AutoML frameworks on 39 data sets.


## Performance Overview
For a first impression, the overall performances of each framework is shown in the "Overview" tab.
You can choose from different plots grouped by tuning time, task type (binary and multiclass) or get results for single tasks.


## Statistical Analysis
The statistical analysis tries to find significant differences of the performing algorithms based on few data set characteristics.
Those characteristics are described below:


| Characteristic | Description |
|:---------------|:------------|
| no.nas      | The method of dealing with mis sing values in a data set differs for each algorithm. Hence, their existence and number can have significant effects |
| na.ratio    | The proportion or relative frequency of NAs in the data set |
| no.obs| Number of observations |
| no.cat.features| Number of categorial features |
| max.cardinality| Maximal cardinality of all categorical features |
| no.num.features| Number of numerical features |


## Hypothesis Tests
Differences between algorithms are illustrated by:

  - Critical Difference Plots
  - Bratley Terry Trees
