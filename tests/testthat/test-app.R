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
  expect_error(review_queue(man["clip_file"], d), "lacks the column")
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
