# DAG of the phase 2 joint score-occupancy model (dev/roadmap-integration.md),
# in the style and notation of the crywolf vignette DAG
# (crywolf: dev/dag/crywolf_dag.dot). Needs Graphviz (`dot`): the copy
# bundled with DiagrammeR misplaces subscripts. Run from the package root:
#   Rscript dev/dag/make_fase2_dag.R
system2("dot", c("-Tpng", "-Gdpi=120", file.path("dev", "dag", "fase2_dag.dot"),
                 "-o", file.path("dev", "dag", "fase2_dag.png")))
