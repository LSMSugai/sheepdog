# The Monte Carlo path next to the four threshold paths of the Curiango
# article (Fig. 4 of the corrected analysis, minutes as occasions): the
# occupancy coefficients of the false-positive model fitted to the versions
# of the calibration (curiango-flow.R), with no threshold, beside those of
# the naive GLMM, the standard occupancy model and the false-positive model
# under MaxF1 and MaxPrecision.
#   Rscript dev/benchmarks/curiango-fig4-mc.R FIG4_DATA [MC_SUMMARY]
# FIG4_DATA is Fig4_data_minutes.csv of the reanalysis (cell, parameter,
# mean, lower, upper, framework, detector, threshold); MC_SUMMARY defaults
# to inst/benchmarks/curiango-flow-summary.csv.
# The models share the occupancy covariates (night means at each recorder,
# standardised over the site-nights; moon on the log scale) but not the
# rest: the false-positive model of the article has a recorder random
# effect on detection, the Monte Carlo fits do not, and the article fits
# each path to the detections above its threshold, so the site-nights over
# which the covariates are standardised can differ slightly. Read the
# comparison as approximate.
# Writes the figure and the table to dev/benchmarks/results/ (ignored).
args <- commandArgs(trailingOnly = TRUE)
stopifnot("give the path to Fig4_data_minutes.csv" = length(args) >= 1)
mc_file <- if (length(args) > 1) args[2] else "inst/benchmarks/curiango-flow-summary.csv"
out <- Sys.getenv("OUT", "dev/benchmarks/results")
suppressPackageStartupMessages({library(dplyr); library(ggplot2)})

fig4 <- readr::read_csv(args[1], show_col_types = FALSE)
nomes <- c(occ_temp = "Temperature", occ_rh = "Relative humidity",
           occ_moon = "Moon illumination (log)")
mc <- readr::read_csv(mc_file, show_col_types = FALSE) |>
  filter(variable %in% names(nomes)) |>
  transmute(parameter = unname(nomes[variable]), mean, lower, upper,
            framework = "False-positive occupancy",
            detector = if_else(classifier == "custom", "Custom", "BirdNET"),
            threshold = "No threshold (MC)",
            cell = paste(detector, "—", threshold))
tab <- bind_rows(fig4, mc) |>
  mutate(framework = factor(framework, c("Naïve GLMM", "Standard occupancy",
                                         "False-positive occupancy")),
         threshold = factor(threshold, c("MaxF1", "MaxPrecision",
                                         "No threshold (MC)")),
         parameter = factor(parameter, rev(unname(nomes))),
         detector = factor(detector, c("BirdNET", "Custom")))
dir.create(out, showWarnings = FALSE, recursive = TRUE)
readr::write_csv(tab, file.path(out, "curiango-fig4-mc.csv"))

cores <- c("Naïve GLMM" = "grey35", "Standard occupancy" = "#1b7837",
           "False-positive occupancy" = "#762a83")
p <- ggplot(tab, aes(mean, parameter, colour = framework, shape = framework)) +
  geom_vline(xintercept = 0, linetype = "dashed", colour = "grey50") +
  geom_pointrange(aes(xmin = lower, xmax = upper),
                  position = position_dodge(width = 0.6), size = 0.4) +
  facet_grid(detector ~ threshold) +
  scale_colour_manual(values = cores) +
  scale_shape_manual(values = c(15, 16, 17)) +
  labs(x = "Effect on the latent nightly state (logit scale)", y = NULL,
       colour = NULL, shape = NULL) +
  theme_bw(base_size = 11) +
  theme(legend.position = "bottom", panel.grid.minor = element_blank())
ggsave(file.path(out, "curiango-fig4-mc.png"), p, width = 10, height = 6.5,
       dpi = 200)
# o caminho MC cai dentro da amplitude dos caminhos com limiar?
tab |>
  filter(framework == "False-positive occupancy") |>
  select(detector, parameter, threshold, mean, lower, upper) |>
  arrange(detector, parameter, threshold) |>
  print(n = Inf)
