# =============================================================================
# diagram_stage1_retraining.R
#
# Figura 3 do indice de referencia: quando retreinar e o ciclo do retreino.
# Baseada na figura de Larissa S. M. Sugai.
# Uso: rode a partir da raiz do repositorio.
# =============================================================================
source("data-raw/diagram_style.R")

save_diagram(paste0('digraph retrain {', diagram_header("Stage 1. Retraining: when the classifier, not the review, limits precision"), '
  gatilho [label = "\\"unreliable\\" in review_support(), or\n\\"poor\\" in calibration_quality() after the other options,\nor most false positives come from one cause",
           fillcolor = "#f4f4f4", color = "#9a9a9a"]

  subgraph cluster_ciclo {
    label = "The retraining loop"
    ', stage_cluster("s1"), '
    ouvir [label = "Listen to the false positives\nvalidation_by_clip.csv, verdict = negative"]
    pos [label = "retraining_clips()\nconfirmed positive clips, retraining_clips.csv"]
    set [label = "build_training_set()\ntrain, val and test split by night;\nnegatives in one folder (\\"Noise\\");\nwarns below min_files = 100 per class"]
    treino [label = "Train in BirdNET-Analyzer\n(outside R)", fillcolor = "#eeeeee", color = "#9a9a9a"]
    rodar [label = "Run the new classifier on the audio\nnew selection tables", fillcolor = "#eeeeee", color = "#9a9a9a"]
    excl [label = "exclude_training_clips() or training_nights()\ntraining clips are never drawn again"]
  }
  nova [label = "A new validation\nselect_clips(), review, diagnostic (Figures 1 and 2)",
        fillcolor = "#f4f4f4", color = "#9a9a9a"]

  gatilho -> ouvir -> pos -> set -> treino -> rodar -> excl -> nova
}'), "stage1_retraining", width = 1100)
