# Fixture multiespecies do esquema sheepdog-occupancy 1.3, compartilhada com
# o crywolf (fp_occu_ms(), Fase A do roadmap dele): tres especies do exemplo,
# escrita em tests/testthat/fixtures/export-1.3-ms/.
#   * phy_cuv e ela_bic: comuns, detectadas e revisadas nos quatro sitios;
#   * lep_fus: rara, so com as deteccoes de ARA e BAI (ausente de NHE e XAR)
#     e 15 clipes revisados por sitio.
# Calibracao com a temperatura simulada da fixture 1.3 e efeitos de especie
# e de sitio x especie (tp ~ logit_conf + temp_z + (logit_conf | species) +
# (1 | site:species)); sem grade, as versoes (20, "sample", seed 2026) saem
# do export. A raridade e construida para o teste e nao descreve a especie.
# Run from the repository root (needs brms with a Stan backend and arrow):
#   Rscript data-raw/make_export_fixture_ms.R
devtools::load_all(quiet = TRUE)
suppressPackageStartupMessages(library(dplyr))

ex <- system.file("extdata", "example", package = "sheepdog")
out <- "tests/testthat/fixtures/export-1.3-ms"
especies <- c("phy_cuv", "ela_bic", "lep_fus")
rara <- "lep_fus"
sitios_rara <- c("ARA", "BAI")

det <- read_selection_tables(file.path(ex, "birdnet")) |>
  filter(folder_name(species_code) %in% especies,
         folder_name(species_code) != rara | site %in% sitios_rara)

# clipes revisados das tres especies; da rara, 15 por sitio (sorteados)
val_tab <- list.files(file.path(ex, "validation"), full.names = TRUE) |>
  lapply(readr::read_csv, col_types = readr::cols(.default = "c"), na = "") |>
  bind_rows() |>
  filter(species_folder %in% especies,
         species_folder != rara | site %in% sitios_rara)
val_tab <- withr::with_seed(2026, bind_rows(
  filter(val_tab, species_folder != rara),
  val_tab |> filter(species_folder == rara) |> group_by(site) |>
    slice_sample(n = 15) |> ungroup()))
val_dir <- withr::local_tempdir()
val_files <- vapply(split(val_tab, val_tab$site), function(v) {
  f <- file.path(val_dir, paste0("validation_by_clip_", v$site[1], ".csv"))
  readr::write_csv(v, f, na = "NA")
  f
}, character(1))

# temperatura simulada por data, como na fixture 1.3
rec <- readr::read_csv(file.path(ex, "recordings.csv"), show_col_types = FALSE)
datas <- sort(unique(regmatches(rec$source_audio,
                                regexpr("[0-9]{8}", rec$source_audio))))
temp_dia <- withr::with_seed(2026, tibble(
  data = datas, temp = round(stats::rnorm(length(datas), 22, 3), 1)))
centro <- mean(temp_dia$temp)
escala <- stats::sd(temp_dia$temp)
covs <- tibble(site = rec$site, source_audio = rec$source_audio,
               data = regmatches(rec$source_audio,
                                 regexpr("[0-9]{8}", rec$source_audio))) |>
  left_join(temp_dia, by = "data") |>
  mutate(temp_z = round((temp - centro) / escala, 4)) |>
  select(site, source_audio, temp_z)
val <- read_validations(val_files, keep = "source_audio") |>
  mutate(source_audio = gsub("\\\\", "/", source_audio),
         data = regmatches(source_audio, regexpr("[0-9]{8}", source_audio))) |>
  left_join(temp_dia, by = "data") |>
  mutate(temp_z = (temp - centro) / escala)
f <- tp ~ logit_conf + temp_z + (logit_conf | species) + (1 | site:species)
fit <- fit_calibration(val, f, engine = "brms",
                       prior = calibration_prior(f, val),
                       chains = 4, iter = 2000, refresh = 0, seed = 2026,
                       control = list(adapt_delta = 0.99))

unlink(out, recursive = TRUE)
export_occupancy_data(out, det, recordings = file.path(ex, "recordings.csv"),
                      validation = val_files, fit = fit,
                      occasion_covariates = covs,
                      n_draws = 20, n_versions = 20, rule = "sample",
                      covariate_scaling = list(temp_z = c(center = centro,
                                                          scale = escala)),
                      classifier = "example", overwrite = TRUE)
# a data de criacao e a versao mudariam a cada execucao
sc <- jsonlite::read_json(file.path(out, "schema.json"))
sc$created <- "2026-11-02T00:00:00-0400"
sc$sites <- I(unlist(sc$sites)); sc$species <- I(unlist(sc$species))
sc$occasion_covariates <- I(unlist(sc$occasion_covariates))
sc$calibration$keys <- I(unlist(sc$calibration$keys))
sc$calibration$covariates <- I(unlist(sc$calibration$covariates))
sc$occasion_draws$species <- I(unlist(sc$occasion_draws$species))
jsonlite::write_json(sc, file.path(out, "schema.json"), auto_unbox = TRUE,
                     pretty = TRUE, digits = NA)
