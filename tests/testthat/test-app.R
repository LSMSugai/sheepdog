# WAV PCM de 16 bits com um tom de 1 kHz
escreve_wav <- function(f, dur = 0.5, sr = 8000) {
  y <- as.integer(sin(2 * pi * 1000 * seq(0, dur, by = 1 / sr)) * 8000)
  con <- file(f, "wb")
  on.exit(close(con))
  n <- length(y)
  writeChar("RIFF", con, eos = NULL)
  writeBin(as.integer(36 + 2 * n), con, size = 4, endian = "little")
  writeChar("WAVEfmt ", con, eos = NULL)
  writeBin(16L, con, size = 4, endian = "little")
  writeBin(c(1L, 1L), con, size = 2, endian = "little")
  writeBin(c(as.integer(sr), as.integer(2 * sr)), con, size = 4,
           endian = "little")
  writeBin(c(2L, 16L), con, size = 2, endian = "little")
  writeChar("data", con, eos = NULL)
  writeBin(as.integer(2 * n), con, size = 4, endian = "little")
  writeBin(y, con, size = 2, endian = "little")
}

# Manifesto de 6 clipes (2 especies) com revisores e os clipes cortados
app_dados <- function(d) {
  man <- tibble::tibble(
    site = "A", species_code = rep(c("Sp a", "Sp b"), each = 3),
    species_folder = rep(c("sp_a", "sp_b"), each = 3),
    night = "20211001", recording_hour = 20, confidence = 0.8,
    sampling_mode = "top",
    clip_file = paste0("clip", 1:6, ".wav"),
    reviewer = rep(c("ana", "bia"), 3),
    second_reviewer = c("bia", NA, NA, NA, NA, NA))
  for (i in seq_len(nrow(man))) {
    dir.create(file.path(d, "clips", man$species_folder[i]),
               recursive = TRUE, showWarnings = FALSE)
    escreve_wav(file.path(d, "clips", man$species_folder[i],
                          man$clip_file[i]))
  }
  man
}

test_that("the verdicts log keeps the last verdict of each reviewer", {
  f <- withr::local_tempfile(fileext = ".csv")
  expect_identical(nrow(read_verdict_log(f)), 0L)
  append_verdict(f, "c1.wav", "sp_a", "ana", "positive")
  append_verdict(f, "c2.wav", "sp_a", "ana", "negative")
  append_verdict(f, "c1.wav", "sp_a", "ana", "uncertain")
  append_verdict(f, "c1.wav", "sp_a", "bia", "positive")
  log <- read_verdict_log(f)
  expect_named(log, c("clip_file", "species_folder", "reviewer", "verdict",
                      "time"))
  expect_identical(nrow(log), 3L)
  expect_identical(log$verdict[log$clip_file == "c1.wav" &
                                 log$reviewer == "ana"], "uncertain")
  # sem revisor, a coluna fica vazia
  append_verdict(f, "c3.wav", "sp_a", NULL, "negative")
  expect_true(is.na(read_verdict_log(f)$reviewer[4]))
  readr::write_csv(tibble::tibble(clip_file = "x", species_folder = "y",
                                  reviewer = "z", verdict = "talvez",
                                  time = "t"), f)
  expect_error(read_verdict_log(f), "Unknown verdict")
})

test_that("the queue follows the reviewer of assign_reviewers()", {
  d <- withr::local_tempdir()
  man <- app_dados(d)
  fila <- review_queue(man, file.path(d, "clips"), "bia")
  # os clipes de bia mais o da sobreposicao
  expect_setequal(fila$clip_file, c("clip1.wav", "clip2.wav", "clip4.wav",
                                    "clip6.wav"))
  expect_true(all(file.exists(fila$path)))
  expect_identical(nrow(review_queue(man, file.path(d, "clips"))), 6L)
  expect_error(review_queue(man, file.path(d, "clips"), "caio"),
               "No clip")
  expect_error(review_queue(man, file.path(d, "nada")), "None of the clips")
  file.remove(fila$path[1])
  expect_warning(review_queue(man, file.path(d, "clips")), "not found")
  expect_error(suppressWarnings(review_queue(man["clip_file"], d)),
               "lacks the column")
})

test_that("the app writes each verdict and moves to the next clip", {
  skip_if_not_installed("shiny")
  d <- withr::local_tempdir()
  man <- app_dados(d)
  f <- file.path(d, "verdicts.csv")
  # bia: clip1 e clip2 (sp_a), clip4 e clip6 (sp_b)
  fila <- review_queue(man, file.path(d, "clips"), "bia")
  shiny::testServer(review_server, args = list(
    fila = fila, verdicts_file = f, reviewer = "bia"), {
    session$setInputs(species = "", pending = TRUE)
    estado <- session$returned
    expect_identical(estado$current(), 1L)
    session$setInputs(positive = 1)
    expect_identical(estado$current(), 2L)
    session$setInputs(key = "n")
    session$setInputs(key = "u")
    expect_identical(estado$current(), 4L)
    expect_identical(unname(estado$verdicts()),
                     c("positive", "negative", "uncertain"))
    session$setInputs(key = "ArrowLeft")
    expect_identical(estado$current(), 3L)
    expect_match(output$progress, "3 of 4")
    # filtro por especie: so o clipe de sp_b ainda nao revisado
    session$setInputs(species = "sp_b")
    expect_identical(fila$clip_file[estado$current()], "clip6.wav")
  })
  log <- read_verdict_log(f)
  expect_identical(log$verdict, c("positive", "negative", "uncertain"))
  expect_identical(log$clip_file, c("clip1.wav", "clip2.wav", "clip4.wav"))
  expect_true(all(log$reviewer == "bia"))
  # ao reabrir, os ja revisados saem da fila
  shiny::testServer(review_server, args = list(
    fila = fila, verdicts_file = f, reviewer = "bia"), {
    session$setInputs(species = "", pending = TRUE)
    expect_identical(session$returned$current(), 4L)
    session$setInputs(pending = FALSE)
    expect_identical(session$returned$current(), 1L)
    expect_match(output$current_verdict, "positive")
  })
})

test_that("app_verdicts() returns the table of classify_review()", {
  d <- withr::local_tempdir()
  man <- app_dados(d)
  f <- file.path(d, "verdicts.csv")
  append_verdict(f, "clip1.wav", "sp_a", "ana", "positive")
  append_verdict(f, "clip1.wav", "sp_a", "bia", "negative")
  append_verdict(f, "clip2.wav", "sp_a", "bia", "positive")
  append_verdict(f, "clip3.wav", "sp_a", "ana", "uncertain")
  v <- suppressMessages(app_verdicts(man, f, file.path(d, "clips"),
                                     reviewer = "ana"))
  expect_identical(nrow(v), 6L)
  expect_identical(v$verdict, c("positive", "not_reviewed", "uncertain",
                                rep("not_reviewed", 3)))
  expect_true(all(file.exists(v$reviewed_path)))
  expect_true(all(v$reviewer == "ana"))
  # todos os revisores: uma linha por clipe e revisor
  todos <- suppressMessages(app_verdicts(man, f))
  expect_identical(nrow(todos), 7L)
  expect_true(all(is.na(todos$reviewed_path)))
  ag <- suppressWarnings(reviewer_agreement(
    dplyr::filter(todos, !is.na(reviewer))))
  expect_identical(ag$n_clips, 1L)
  cons <- suppressMessages(consensus_verdicts(
    dplyr::filter(todos, !is.na(reviewer))))
  expect_identical(cons$verdict[cons$clip_file == "clip1.wav"],
                   "disagreement")
  # incertos ficam fora da precisao
  p <- precision_by_bin(v, min_n = 1)
  expect_identical(sum(p$n_reviewed), 1L)
  append_verdict(f, "fora.wav", "sp_a", "ana", "positive")
  expect_warning(suppressMessages(app_verdicts(man, f)), "not in the")
})

test_that("the review queue can be a reactive that starts empty", {
  skip_if_not_installed("shiny")
  d <- withr::local_tempdir()
  man <- app_dados(d)
  cortada <- review_queue(man, file.path(d, "clips"))
  f <- file.path(d, "verdicts.csv")
  entrada <- shiny::reactiveVal(NULL)
  shiny::testServer(review_server, args = list(
    fila = entrada, verdicts_file = f, reviewer = "ana"), {
      session$setInputs(species = "", pending = TRUE)
      expect_true(is.na(atual()))
      expect_match(output$current_verdict, "Sampling tab")
      session$setInputs(positive = 1)
      expect_false(file.exists(f))
      # clipes recem-cortados chegam a fila
      entrada(cortada)
      session$flushReact()
      expect_identical(atual(), 1L)
      expect_identical(output$progress, "0 of 6 clips reviewed")
      session$setInputs(positive = 2)
      expect_identical(read_verdict_log(f)$clip_file, "clip1.wav")
      expect_identical(atual(), 2L)
    })
})

test_that("sampling_args() keeps only the filled fields", {
  a <- sampling_args(list(mode = "random_detections", occasion_unit = "file",
                          threshold = NA, n_top = 2, min_confidence = 0.1,
                          seed = 2026, target_total = NA,
                          max_per_species = 5, sites = NULL,
                          species = c("boa-ran"), hour_start = NA,
                          hour_end = NA, remap_from = "", remap_to = "",
                          strata = "night", recording_fraction = 0.5))
  expect_identical(a$strata, "night")
  expect_identical(a$max_per_species, 5)
  expect_null(a$threshold)
  expect_null(a$remap_from)
  expect_null(a$recording_fraction)
})

test_that("the sampling tab draws, then cuts and writes the manifest", {
  skip_if_not_installed("shiny")
  # o corte de verdade usa o av
  skip_if_not_installed("av")
  ex <- system.file("extdata", "example", package = "sheepdog")
  det <- suppressMessages(read_selection_tables(file.path(ex, "birdnet")))
  out <- withr::local_tempdir()
  shiny::testServer(sampling_server, args = list(
    detections = det, selection_dir = file.path(ex, "birdnet"),
    output_dir = out, classifier = "test"), {
      session$setInputs(mode = "random_detections", occasion_unit = "file",
                        threshold = 0.5, n_top = 1, strata = "night",
                        target_total = NA, max_per_species = NA,
                        min_confidence = 0.1, sites = "ARA", species = NULL,
                        hour_start = NA, hour_end = NA, seed = 2026,
                        remap_from = "", remap_to = "", simulate = TRUE,
                        replace = FALSE)
      session$setInputs(cut = 1)
      expect_match(notas(), "Draw the clips first")
      session$setInputs(draw = 1)
      sel <- selecao()
      ref <- suppressWarnings(suppressMessages(select_clips(
        det, sampling_mode = "random_detections", threshold = 0.5,
        n_top = 1, strata = "night", sites = "ARA", seed = 2026)))
      expect_identical(sel$clip_file, ref$clip_file)
      expect_true(all(sel$site == "ARA"))
      expect_match(output$counts, "ARA")
      # simulado: nada gravado, a fila nao recarrega
      session$setInputs(cut = 2)
      expect_true(all(status()$status == "audio_not_found"))
      expect_false(file.exists(file.path(out, "clip_manifest.csv")))
      expect_identical(cortes(), 0L)
      session$setInputs(simulate = FALSE, cut = 3)
      man <- readr::read_csv(file.path(out, "clip_manifest.csv"),
                             show_col_types = FALSE)
      expect_identical(man$clip_file, sel$clip_file)
      info <- readr::read_csv(file.path(out, "extraction_info.csv"),
                              show_col_types = FALSE)
      expect_identical(info$value[info$key == "select_clips.strata"],
                       "night")
      expect_identical(info$value[info$key == "classifier"], "test")
      expect_identical(cortes(), 1L)
      # nao sobrescreve o manifesto sem pedir
      session$setInputs(cut = 4)
      expect_match(notas(), "already exists")
      expect_identical(cortes(), 1L)
      # top avisa que nao estima falsos positivos
      session$setInputs(mode = "top", draw = 2)
      expect_true(any(grepl("false-positive rate", notas())))
    })
})

test_that("the export tab writes the occupancy tables with the verdicts", {
  skip_if_not_installed("shiny")
  ex <- system.file("extdata", "example", package = "sheepdog")
  det <- suppressMessages(read_selection_tables(file.path(ex, "birdnet")))
  rec <- readr::read_csv(file.path(ex, "recordings.csv"),
                         show_col_types = FALSE)
  out <- withr::local_tempdir()
  man <- suppressWarnings(suppressMessages(select_clips(
    det, sampling_mode = "random_detections", threshold = 0.5, n_top = 1,
    sites = "ARA")))
  readr::write_csv(man, file.path(out, "clip_manifest.csv"))
  f <- file.path(out, "verdicts.csv")
  for (i in 1:4) {
    append_verdict(f, man$clip_file[i], man$species_folder[i], "ana",
                   c("positive", "negative")[1 + i %% 2])
  }
  # dois revisores discordam num clipe
  append_verdict(f, man$clip_file[1], man$species_folder[1], "bia",
                 "positive")
  shiny::testServer(export_server, args = list(
    detections = det, output_dir = out, clips_dir = file.path(out, "clips"),
    verdicts_file = f, recordings = rec), {
      session$setInputs(occasion_unit = "file", min_confidence = 0.1,
                        export_dir = file.path(out, "occupancy"),
                        overwrite = FALSE, export = 1)
      r <- resultado()
      expect_false(is.null(r))
      expect_true(file.exists(file.path(out, "occupancy", "schema.json")))
      expect_identical(r$schema$schema, "sheepdog-occupancy")
      expect_identical(nrow(r$tables$validation), 4L)
      expect_identical(sum(r$tables$validation$verdict == "disagreement"),
                       1L)
      expect_match(output$tables, "validation")
      # sem overwrite, a segunda exportacao falha com aviso no app
      session$setInputs(export = 2)
      expect_true(any(grepl("^Error", notas())))
    })
})

test_that("app_verdicts() reports the clips marked more than once", {
  d <- withr::local_tempdir()
  man <- app_dados(d)
  f <- file.path(d, "verdicts.csv")
  append_verdict(f, "clip1.wav", "sp_a", "ana", "positive")
  append_verdict(f, "clip1.wav", "sp_a", "ana", "positive")
  append_verdict(f, "clip2.wav", "sp_a", "ana", "positive")
  append_verdict(f, "clip2.wav", "sp_a", "ana", "negative")
  append_verdict(f, "clip3.wav", "sp_a", "bia", "positive")
  msgs <- character()
  v <- withCallingHandlers(
    app_verdicts(man, f, reviewer = "ana"),
    message = function(m) {
      msgs <<- c(msgs, conditionMessage(m))
      invokeRestart("muffleMessage")
    })
  expect_true(any(grepl("2 clip\\(s\\) marked more than once by the same reviewer, 1 of them",
                        msgs)))
  expect_identical(v$verdict[v$clip_file == "clip2.wav"], "negative")
  # um clipe marcado por dois revisores nao conta como remarcado
  append_verdict(f, "clip3.wav", "sp_a", "ana", "negative")
  msgs <- character()
  withCallingHandlers(
    app_verdicts(man, f, reviewer = "bia"),
    message = function(m) {
      msgs <<- c(msgs, conditionMessage(m))
      invokeRestart("muffleMessage")
    })
  expect_false(any(grepl("more than once", msgs)))
})

test_that("post_validation() reads the verdicts file of the app", {
  d <- withr::local_tempdir()
  man <- app_dados(d)
  man$confidence <- c(0.6, 0.7, 0.8, 0.6, 0.7, 0.9)
  man$source_audio <- "rec.wav"
  f <- file.path(d, "verdicts.csv")
  append_verdict(f, "clip1.wav", "sp_a", "ana", "positive")
  append_verdict(f, "clip2.wav", "sp_a", "bia", "negative")
  append_verdict(f, "clip4.wav", "sp_b", "bia", "positive")
  append_verdict(f, "clip4.wav", "sp_b", "bia", "negative")
  saida <- file.path(d, "pv")
  res <- suppressMessages(post_validation(
    file.path(d, "clips"), man, saida, verdicts_file = f, min_n = 1))
  expect_true(file.exists(file.path(saida, "validation_by_clip.csv")))
  expect_identical(nrow(res$validation), 6L)
  expect_identical(res$validation$verdict,
                   c("positive", "negative", "not_reviewed", "negative",
                     rep("not_reviewed", 2)))
  expect_true(all(file.exists(res$validation$reviewed_path)))
  expect_identical(sum(res$precision$n_reviewed), 3L)
  # so um revisor
  so_ana <- suppressMessages(post_validation(
    manifest_path = man, output_dir = file.path(d, "pv_ana"),
    verdicts_file = f, reviewer = "ana", min_n = 1))
  expect_identical(sum(so_ana$validation$verdict == "positive"), 1L)
  # dois revisores no mesmo clipe: consenso
  append_verdict(f, "clip1.wav", "sp_a", "bia", "negative")
  cons <- suppressMessages(post_validation(
    manifest_path = man, output_dir = file.path(d, "pv_cons"),
    verdicts_file = f, min_n = 1))
  expect_identical(nrow(cons$validation), 6L)
  expect_identical(cons$validation$verdict[cons$validation$clip_file ==
                                             "clip1.wav"], "disagreement")
  expect_error(post_validation(manifest_path = man, output_dir = saida),
               "Give `review_dir`")
  expect_error(suppressMessages(post_validation(
    manifest_path = man, output_dir = saida, verdicts_file = f,
    reviewer = "zeca")), "Check `verdicts_file`")
})
