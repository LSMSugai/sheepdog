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
