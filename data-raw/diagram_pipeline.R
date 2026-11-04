# =============================================================================
# diagram_pipeline.R
#
# Esquema (DiagrammeR) dos tres estagios do sheepdog, com as funcoes e os
# arquivos de cada um:
#   1. Dados de validacao (extracao -> revisao manual -> TP/FP)
#   2. Calibracao (score -> probabilidade)
#   3. Matrizes de comunidade
# e o ramo da ocupacao (export_occupancy_data() -> occasion_draws() -> crywolf).
#
# Uso: rode o script inteiro a partir da raiz do repositorio; o diagrama
# abre no Viewer do RStudio e e exportado para man/figures/pipeline.png.
# Dependencias: install.packages(c("DiagrammeR", "DiagrammeRsvg", "rsvg"))
# =============================================================================

library(DiagrammeR)

fluxo <- grViz('
digraph pipeline {

  graph [rankdir = TB, fontname = "Helvetica", fontsize = 13,
         nodesep = 0.4, ranksep = 0.5, bgcolor = "white",
         label = "sheepdog: from BirdNET detections to analysis-ready data",
         labelloc = "t", fontcolor = "#2c3e50"]

  node [fontname = "Helvetica", fontsize = 11.5, style = "filled,rounded",
        shape = box, penwidth = 1.1, color = "#8aa5b8", margin = "0.2,0.11"]
  edge [fontname = "Helvetica", fontsize = 10, color = "#7f8c99",
        fontcolor = "#5d6b78", arrowsize = 0.8]

  audios [label = "Recordings\n..._YYYYMMDD_HHMMSS (.wav, .flac, .mp3)",
          shape = note, fillcolor = "#ffffff", color = "#b8b8b8"]
  birdnet [label = "BirdNET classifier (pretrained or custom)\nBirdNET_SelectionTable.txt per site",
           fillcolor = "#eeeeee", color = "#9a9a9a"]

  /* ------- ESTAGIO 1: dados de validacao ------- */
  subgraph cluster_e1 {
    label = "Stage 1. Validation data"
    fontcolor = "#1f5c8b"; color = "#bcd4e6"; style = "rounded"
    bgcolor = "#eef5fb"

    listar [label = "list_recordings()\nevery recording made,\nwith or without predictions",
            fillcolor = "#d9e9f8"]
    extrair [label = "extract_validation_clips()\nread_selection_tables() > select_clips()\n> cut_clips() > pack_clips()\nrandom draws stratified within site x species\n(night, hour, month, ... or covariate_bins())",
             fillcolor = "#d9e9f8"]
    manifesto [label = "clip_manifest.csv\nclips/<species_folder>/, packages/<species_folder>.zip",
               shape = note, fillcolor = "#ffffff"]
    gui [label = "Manual review in the BirdNET GUI\nPositive / Negative folders",
         fillcolor = "#d9e9f8"]
    app [label = "Manual review in run_app()\nverdicts.csv; the app also draws and cuts\nthe clips and exports the occupancy tables",
         fillcolor = "#d9e9f8"]
    revisores [label = "Several reviewers (optional)\nassign_reviewers(), split_by_reviewer(),\nreviewer_agreement(), consensus_verdicts()",
               fillcolor = "#d9e9f8"]
    posval [label = "post_validation()\nreview folders or verdicts_file;\nclassify_review(), precision_by_bin(),\nsuggest_thresholds(), nightly_presence()",
            fillcolor = "#d9e9f8"]
    tpfp [label = "validation_by_clip.csv\nmanifest + verdict per clip\n(positive / negative / not reviewed)",
          shape = note, fillcolor = "#ffffff"]
    suporte [label = "review_support()\nwhich site x species cells (or bins)\nstill need review",
             fillcolor = "#d9e9f8"]
  }

  /* ------- ESTAGIO 2: calibracao ------- */
  subgraph cluster_e2 {
    label = "Stage 2. Calibration: score to probability"
    fontcolor = "#8a5a00"; color = "#ecd9b0"; style = "rounded"
    bgcolor = "#fdf6e9"

    cv [label = "compare_calibration_models()\ncandidates from tp ~ logit(conf) to\n+ (logit(conf) | species) + (1 | site:species);\nstratified k-fold CV, simplest model within\none SE of the lowest log-loss",
        fillcolor = "#fceecf"]
    fit [label = "fit_calibration()\nselected model refitted to all clips\nengine = \\"lme4\\" or \\"brms\\"",
         fillcolor = "#fceecf"]
    limiares [label = "calibrated_thresholds()\na threshold per site x species\nfrom the model (thresholds.csv)",
              fillcolor = "#fceecf"]
    bayes [label = "Bayesian checks (brms)\ncalibration_prior(), calibration_diagnostics(),\ncalibration_ppc(), calibration_sensitivity()",
           fillcolor = "#fceecf"]
    prever [label = "score_detections()\nP(TP) for every detection\n(calibrated species only)",
            fillcolor = "#f9e3ae"]
    historico [label = "detection_history() / history_draws()\nnightly detection histories\nP(TP) >= p_min, or one version per posterior draw",
               fillcolor = "#f9e3ae"]
  }

  /* ------- ESTAGIO 3: matrizes ------- */
  subgraph cluster_e3 {
    label = "Stage 3. Community matrices"
    fontcolor = "#1e6b3a"; color = "#bcdcc6"; style = "rounded"
    bgcolor = "#eefaf1"

    nucleo [label = "cell_status(), suggest_core_species()\nwhich cells and species are supported",
            fillcolor = "#d9f2e0"]
    matrizes [label = "build_community_matrices() / community_matrices_draws()\nsite x month, core species, k >= k_min\nnights with detection / nights recorded",
              fillcolor = "#d9f2e0"]
  }

  /* ------- OCUPACAO: exportacao para o crywolf ------- */
  subgraph cluster_occ {
    label = "Occupancy data (schema sheepdog-occupancy)"
    fontcolor = "#5e3a7a"; color = "#d6c3e6"; style = "rounded"
    bgcolor = "#f8f2fc"

    exportar [label = "export_occupancy_data()\noccasions, detections, validation,\ncalibration draws, schema.json",
              fillcolor = "#efe2f8", color = "#b393c9"]
    versoes [label = "occasion_draws()\none detection data set per posterior draw\n(occasion_draws.parquet)",
             fillcolor = "#efe2f8", color = "#b393c9"]
  }

  ordenacoes [label = "Multivariate ordinations\n(PCoA, NMDS, RDA)",
              fillcolor = "#f3e8fa", color = "#b393c9"]
  occupancy [label = "Occupancy models with false positives\n(crywolf, or any occupancy software)",
             fillcolor = "#f3e8fa", color = "#b393c9"]
  retreino [label = "retraining_clips.csv\nclassifier retraining",
            fillcolor = "#f3e8fa", color = "#b393c9"]

  /* ------- FLUXO ------- */
  audios  -> birdnet
  birdnet -> extrair
  audios  -> listar [style = dashed]
  listar  -> extrair [style = dashed]
  extrair -> manifesto
  manifesto -> gui
  manifesto -> app
  gui     -> posval
  app     -> posval
  gui     -> revisores [style = dashed]
  app     -> revisores [style = dashed]
  revisores -> posval [style = dashed]
  posval  -> tpfp
  tpfp    -> suporte [style = dashed]
  suporte -> extrair [label = " review more", style = dashed, constraint = false]
  tpfp    -> cv [label = " calibrate()"]
  cv      -> fit [label = " selected model"]
  fit     -> bayes [style = dashed]
  fit     -> limiares [style = dashed]
  fit     -> prever
  birdnet -> prever [label = " every detection\n (not only the reviewed ones)", style = dashed]
  prever  -> historico
  historico -> nucleo
  nucleo  -> matrizes
  matrizes -> ordenacoes
  fit     -> exportar [label = " fit ="]
  tpfp    -> exportar [label = " validation =", style = dashed]
  exportar -> versoes
  versoes -> occupancy
  posval  -> retreino [style = dashed]
}
')

fluxo  # abre no Viewer

svg_txt <- DiagrammeRsvg::export_svg(fluxo)
rsvg::rsvg_png(charToRaw(svg_txt), "man/figures/pipeline.png", width = 2400)
message("Diagram written to man/figures/pipeline.png")
