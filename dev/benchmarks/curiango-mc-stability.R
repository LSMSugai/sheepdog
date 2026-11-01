# Choice of M for the Monte Carlo propagation of the calibration (phase 1
# of dev/roadmap-integration.md): how many versions of the detections
# fp_occu_mc() needs on the Curiango data.
# Reads the draws of each fit saved by curiango-flow.R with DRAWS_DIR set,
# after a run with a large M (M = 50):
#   M=50 DRAWS_DIR=dev/benchmarks/results/mc-draws \
#     OUT=dev/benchmarks/results/curiango-flow-m50 \
#     Rscript dev/benchmarks/curiango-flow.R
#   Rscript dev/benchmarks/curiango-mc-stability.R [DRAWS_DIR]
# Two measures for each parameter and M:
#   * the Monte Carlo standard error of the pooled mean, sd_between /
#     sqrt(M) (the versions are independent draws of the calibration), as a
#     share of the pooled posterior standard deviation;
#   * the spread, over R random subsets of M of the fits, of the pooled
#     mean and of the bounds of the 95% interval, as a share of the pooled
#     posterior standard deviation of all fits. Subsets of a finite set of
#     fits understate the spread as M approaches the number of fits, so this
#     measure is reported only up to half of them.
# Writes inst/benchmarks/curiango-mc-stability.csv.
args <- commandArgs(trailingOnly = TRUE)
draws_dir <- if (length(args)) args[1] else "dev/benchmarks/results/mc-draws"
out <- Sys.getenv("OUT", "inst/benchmarks")
R <- as.integer(Sys.getenv("R", "200"))
chains_per_fit <- 4
suppressPackageStartupMessages({library(dplyr); library(posterior)})

stability <- function(cl) {
  dr <- readRDS(file.path(draws_dir, paste0(cl, "-draws.rds")))
  diag <- readRDS(file.path(draws_dir, paste0(cl, "-diagnostics.rds")))
  n_fits <- sum(diag$kept)
  stopifnot(nchains(dr) == n_fits * chains_per_fit)
  a <- as_draws_array(dr)
  fit_of_chain <- rep(seq_len(n_fits), each = chains_per_fit)
  vars <- variables(dr)
  # media e dp de cada ajuste; posterior combinada de todos
  per_fit <- lapply(vars, function(v) {
    x <- a[, , v, drop = TRUE]
    tibble(variable = v, fit = seq_len(n_fits),
           mean = tapply(colMeans(x), fit_of_chain, mean),
           sd = tapply(seq_along(fit_of_chain), fit_of_chain,
                       function(k) sd(as.vector(x[, k]))))
  }) |> bind_rows()
  full <- summarise_draws(dr, mean = mean, sd = sd)
  between <- per_fit |>
    summarise(sd_between = sqrt(mean((mean - mean(mean))^2)), .by = variable)
  ms <- sort(unique(c(2, 5, 10, 15, 20, 25, 30, 40, n_fits)))
  ms <- ms[ms <= n_fits]
  set.seed(2026)
  subsets <- lapply(ms[ms <= n_fits / 2], function(m) {
    lapply(seq_len(R), function(r) {
      k <- which(fit_of_chain %in% sample.int(n_fits, m))
      s <- summarise_draws(subset_draws(dr, chain = k), mean = mean,
                           lower = ~ quantile(.x, 0.025, names = FALSE),
                           upper = ~ quantile(.x, 0.975, names = FALSE))
      mutate(s, m = m, rep = r)
    }) |> bind_rows()
  }) |> bind_rows()
  spread <- if (nrow(subsets) == 0) {
    tibble(variable = character(), m = numeric(), sd_mean = numeric(),
           sd_lower = numeric(), sd_upper = numeric())
  } else {
    subsets |>
      summarise(sd_mean = sd(mean), sd_lower = sd(lower),
                sd_upper = sd(upper), .by = c(variable, m))
  }
  tidyr::expand_grid(variable = vars, m = ms) |>
    left_join(full, by = "variable") |>
    left_join(between, by = "variable") |>
    left_join(spread, by = c("variable", "m")) |>
    transmute(classifier = cl, variable, m, posterior_sd = sd,
              mcse_mean_share = sd_between / sqrt(m) / sd,
              subset_mean_share = sd_mean / sd,
              subset_lower_share = sd_lower / sd,
              subset_upper_share = sd_upper / sd,
              n_fits)
}
res <- bind_rows(lapply(c("custom", "birdnet"), stability))
dir.create(out, showWarnings = FALSE, recursive = TRUE)
readr::write_csv(res, file.path(out, "curiango-mc-stability.csv"), na = "")
# menor M em que o erro de Monte Carlo da media fica abaixo de 10% do dp
# posterior em todos os coeficientes de ocupacao
res |>
  filter(startsWith(variable, "occ_")) |>
  summarise(worst = max(mcse_mean_share), .by = c(classifier, m)) |>
  print(n = Inf)
