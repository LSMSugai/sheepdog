#' Check the quality of the calibrated probabilities by species
#'
#' [compare_calibration_models()] scores each model over all the clips,
#' which can hide a species whose probabilities should not be trusted: the
#' mean AUC rises when species differ in precision, even if the score says
#' little within a species, and partial pooling lends such a species the
#' curve of the others. This function refits one model by cross-validation
#' and scores the held-out predictions within each group, asking three
#' questions before the probabilities are used:
#'
#' * Does the model add information? `logloss_gain` is the log-loss of a
#'   null model, the share of true positives of the group in the training
#'   folds, minus the log-loss of the model. It plays the part of a
#'   comparison with an intercept-only model, on held-out clips.
#' * Does it discriminate? `auc` is the AUC of the held-out probabilities
#'   within the group, and `auc_score` that of the raw confidence score.
#'   An `auc` well above `auc_score` means that the discrimination comes
#'   from other terms of the model (e.g. site effects, when `by = "species"`),
#'   not from the score, so both must reach `auc_min`. Unlike the AUC of
#'   [compare_calibration_models()], these are not reversed when the
#'   ranking is inverted, so values below 0.5 can occur.
#' * Are the probabilities correct? `cal_intercept` and `cal_slope` come
#'   from a logistic regression of the verdicts on the logit of the
#'   held-out probabilities (intercept 0 and slope 1 when well calibrated).
#'   AUC alone does not answer this: a model can rank clips well and still
#'   give wrong probabilities.
#'
#' The limits behind `status` are screening values, not estimates: they are
#' meant to direct attention to a group, and should be set for each project.
#' A group marked `"poor"` needs more clips, a different model or a decision
#' to leave the species out of the analyses that use P(TP).
#'
#' The results depend on the design of the review. Discrimination is
#' measured over the scores that were reviewed, so the `"top"` design, which
#' concentrates the clips at high scores (see `conf_min` and `conf_max`),
#' can give a low AUC even with a good classifier. The clips of
#' `"random_detections"` cover the range of scores of the predictions.
#'
#' The fits use maximum likelihood, also when the final model is fitted with
#' `engine = "brms"`. Use `fold_group` to keep the clips of a recording or
#' night on the same side of the split.
#'
#' @inheritParams compare_calibration_models
#' @param formula Formula of the model to check, e.g. the one chosen by
#'   [select_calibration_model()].
#' @param by Columns that define the groups: `"species"`, or
#'   `c("site", "species")` for the cells of the calibration, which hold
#'   fewer clips each.
#' @param min_class Least number of true positives and of false positives
#'   for a group to be judged. With fewer, `status` is `"insufficient"`.
#' @param auc_min Lowest acceptable `auc` and `auc_score`.
#' @param slope_range Acceptable range of `cal_slope`.
#' @param intercept_max Largest acceptable absolute `cal_intercept`.
#'
#' @return A tibble with one row per group: the `by` columns, `n`, `n_tp`,
#'   `n_fp`, `conf_min`, `conf_max`, `auc`, `auc_score`, `logloss`,
#'   `logloss_null`, `logloss_gain`, `cal_intercept`, `cal_slope`, `status`
#'   (`"ok"`, `"poor"` or `"insufficient"`) and `reason`. Measures that
#'   cannot be computed (e.g. the AUC of a group with one verdict) are `NA`.
#'   Folds whose fit failed are left out, with a warning.
#' @seealso [compare_calibration_models()], [calibration_ppc()]
#' @export
calibration_quality <- function(validations, formula, k_folds = 5,
                                seed = 2026, fold_group = NULL,
                                by = "species", min_class = 10,
                                auc_min = 0.7, slope_range = c(0.5, 1.5),
                                intercept_max = 1) {
  if (!inherits(formula, "formula")) {
    stop("`formula` must be a model formula.", call. = FALSE)
  }
  if (!is.character(by) || length(by) == 0L || anyNA(by) ||
      !all(by %in% names(validations))) {
    stop("`by` must name columns of `validations`.", call. = FALSE)
  }
  if (anyNA(validations[by])) {
    stop("The `by` columns must have no missing values.", call. = FALSE)
  }
  if (!is.numeric(slope_range) || length(slope_range) != 2L ||
      anyNA(slope_range) || slope_range[1] >= slope_range[2]) {
    stop("`slope_range` must be two increasing numbers.", call. = FALSE)
  }
  need_lme4(list(formula))

  val <- validations
  val$.dobra <- calibration_folds(validations, k_folds, seed, fold_group)
  val$.grupo <- do.call(paste, c(lapply(val[by], as.character), sep = "\r"))
  val$.p <- NA_real_
  val$.p_nulo <- NA_real_
  n_falhas <- 0L
  for (k in seq_len(k_folds)) {
    teste <- which(val$.dobra == k)
    treino <- val[val$.dobra != k, ]
    fit <- tryCatch(fit_model(formula, treino), error = function(e) NULL)
    if (is.null(fit)) {
      n_falhas <- n_falhas + 1L
      next
    }
    val$.p[teste] <- predict_tp(fit, val[teste, ])
    # taxa do grupo no treino, suavizada para nao dar 0 ou 1; grupo ausente
    # do treino (dobras agrupadas) recebe a taxa geral
    taxa <- tapply(treino$tp, treino$.grupo,
                   function(x) (sum(x) + 1) / (length(x) + 2))
    nulo <- unname(taxa[val$.grupo[teste]])
    nulo[is.na(nulo)] <- mean(treino$tp)
    val$.p_nulo[teste] <- nulo
  }
  if (n_falhas == k_folds) {
    stop("The fit failed in all the folds.", call. = FALSE)
  }
  if (n_falhas > 0L) {
    warning("The fit failed in ", n_falhas, " of ", k_folds,
            " folds, left out of the measures.", call. = FALSE)
  }

  val |>
    filter(!is.na(.p)) |>
    group_by(across(all_of(by))) |>
    group_modify(function(d, chave) {
      quality_row(d, min_class, auc_min, slope_range, intercept_max)
    }) |>
    ungroup()
}

# Medidas de um grupo sobre as predicoes fora da amostra
quality_row <- function(d, min_class, auc_min, slope_range, intercept_max) {
  medidas <- score_probabilities(d$tp, d$.p)
  ll_nulo <- score_probabilities(d$tp, d$.p_nulo)[["logloss"]]
  ganho <- ll_nulo - medidas[["logloss"]]
  n_tp <- sum(d$tp == 1L)
  n_fp <- sum(d$tp == 0L)
  area <- auc_ordered(d$tp, d$.p)
  area_score <- auc_ordered(d$tp, d$confidence)
  inclinacao <- medidas[["cal_slope"]]
  intercepto <- medidas[["cal_intercept"]]

  fora <- function(teste) isTRUE(teste)
  motivos <- c(
    if (fora(ganho <= 0)) "no gain over the null model",
    if (fora(area < auc_min)) "low AUC",
    if (fora(area_score < auc_min)) "low AUC of the score",
    if (fora(inclinacao < slope_range[1] || inclinacao > slope_range[2])) {
      "calibration slope out of range"
    },
    if (fora(abs(intercepto) > intercept_max)) {
      "calibration intercept out of range"
    })
  poucos <- n_tp < min_class || n_fp < min_class
  tibble(n = nrow(d), n_tp = n_tp, n_fp = n_fp,
         conf_min = min(d$confidence), conf_max = max(d$confidence),
         auc = area, auc_score = area_score,
         logloss = medidas[["logloss"]], logloss_null = ll_nulo,
         logloss_gain = ganho, cal_intercept = intercepto,
         cal_slope = inclinacao,
         status = if (poucos) "insufficient"
                  else if (length(motivos) > 0) "poor" else "ok",
         reason = if (poucos) {
           paste0("fewer than ", min_class, " clips of a verdict")
         } else {
           paste(motivos, collapse = "; ")
         })
}

# AUC com a direcao fixa: pROC::roc() por padrao inverte a ordem quando ela
# da uma area abaixo de 0.5, o que esconderia um score invertido
auc_ordered <- function(tp, p) {
  if (n_distinct(tp) < 2L) return(NA_real_)
  as.numeric(pROC::auc(pROC::roc(tp, p, levels = c(0, 1), direction = "<",
                                 quiet = TRUE)))
}
