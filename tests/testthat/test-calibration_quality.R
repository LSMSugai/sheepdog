# Tres especies com a mesma prevalencia: em A o score informa, em B nao
# informa e em C esta invertido
quality_data <- function(n = 300) {
  withr::with_seed(11, {
    faz <- function(especie, beta) {
      lc <- stats::rnorm(n, 0, 1.5)
      tibble::tibble(site = rep(c("S1", "S2"), length.out = n),
                     species = especie, logit_conf = lc,
                     confidence = stats::plogis(lc),
                     tp = stats::rbinom(n, 1, stats::plogis(beta * lc)))
    }
    dados <- rbind(faz("A", 2), faz("B", 0), faz("C", -2))
    dados$site <- factor(dados$site)
    dados$species <- factor(dados$species)
    dados
  })
}

test_that("calibration_quality() flags the species the pooled model hides", {
  q <- calibration_quality(quality_data(), tp ~ logit_conf * species)
  expect_equal(as.character(q$species), c("A", "B", "C"))
  expect_equal(q$n, rep(300L, 3))
  expect_equal(q$n_tp + q$n_fp, q$n)
  # em C o modelo inverte a curva, mas o score nao discrimina como esta
  expect_equal(q$status, c("ok", "poor", "poor"))
  expect_match(q$reason[2], "low AUC")
  expect_gt(q$auc[3], 0.7)
  expect_equal(q$reason[3], "low AUC of the score")
  expect_gt(q$logloss_gain[1], 0.1)
  expect_lt(q$logloss_gain[2], 0.02)
  expect_lt(abs(q$cal_slope[1] - 1), 0.5)
})

test_that("a global model is judged poor for the species it does not fit", {
  d <- quality_data()
  d <- d[d$species != "C", ]
  d$species <- droplevels(d$species)
  q <- calibration_quality(d, tp ~ logit_conf)
  expect_equal(q$status[q$species == "B"], "poor")
  # o AUC do score bruto nao e invertido: em C ele fica abaixo de 0.5
  q3 <- calibration_quality(quality_data(), tp ~ logit_conf)
  expect_lt(q3$auc_score[q3$species == "C"], 0.5)
  expect_lt(q3$auc[q3$species == "C"], 0.5)
})

test_that("calibration_quality() scores cells and leaves few clips unjudged", {
  d <- quality_data()
  q <- calibration_quality(d, tp ~ logit_conf * species,
                           by = c("site", "species"))
  expect_equal(nrow(q), 6L)
  expect_true(all(c("site", "species") %in% names(q)))
  q <- calibration_quality(d, tp ~ logit_conf * species, min_class = 1000)
  expect_true(all(q$status == "insufficient"))
  expect_match(q$reason[1], "fewer than 1000")
})

test_that("a group with one verdict has no AUC and is insufficient", {
  d <- quality_data()
  d$tp[d$species == "A"] <- 1L
  q <- calibration_quality(d, tp ~ logit_conf * species)
  expect_true(is.na(q$auc[q$species == "A"]))
  expect_equal(q$status[q$species == "A"], "insufficient")
})

test_that("limits of status can be changed", {
  d <- quality_data()
  q <- calibration_quality(d, tp ~ logit_conf * species, auc_min = 0.99)
  expect_equal(q$status[q$species == "A"], "poor")
  q <- calibration_quality(d, tp ~ logit_conf * species, auc_min = 0,
                           slope_range = c(-100, 100), intercept_max = 100)
  expect_equal(q$status[q$species == "C"], "ok")
})

test_that("calibration_quality() keeps folds grouped and the random state", {
  d <- quality_data()
  d$night <- rep(1:30, length.out = nrow(d))
  set.seed(1)
  antes <- .Random.seed
  q <- calibration_quality(d, tp ~ logit_conf * species, fold_group = "night")
  expect_identical(.Random.seed, antes)
  expect_equal(nrow(q), 3L)
})

test_that("calibration_quality() checks its input", {
  d <- quality_data()
  expect_error(calibration_quality(d, "tp ~ logit_conf"), "formula")
  expect_error(calibration_quality(d, tp ~ logit_conf, by = "nope"), "`by`")
  expect_error(calibration_quality(d, tp ~ logit_conf,
                                   slope_range = c(2, 1)), "slope_range")
  expect_error(calibration_quality(d, tp ~ nope), "all the folds")
})
