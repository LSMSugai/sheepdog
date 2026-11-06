# =============================================================================
# diagram_stage1_validation.R
#
# Figura 1 do indice de referencia: selecao, revisao (por uma ou varias
# pessoas), resumo e rodadas. Baseada na figura de Larissa S. M. Sugai.
# Uso: rode a partir da raiz do repositorio.
# =============================================================================
source("data-raw/diagram_style.R")

save_diagram(paste0('digraph s1 {', diagram_header("Stage 1. Validation: from predictions to verdicts"), '
  tabelas [label = "BirdNET_SelectionTable.txt\nevery prediction with its score",
           shape = note, fillcolor = "#ffffff", color = "#b8b8b8"]

  subgraph cluster_sel {
    label = "Selection: extract_validation_clips()"
    ', stage_cluster("s1"), '
    ler [label = "read_selection_tables()"]
    modo [label = "select_clips()\nsampling_mode", shape = diamond,
          style = "filled", fillcolor = "#c8def3", margin = "0.02,0.02"]
    top [label = "\\"top\\"\nhighest scores per recording"]
    det [label = "\\"random_detections\\"\noccasions with a score >= threshold"]
    rec [label = "\\"random_recordings\\"\nany recording, from list_recordings()"]
    cortar [label = "cut_clips(), pack_clips()\nclip_manifest.csv, one zip per species"]
  }

  subgraph cluster_rev {
    label = "Review"
    ', stage_cluster("s1"), '
    gui [label = "BirdNET GUI\nPositive / Negative folders"]
    app [label = "run_app()\nverdicts.csv"]
    varios [label = "Several reviewers (optional)\nassign_reviewers(), split_by_reviewer(),\nreviewer_agreement(), consensus_verdicts()"]
  }

  subgraph cluster_sum {
    label = "Summary: post_validation()"
    ', stage_cluster("s1"), '
    verdito [label = "classify_review() or app_verdicts()\nvalidation_by_clip.csv"]
    resumo [label = "precision_by_bin(), suggest_thresholds(),\nnightly_presence(), retraining_clips()"]
    rodadas [label = "combine_rounds()\nvalidation_combined.csv, with the\ncumulative inclusion probabilities"]
  }

  diag [label = "Diagnostic (Figure 2)", fillcolor = "#f4f4f4", color = "#9a9a9a"]

  tabelas -> ler -> modo
  modo -> top; modo -> det; modo -> rec
  top -> cortar; det -> cortar; rec -> cortar
  cortar -> gui; cortar -> app
  gui -> varios [style = dashed]; app -> varios [style = dashed]
  gui -> verdito; app -> verdito; varios -> verdito [style = dashed]
  verdito -> resumo
  verdito -> rodadas [style = dashed, label = " previous ="]
  resumo -> diag; rodadas -> diag [style = dashed]
}'), "stage1_validation")
