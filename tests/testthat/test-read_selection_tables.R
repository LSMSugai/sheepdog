test_that("read_selection_tables() names sites by folder", {
  pred <- suppressMessages(
    read_selection_tables(file.path(sim_root(), "tabelas")))
  expect_identical(names(pred)[1], "site")
  expect_setequal(unique(pred$site), c("ARA", "XAR", "BAI"))
  expect_true(all(c("begin_time", "end_time", "species_code", "confidence",
                    "begin_path", "file_offset") %in% names(pred)))
})

test_that("read_selection_tables() reports missing columns", {
  d <- withr::local_tempdir()
  dir.create(file.path(d, "SITE"))
  writeLines("Begin Time (s)\tConfidence\n0\t0.5",
             file.path(d, "SITE", "BirdNET_SelectionTable.txt"))
  expect_error(suppressMessages(read_selection_tables(d)), "lacks the columns")
})

test_that("read_selection_tables() fails when nothing is found", {
  expect_error(read_selection_tables(withr::local_tempdir()),
               "No selection table")
})

# Divide uma tabela combinada em tabelas por audio, como a GUI do BirdNET
# grava sem "Combine selection tables": selection recomeca em 1 em cada
# tabela. `vazio` acrescenta uma tabela so com o cabecalho.
split_per_audio <- function(combinada, pasta, vazio = NULL) {
  tab <- utils::read.delim(combinada, check.names = FALSE,
                           stringsAsFactors = FALSE)
  dir.create(pasta, recursive = TRUE, showWarnings = FALSE)
  audio <- sub("^.*\\\\", "", tab[["Begin Path"]])
  for (a in unique(audio)) {
    parte <- tab[audio == a, ]
    parte$Selection <- seq_len(nrow(parte))
    utils::write.table(parte, file.path(pasta, paste0(
      sub("\\.wav$", "", a), ".BirdNET.selection.table.txt")),
      sep = "\t", quote = FALSE, row.names = FALSE)
  }
  if (!is.null(vazio)) {
    utils::write.table(tab[0, ], file.path(pasta, paste0(
      vazio, ".BirdNET.selection.table.txt")),
      sep = "\t", quote = FALSE, row.names = FALSE)
  }
  invisible(unique(audio))
}

test_that("per-audio tables give the same result as the combined table", {
  comb <- file.path(sim_root(), "tabelas", "output_ARA",
                    "BirdNET_SelectionTable.txt")
  d <- withr::local_tempdir()
  # uma gravacao sem predicoes no meio da ordem dos arquivos
  split_per_audio(comb, file.path(d, "output_ARA"),
                  vazio = "ARA01_20220110_190000")
  esperado <- suppressMessages(read_selection_tables(dirname(comb)))
  obtido <- suppressMessages(read_selection_tables(d))
  expect_identical(obtido$site, rep("ARA", nrow(obtido)))
  expect_equal(as.data.frame(obtido), as.data.frame(esperado),
               ignore_attr = TRUE)
  expect_identical(obtido$selection, seq_len(nrow(obtido)))
})

test_that("a folder with a combined table ignores its per-audio tables", {
  comb <- file.path(sim_root(), "tabelas", "output_ARA",
                    "BirdNET_SelectionTable.txt")
  d <- withr::local_tempdir()
  split_per_audio(comb, file.path(d, "ARA"))
  file.copy(comb, file.path(d, "ARA"))
  expect_message(pred <- read_selection_tables(d), "ignored")
  esperado <- suppressMessages(read_selection_tables(dirname(comb)))
  expect_identical(nrow(pred), nrow(esperado))
})

test_that("per_audio_pattern = NULL reads only combined tables", {
  comb <- file.path(sim_root(), "tabelas", "output_ARA",
                    "BirdNET_SelectionTable.txt")
  d <- withr::local_tempdir()
  split_per_audio(comb, file.path(d, "ARA"))
  expect_error(read_selection_tables(d, per_audio_pattern = NULL),
               "per_audio_pattern")
})

test_that("score columns are the same from a folder and from the table", {
  comb <- file.path(sim_root(), "tabelas", "output_ARA",
                    "BirdNET_SelectionTable.txt")
  d <- withr::local_tempdir()
  split_per_audio(comb, d)
  expect_equal(as.data.frame(read_score_columns(d)),
               as.data.frame(read_score_columns(comb)),
               ignore_attr = TRUE)
})

test_that("empty per-audio tables are skipped with a warning", {
  d <- withr::local_tempdir()
  dir.create(file.path(d, "ARA"))
  file.create(file.path(d, "ARA", c("a.BirdNET.selection.table.txt",
                                    "b.BirdNET.selection.table.txt")))
  expect_error(
    expect_warning(suppressMessages(read_selection_tables(d)), "Empty table"),
    "No prediction read")
})

test_that("read_score_columns() handles empty and nested folders", {
  comb <- file.path(sim_root(), "tabelas", "output_ARA",
                    "BirdNET_SelectionTable.txt")
  vazia <- withr::local_tempdir()
  expect_null(read_score_columns(vazia))
  file.create(file.path(vazia, "a.BirdNET.selection.table.txt"))
  expect_null(suppressWarnings(read_score_columns(vazia)))
  d <- withr::local_tempdir()
  split_per_audio(comb, file.path(d, "um"))
  split_per_audio(comb, file.path(d, "dois"))
  expect_error(read_score_columns(d), "one folder per site")
})

test_that("per-audio tables in the format of the BirdNET GUI are read", {
  # cabecalho, ordem das colunas e formato dos numeros de uma tabela real
  # por audio do BirdNET GUI (Common Name antes de Species Code, tempos com
  # uma casa decimal, Begin Time igual a File Offset); valores inventados
  cab <- paste("Selection", "View", "Channel", "Begin Time (s)",
               "End Time (s)", "Low Freq (Hz)", "High Freq (Hz)",
               "Common Name", "Species Code", "Confidence", "Begin Path",
               "File Offset (s)", sep = "\t")
  linha <- function(sel, t0, nome, cod, conf, audio) {
    paste(sel, "Spectrogram 1", 1, sprintf("%.1f", t0),
          sprintf("%.1f", t0 + 3), 0, 15000, nome, cod,
          sprintf("%.4f", conf), paste0("/Volumes/audio/", audio, ".flac"),
          sprintf("%.1f", t0), sep = "\t")
  }
  d <- withr::local_tempdir()
  dir.create(file.path(d, "Campus01"))
  a1 <- "Campus01_20261003_074339"
  a2 <- "Campus01_20261003_084339"
  writeLines(c(cab, linha(1, 0, "Sayaca Tanager", "saytan1", 0.5603, a1),
               linha(2, 8, "Rufous-collared Sparrow", "rucspa1", 0.2303, a1)),
             file.path(d, "Campus01", paste0(a1, ".BirdNET.selection.table.txt")))
  writeLines(c(cab, linha(1, 12, "Sayaca Tanager", "saytan1", 0.9230, a2)),
             file.path(d, "Campus01", paste0(a2, ".BirdNET.selection.table.txt")))
  pred <- suppressMessages(read_selection_tables(d))
  expect_identical(nrow(pred), 3L)
  expect_identical(pred$selection, 1:3)
  expect_identical(unique(pred$site), "Campus01")
  expect_identical(pred$species_code, c("saytan1", "rucspa1", "saytan1"))
  expect_equal(pred$file_offset, c(0, 8, 12))
  expect_type(pred$confidence, "double")
  m <- suppressMessages(select_clips(pred, n_top = 1))
  expect_setequal(m$recording_hour, c("07", "08"))
  expect_true(all(m$recording_date == "20261003"))
})
