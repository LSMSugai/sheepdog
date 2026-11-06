# Predicoes simuladas: n_occ ocasioes (arquivos) por celula, dois clipes por
# ocasiao, e um estrato por celula com strata = "site_species"
rounds_detections <- function(n_occ = 20, sites = "A", species = "Sp_one") {
  grade <- expand.grid(site = sites, species_code = species, k = seq_len(n_occ),
                       clip = 0:1, stringsAsFactors = FALSE)
  dia <- sprintf("202401%02d", (grade$k - 1) %% 28 + 1)
  hora <- sprintf("%02d0000", (grade$k - 1) %/% 28)
  tibble::tibble(
    site = grade$site, species_code = grade$species_code,
    confidence = 0.6 + 0.3 * grade$clip,
    begin_path = paste0("/audio/", grade$site, "/", grade$site, "_", dia, "_",
                        hora, ".wav"),
    file_offset = 3 * grade$clip, begin_time = 3 * grade$clip,
    end_time = 3 * grade$clip + 3)
}

draw <- function(pred, ...) {
  suppressMessages(select_clips(pred, "random_detections", threshold = 0.5,
                                strata = "site_species", n_top = 2, ...))
}
ids <- function(m) unique(m$occasion_id)

test_that("two rounds do not repeat occasions and accumulate the probability", {
  pred <- rounds_detections(20)
  r1 <- draw(pred)
  expect_equal(unique(r1$round), 1L)
  expect_equal(unique(r1$inclusion_prob), 2 / 20)
  expect_equal(unique(r1$n_candidates), 20L)

  r2 <- draw(pred, previous = r1, candidates = attr(r1, "candidates"))
  expect_equal(unique(r2$round), 2L)
  expect_length(intersect(ids(r1), ids(r2)), 0)
  expect_equal(unique(r2$inclusion_prob), 4 / 20)
  expect_equal(unique(r2$inclusion_prob_round), 2 / 18)
  expect_equal(unique(r2$n_drawn), 4L)

  comb <- combine_rounds(list(r1, r2), attr(r1, "candidates"))
  expect_equal(unique(comb$inclusion_prob), 4 / 20)
  expect_equal(unique(comb$n_rounds), 2L)
  expect_equal(nrow(comb), nrow(r1) + nrow(r2))
})

test_that("the first round is the same draw as before", {
  pred <- rounds_detections(20)
  r1 <- draw(pred, seed = 7)
  esperado <- withr::with_seed(7, {
    sort(dplyr::slice_sample(
      dplyr::distinct(attr(r1, "candidates"), occasion_id), n = 2)$occasion_id)
  })
  expect_equal(sort(ids(r1)), esperado)
})

test_that("rounds go on until the stratum is exhausted", {
  pred <- rounds_detections(5)
  lista <- NULL
  feitas <- list()
  for (k in 1:3) {
    r <- draw(pred, previous = if (k > 1) dplyr::bind_rows(feitas),
              candidates = lista)
    if (k == 1) lista <- attr(r, "candidates")
    feitas[[k]] <- r
  }
  expect_equal(unique(feitas[[3]]$inclusion_prob), 1)
  expect_length(ids(feitas[[3]]), 1)
  expect_length(unique(unlist(lapply(feitas, ids))), 5)

  vazia <- draw(pred, previous = dplyr::bind_rows(feitas), candidates = lista)
  expect_equal(nrow(vazia), 0)
  expect_message(
    select_clips(pred, "random_detections", threshold = 0.5,
                 strata = "site_species", n_top = 2,
                 previous = dplyr::bind_rows(feitas), candidates = lista),
    "0 occasions drawn")
})

test_that("a round restricted to some cells leaves the others unchanged", {
  pred <- rounds_detections(10, sites = c("A", "B"))
  r1 <- draw(pred)
  lista <- attr(r1, "candidates")
  r2 <- draw(pred, previous = r1, candidates = lista,
             cells = data.frame(site = "A", species_code = "Sp_one"))
  expect_equal(unique(r2$site), "A")
  comb <- combine_rounds(list(r1, r2), lista)
  expect_equal(unique(comb$inclusion_prob[comb$site == "A"]), 4 / 10)
  expect_equal(unique(comb$inclusion_prob[comb$site == "B"]), 2 / 10)
  expect_equal(unique(comb$n_rounds[comb$site == "B"]), 1L)
  expect_error(draw(pred, previous = r1, candidates = lista,
                    cells = data.frame(site = "C", species_code = "Sp_one")),
               "No candidate occasion")
})

test_that("a different design is refused", {
  pred <- rounds_detections(20)
  r1 <- draw(pred)
  lista <- attr(r1, "candidates")
  expect_error(
    suppressMessages(select_clips(pred, "random_detections", threshold = 0.7,
                                  strata = "site_species", previous = r1,
                                  candidates = lista)), "threshold")
  expect_error(
    suppressMessages(select_clips(pred, "random_detections", threshold = 0.5,
                                  strata = "night", previous = r1,
                                  candidates = lista)), "strata")
  expect_error(
    suppressMessages(select_clips(pred, "random_detections", threshold = 0.5,
                                  occasion_unit = "minute",
                                  strata = "site_species", previous = r1,
                                  candidates = lista)), "occasion_unit")
  expect_error(draw(pred, previous = r1, candidates = lista,
                    max_per_species = 1), "max_per_species")
  expect_error(
    suppressMessages(select_clips(pred, "top", previous = r1)),
    "same design")
  expect_error(draw(pred, candidates = lista), "give `previous`")
})

test_that("a capped first round cannot have later rounds", {
  pred <- rounds_detections(20)
  r1 <- draw(pred, max_per_species = 1)
  expect_true(all(is.na(r1$n_candidates)))
  expect_error(draw(pred, previous = r1, candidates = attr(r1, "candidates")),
               "second stage")
})

test_that("changed predictions warn and keep the candidates", {
  pred <- rounds_detections(20)
  r1 <- draw(pred)
  lista <- attr(r1, "candidates")
  mais <- rounds_detections(25)
  expect_warning(r2 <- draw(mais, previous = r1, candidates = lista),
                 "changed since the first round")
  expect_equal(unique(r2$n_candidates), 20L)
  expect_equal(unique(r2$inclusion_prob), 4 / 20)
  expect_true(all(ids(r2) %in% lista$occasion_id))
})

test_that("the candidates survive a csv and are found beside the manifest", {
  pred <- rounds_detections(20)
  r1 <- draw(pred)
  d <- withr::local_tempdir()
  readr::write_csv(r1, file.path(d, "clip_manifest.csv"))
  readr::write_csv(attr(r1, "candidates"), file.path(d, "candidates.csv"))
  r2 <- draw(pred, previous = file.path(d, "clip_manifest.csv"))
  expect_equal(unique(r2$inclusion_prob), 4 / 20)
  expect_length(intersect(ids(r1), ids(r2)), 0)

  d2 <- withr::local_tempdir()
  readr::write_csv(r2, file.path(d2, "clip_manifest.csv"))
  comb <- read_validation_tables(
    c(file.path(d, "clip_manifest.csv"), file.path(d2, "clip_manifest.csv")),
    candidates = file.path(d, "candidates.csv"))
  expect_equal(unique(comb$inclusion_prob), 4 / 20)
})

test_that("rounds drawn without `previous` are not combined", {
  pred <- rounds_detections(20)
  r1 <- draw(pred)
  expect_error(combine_rounds(list(r1, draw(pred, seed = 1)),
                              attr(r1, "candidates")), "same round")
  repetida <- draw(pred)
  repetida$round <- 2L
  expect_error(combine_rounds(list(r1, repetida), attr(r1, "candidates")),
               "more than one round")
})

test_that("later rounds change the seed", {
  # com a mesma semente, a rodada 2 repetiria as posicoes da rodada 1, e
  # pegaria sempre as vizinhas das ocasioes ja sorteadas
  pred <- rounds_detections(28)
  lista <- attr(draw(pred), "candidates")
  ordem <- match(lista$occasion_id, unique(lista$occasion_id))
  distancia <- vapply(1:40, function(s) {
    r1 <- draw(pred, seed = s)
    r2 <- draw(pred, seed = s, previous = r1, candidates = lista)
    p1 <- match(ids(r1), lista$occasion_id)
    p2 <- match(ids(r2), lista$occasion_id)
    min(abs(outer(p1, p2, `-`)))
  }, numeric(1))
  expect_gt(mean(distancia), 2)
})

test_that("\"top\" leaves out the clips already reviewed", {
  pred <- rounds_detections(6)
  a <- suppressMessages(select_clips(pred, "top", n_top = 1))
  b <- suppressMessages(select_clips(pred, "top", n_top = 1, previous = a))
  expect_equal(unique(b$round), 2L)
  expect_true(all(is.na(b$inclusion_prob)))
  expect_length(intersect(paste(a$occasion_id, a$clip_start),
                          paste(b$occasion_id, b$clip_start)), 0)
})

test_that("the combined rounds are a simple random sample", {
  skip_on_cran()
  pred <- rounds_detections(12)
  lista <- attr(draw(pred), "candidates")
  sorteios <- lapply(1:300, function(s) {
    r1 <- draw(pred, seed = 1000 + s)
    r2 <- draw(pred, seed = 1000 + s, previous = r1, candidates = lista)
    c(ids(r1), ids(r2))
  })
  # cada ocasiao entra em 4/12 das amostras; dois sorteios independentes de
  # 4 em 12 dariam erro-padrao de cerca de 0,027
  freq <- table(factor(unlist(sorteios), levels = lista$occasion_id)) / 300
  expect_lt(max(abs(freq - 4 / 12)), 0.1)
  pares <- vapply(sorteios, function(x) all(lista$occasion_id[1:2] %in% x), TRUE)
  expect_lt(abs(mean(pares) - (4 / 12) * (3 / 11)), 0.06)
})

test_that("weighted precision of combined rounds matches a single draw", {
  # dois estratos desiguais: rodadas combinadas e um sorteio unico do mesmo
  # tamanho dao a mesma probabilidade por estrato, logo o mesmo estimador
  pred <- rounds_detections(20, sites = c("A", "B"))
  pred <- pred[!(pred$site == "B" & grepl("_2024011|_2024012", pred$begin_path)), ]
  r1 <- draw(pred)
  lista <- attr(r1, "candidates")
  r2 <- draw(pred, previous = r1, candidates = lista)
  comb <- combine_rounds(list(r1, r2), lista)
  unico <- suppressMessages(select_clips(pred, "random_detections",
                                         threshold = 0.5, n_top = 4,
                                         strata = "site_species"))
  por_local <- function(x) {
    attr(x, "candidates") <- NULL
    dplyr::arrange(dplyr::distinct(x, site, inclusion_prob), site)
  }
  expect_equal(por_local(comb), por_local(unico))
})

test_that("stacked rounds that were not combined raise a warning", {
  pred <- rounds_detections(40)
  r1 <- draw(pred, seed = 1)
  r2 <- draw(pred, previous = r1, candidates = attr(r1, "candidates"))
  v <- dplyr::bind_rows(r1, r2) |>
    dplyr::mutate(verdict = "positive", reviewed_path = NA_character_)
  expect_warning(suggest_thresholds(v, min_n = 1), "combine_rounds")
  comb <- combine_rounds(v, attr(r1, "candidates"))
  expect_no_warning(suggest_thresholds(comb, min_n = 1))
})

test_that("review_support() flags cells that reached the target in the last round", {
  pred <- rounds_detections(40, sites = c("A", "B"))
  r1 <- draw(pred)
  lista <- attr(r1, "candidates")
  r2 <- draw(pred, previous = r1, candidates = lista)
  r2 <- r2[r2$site == "A", ]
  comb <- dplyr::bind_rows(r1, r2) |>
    dplyr::mutate(verdict = "positive") |>
    combine_rounds(lista)
  expect_message(rs <- review_support(comb, pred, min_n = 6, conf_high = 0.5),
                 "last round")
  expect_equal(rs$n_rounds[rs$site == "A"], 2L)
  expect_true(rs$reached_last_round[rs$site == "A"])
  expect_false(rs$reached_last_round[rs$site == "B"])
})

test_that("extract_validation_clips() writes the candidates and protects the manifest", {
  skip_if_not(file.exists(file.path(sim_root(), "tabelas")))
  d <- withr::local_tempdir()
  args <- list(data_dir = file.path(sim_root(), "tabelas"), output_dir = d,
               sampling_mode = "random_detections", threshold = 0.5, n_top = 1,
               simulate = TRUE, make_zip = FALSE)
  suppressMessages(suppressWarnings(do.call(extract_validation_clips, args)))
  expect_true(file.exists(file.path(d, "candidates.csv")))
  args$previous <- file.path(d, "clip_manifest.csv")
  expect_error(do.call(extract_validation_clips, args), "another")
  d2 <- withr::local_tempdir()
  args$output_dir <- d2
  m <- suppressMessages(suppressWarnings(do.call(extract_validation_clips, args)))
  expect_equal(unique(m$round), 2L)
  expect_true(file.exists(file.path(d2, "candidates.csv")))
})
