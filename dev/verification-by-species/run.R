# Quantos clipes verificados cada especie recebe em cada desenho do
# select_clips(), com os dados de exemplo (8 especies, 4 sitios). Mede o
# risco apontado na Fase A do crywolf: verificacao rara demais nas especies
# raras. Os positivos esperados usam a precisao de cada especie nos clipes
# revisados do exemplo (sem novo sorteio de vereditos).
# Rode da raiz do repositorio: Rscript dev/verification-by-species/run.R
devtools::load_all(quiet = TRUE)
suppressPackageStartupMessages(library(dplyr))

ex <- system.file("extdata", "example", package = "sheepdog")
det <- suppressMessages(read_selection_tables(file.path(ex, "birdnet")))
val <- suppressMessages(read_validations(
  list.files(file.path(ex, "validation"), full.names = TRUE)))
prec <- val |> group_by(species) |> summarise(prec = mean(tp))
rec <- file.path(ex, "recordings.csv")
n_rec <- nrow(readr::read_csv(rec, show_col_types = FALSE))

# cenario raro: lep_fus so com 15 deteccoes em ARA (sorteadas), como uma
# especie que mal aparece; as demais ficam como no exemplo
rara <- withr::with_seed(2026, det |>
  filter(folder_name(species_code) == "lep_fus", site == "ARA") |>
  slice_sample(n = 15))
det_rara <- bind_rows(filter(det, folder_name(species_code) != "lep_fus"), rara)

conta <- function(man, desenho) {
  man |> count(species = species_folder, name = "clips") |>
    mutate(desenho = desenho)
}
res <- list()
for (cen in c("exemplo", "rara")) {
  d <- if (cen == "rara") det_rara else det
  for (alvo in c(40, 80, 160)) {
    for (modo in c("top", "random_detections")) {
      man <- suppressMessages(suppressWarnings(select_clips(
        d, modo, threshold = if (modo == "random_detections") 0.5,
        target_total = alvo, seed = 2026)))
      res[[length(res) + 1]] <- conta(man, paste0(cen, ": ", modo,
                                                 ", target_total = ", alvo))
    }
  }
}
# random_recordings: cada gravacao sorteada e revisada para todas as
# especies; os positivos esperados sao as gravacoes em que a especie tem
# predicao >= 0,5, vezes a precisao
for (cen in c("exemplo", "rara")) {
  d <- if (cen == "rara") det_rara else det
  gravs <- d |> filter(confidence >= 0.5) |>
    distinct(species = folder_name(species_code), site, source_audio = begin_path) |>
    count(species, name = "rec_com_pred")
  for (fr in c(0.05, 0.1, 0.2)) {
    res[[length(res) + 1]] <- gravs |>
      transmute(species, clips = round(fr * n_rec), pos_rr = fr * rec_com_pred,
                desenho = paste0(cen, ": random_recordings, ", fr))
  }
}
tab <- bind_rows(res) |>
  left_join(prec, by = "species") |>
  mutate(pos = if_else(is.na(pos_rr), clips * prec, pos_rr),
         neg = clips - pos) |>
  select(desenho, species, clips, pos, neg)
saveRDS(tab, "dev/verification-by-species/results.rds")
largo <- tab |> mutate(txt = sprintf("%d (%.0f+)", clips, pos)) |>
  select(desenho, species, txt) |>
  tidyr::pivot_wider(names_from = species, values_from = txt)
print(as.data.frame(largo), right = FALSE)
cat("\nDeteccoes (>= 0.1) por especie:\n")
print(table(folder_name(det$species_code)))
