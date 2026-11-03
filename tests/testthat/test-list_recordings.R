# Arvore de audio falsa: <raiz>/<sitio>/[subpasta/]<arquivo>
fake_audio <- function() {
  raiz <- withr::local_tempdir(.local_envir = parent.frame())
  dir.create(file.path(raiz, "ARA", "card1"), recursive = TRUE)
  dir.create(file.path(raiz, "BAI"))
  file.create(file.path(raiz, "ARA", "card1",
                        c("ARA01_20211001_190000.wav",
                          "ARA01_20211001_200000.WAV")),
              file.path(raiz, "BAI", "BAI01_20211001_190000.flac"),
              file.path(raiz, "BAI", "notes.txt"))
  raiz
}

test_that("list_recordings() takes the site from the first folder", {
  raiz <- fake_audio()
  rec <- suppressMessages(list_recordings(raiz))
  expect_named(rec, c("site", "source_audio"))
  expect_equal(rec$site, c("ARA", "ARA", "BAI"))
  expect_true(all(file.exists(rec$source_audio)))
  expect_false(any(grepl("notes", rec$source_audio)))
})

test_that("list_recordings() remaps the prefix and writes the CSV", {
  raiz <- fake_audio()
  csv <- file.path(withr::local_tempdir(), "recordings.csv")
  rec <- suppressMessages(list_recordings(raiz, remap_from = raiz,
                                          remap_to = "N:", file = csv))
  expect_true(all(startsWith(rec$source_audio, "N:/")))
  expect_equal(readr::read_csv(csv, show_col_types = FALSE), rec,
               ignore_attr = TRUE)
})

test_that("list_recordings() checks the audio of the predictions", {
  raiz <- fake_audio()
  pred <- tibble::tibble(
    begin_path = c(file.path(raiz, "BAI", "BAI01_20211001_190000.flac"),
                   "N:\\XAR\\XAR01_20211001_190000.wav"))
  expect_message(
    expect_warning(list_recordings(raiz, predictions = pred),
                   "1 audio file\\(s\\) of the predictions are not"),
    "1 of 2 audio files")
})

test_that("list_recordings() needs a site for loose files", {
  raiz <- withr::local_tempdir()
  file.create(file.path(raiz, "x_20211001_190000.wav"))
  expect_error(list_recordings(raiz), "directly in `audio_dir`")
  rec <- suppressMessages(list_recordings(raiz, site = "ARA"))
  expect_equal(rec$site, "ARA")
  expect_error(list_recordings(file.path(raiz, "none")), "existing folder")
  expect_error(list_recordings(raiz, site = c("A", "B")), "single site")
  expect_error(list_recordings(raiz, site = "ARA",
                               predictions = data.frame(x = 1)),
               "lacks the column begin_path")
  expect_error(list_recordings(raiz, audio_pattern = "\\.mp4$"),
               "No audio file")
})

test_that("list_recordings() warns about names without a date", {
  raiz <- withr::local_tempdir()
  dir.create(file.path(raiz, "ARA"))
  file.create(file.path(raiz, "ARA", "take1.wav"))
  expect_warning(suppressMessages(list_recordings(raiz)), "YYYYMMDD_HHMMSS")
})

test_that("the list feeds random_recordings in select_clips()", {
  ex <- system.file("extdata", "example", package = "sheepdog")
  pred <- suppressMessages(read_selection_tables(file.path(ex, "birdnet")))
  rec_ex <- readr::read_csv(file.path(ex, "recordings.csv"),
                            show_col_types = FALSE)
  raiz <- withr::local_tempdir()
  locais <- sub("^N:\\\\pam\\\\audio\\\\", "", rec_ex$source_audio)
  locais <- gsub("\\\\", "/", locais)
  for (d in unique(dirname(locais))) dir.create(file.path(raiz, d),
                                                recursive = TRUE)
  file.create(file.path(raiz, locais))
  rec <- suppressMessages(list_recordings(raiz, remap_from = paste0(raiz, "/"),
                                          remap_to = "N:/pam/audio/"))
  expect_equal(nrow(rec), nrow(rec_ex))
  a <- suppressMessages(select_clips(pred, "random_recordings",
                                     recordings = rec, seed = 1))
  b <- suppressMessages(select_clips(pred, "random_recordings",
                                     recordings = rec_ex, seed = 1))
  expect_equal(a$source_audio, b$source_audio)
})
