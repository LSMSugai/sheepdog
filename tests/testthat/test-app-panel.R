# Painel de audio do app: sitio pelo nome do arquivo, reuso da lista de
# gravacoes, montagem da interface, aplicar pastas, confirmacao das pastas,
# janela de escolha de pasta e validacoes de run_app()

ex_birdnet <- function() {
  system.file("extdata", "example", "birdnet", package = "sheepdog")
}

# Pasta com gravacoes de dois sitios soltas lado a lado
audio_flat <- function(d) {
  dir.create(d, recursive = TRUE, showWarnings = FALSE)
  arquivos <- c("Campinas_Campus01_20261003_074339.flac",
                "Campinas_Campus01_20261003_084339.flac",
                "Campinas_Campus02_20261003_074339.flac")
  file.create(file.path(d, arquivos))
  arquivos
}

test_that("site_from_name() reads the site from the file name", {
  caminhos <- c("/a/b/Campinas_Campus01_20261003_074339.flac",
                "C:\\x\\Campinas_Campus02_20261003_074339.flac")
  expect_identical(site_from_name(caminhos, "^[^_]+_([^_]+)_"),
                   c("Campus01", "Campus02"))
  expect_error(site_from_name(caminhos, "^[^_]+_"), "capture group")
  expect_error(site_from_name(caminhos, "^XYZ_(.+)_"), "do not match")
  expect_error(site_from_name(caminhos, c("a", "b")), "single regular")
})

test_that("list_recordings() takes the site from the file name", {
  d <- file.path(withr::local_tempdir(), "audio")
  audio_flat(d)
  # sem site_pattern, arquivos soltos na pasta sao recusados
  expect_error(suppressMessages(list_recordings(d)), "site_pattern")
  rec <- suppressMessages(list_recordings(d, site_pattern = "^[^_]+_([^_]+)_"))
  expect_identical(sort(unique(rec$site)), c("Campus01", "Campus02"))
  expect_identical(sum(rec$site == "Campus01"), 2L)
  expect_error(list_recordings(d, site = "X", site_pattern = "(.+)"),
               "not both")
})

test_that("read_selection_tables() takes the site from the audio file", {
  cab <- paste("Selection", "View", "Channel", "Begin Time (s)",
               "End Time (s)", "Low Freq (Hz)", "High Freq (Hz)",
               "Common Name", "Species Code", "Confidence", "Begin Path",
               "File Offset (s)", sep = "\t")
  linha <- function(audio) {
    paste(1, "Spectrogram 1", 1, "0.0", "3.0", 0, 15000, "Sayaca Tanager",
          "saytan1", "0.9000", paste0("/Volumes/audio/", audio, ".flac"),
          "0.0", sep = "\t")
  }
  d <- withr::local_tempdir()
  dir.create(file.path(d, "resultados"))
  for (a in c("Campinas_Campus01_20261003_074339",
              "Campinas_Campus02_20261003_074339")) {
    writeLines(c(cab, linha(a)), file.path(
      d, "resultados", paste0(a, ".BirdNET.selection.table.txt")))
  }
  pela_pasta <- suppressMessages(read_selection_tables(d))
  expect_identical(unique(pela_pasta$site), "resultados")
  pelo_nome <- suppressMessages(
    read_selection_tables(d, site_pattern = "^[^_]+_([^_]+)_"))
  expect_identical(pelo_nome$site, c("Campus01", "Campus02"))
})

test_that("recording_summary() filters the counts, not the recordings", {
  det <- tibble::tibble(
    site = "A", species_code = c("x", "x", "y"),
    begin_path = c("/a/A_20261003_070000.wav", "/a/A_20261003_070000.wav",
                   "/a/A_20261004_070000.wav"))
  todas <- recording_summary(NULL, det)
  so_x <- recording_summary(NULL, det, species = "x")
  # o dia so com predicoes de "y" continua no resumo, sem predicoes de "x"
  expect_identical(nrow(so_x), nrow(todas))
  expect_identical(so_x$n_detections, c(2L, 0L))
  expect_identical(todas$n_detections, c(2L, 1L))
  expect_true(attr(so_x, "from_detections"))
})

test_that("locate_audio() can reuse a list of the audio folder", {
  d <- withr::local_tempdir()
  dir.create(file.path(d, "new"))
  listados <- file.path(d, "new", "Campinas", "a_20261002_092817.flac")
  # o arquivo nao existe no disco: so a lista dada pode acha-lo
  chk <- locate_audio(file.path(d, "old", "a_20261002_092817.flac"),
                      file.path(d, "new"), files = listados)
  expect_identical(gsub("\\\\", "/", unname(chk$found)),
                   gsub("\\\\", "/", listados))
  expect_length(locate_audio(file.path(d, "old", "a_20261002_092817.flac"),
                             file.path(d, "new"))$found, 0)
})

test_that("listed_files() reuses the list only for the same folder", {
  d <- withr::local_tempdir()
  outra <- withr::local_tempdir()
  rec <- tibble::tibble(site = "A", source_audio = "/x/a.wav")
  expect_identical(listed_files(d, d, rec), "/x/a.wav")
  expect_identical(listed_files(paste0(d, "/"), d, rec), "/x/a.wav")
  expect_null(listed_files(outra, d, rec))
  expect_null(listed_files(d, d, NULL))
  expect_null(listed_files("", d, rec))
  expect_null(listed_files(file.path(d, "no"), d, rec))
})

test_that("app_ui() builds the tabs from the state", {
  skip_if_not_installed("shiny")
  # sem pastas: as abas de sorteio e exportacao pedem as pastas
  vazio <- as.character(app_ui(app_state()))
  expect_match(vazio, "Intro")
  expect_match(vazio, "Audio panel")
  expect_identical(lengths(regmatches(
    vazio, gregexpr("to use this tab", vazio))), 2L)
  # com as tabelas e a pasta da rodada, as abas completas
  st <- app_state(selection_dir = ex_birdnet(),
                  output_dir = withr::local_tempdir(), reviewer = "bia")
  suppressMessages(load_app_state(st))
  pronto <- as.character(app_ui(st))
  expect_match(pronto, "sheepdog (bia)", fixed = TRUE)
  expect_match(pronto, "sampling-mode", fixed = TRUE)
  expect_match(pronto, "export-export_dir", fixed = TRUE)
  expect_false(grepl("to use this tab", pronto))
  # so revisao: uma pagina, sem abas
  so_rev <- app_state(manifest = data.frame(), clips_dir = tempdir())
  expect_true(so_rev$review_only)
  revisao <- as.character(app_ui(so_rev))
  expect_match(revisao, "clip review", fixed = TRUE)
  expect_false(grepl("Audio panel", revisao))
})

test_that("review_app() wires the modules of a ready state", {
  skip_if_not_installed("shiny")
  st <- app_state(selection_dir = ex_birdnet(),
                  output_dir = withr::local_tempdir())
  suppressMessages(load_app_state(st))
  app <- review_app(st)
  expect_s3_class(app, "shiny.appobj")
  shiny::testServer(app, {
    session$flushReact()
    expect_true(app_ready(st))
  })
})

test_that("the audio panel applies the folders and reloads", {
  skip_if_not_installed("shiny")
  base <- withr::local_tempdir()
  audio <- file.path(base, "audio")
  dir.create(file.path(audio, "ARA"), recursive = TRUE)
  file.create(file.path(audio, "ARA", "ARA01_20211001_190000.wav"))
  saida <- file.path(base, "validacao")
  st <- app_state()
  recargas <- 0
  aplicados <- 0
  raiz <- list(reload = function() recargas <<- recargas + 1)
  shiny::testServer(setup_server, args = list(
    st = st, root = raiz, on_apply = function() aplicados <<- aplicados + 1), {
      session$setInputs(audio_dir = audio, selection_dir = ex_birdnet(),
                        output_dir = saida, site_pattern = "")
      suppressMessages(session$setInputs(apply = 1))
      expect_identical(st$selection_dir, ex_birdnet())
      expect_identical(st$output_dir, saida)
      expect_true(st$confirmed)
      expect_true(file.exists(file.path(saida, "recordings.csv")))
      expect_identical(nrow(st$recordings), 1L)
      expect_identical(recargas, 1)
      expect_identical(aplicados, 1)
      # o quadro "Loaded" e refeito pela recarga da pagina (root$reload())
      expect_false(is.null(st$detections))

      # site_pattern no painel: o sitio vem do nome do arquivo de audio
      session$setInputs(site_pattern = "([A-Z]+)[0-9]+_")
      suppressMessages(session$setInputs(apply = 2))
      expect_identical(st$site_pattern, "([A-Z]+)[0-9]+_")
      expect_setequal(unique(st$detections$site),
                      unique(sub("[0-9]+_.*$", "",
                                 basename(gsub("\\\\", "/",
                                               st$detections$begin_path)))))

      # um padrao sem grupo falha e devolve o estado anterior
      session$setInputs(site_pattern = "^[A-Z]+")
      session$setInputs(apply = 3)
      expect_identical(st$site_pattern, "([A-Z]+)[0-9]+_")
      expect_identical(recargas, 2)

      # campo vazio: volta ao sitio pela pasta
      session$setInputs(site_pattern = "")
      suppressMessages(session$setInputs(apply = 4))
      expect_null(st$site_pattern)
      expect_identical(recargas, 3)
    })
})

test_that("confirm_folders() keeps or changes the folders", {
  skip_if_not_installed("shiny")
  servidor <- function(st) {
    function(input, output, session) confirm_folders(st, input, session)
  }
  st <- app_state(selection_dir = "/x/birdnet")
  expect_false(st$confirmed)
  shiny::testServer(servidor(st), {
    session$setInputs(folders_keep = 1)
    expect_true(st$confirmed)
  })
  st2 <- app_state(output_dir = "/x/validacao")
  shiny::testServer(servidor(st2), {
    session$setInputs(folders_change = 1)
    expect_true(st2$confirmed)
  })
  # sem pastas dadas, nada a perguntar
  st3 <- app_state()
  expect_true(st3$confirmed)
  shiny::testServer(servidor(st3), expect_true(st3$confirmed))
})

test_that("choose_dir() uses the dialog of each system", {
  inicio <- NULL
  local_mocked_bindings(
    dir_dialog_rstudio_available = function() FALSE,
    dir_dialog_tcltk_available = function() TRUE,
    dir_dialog_windows = function(i, c) { inicio <<- i; "C:/audio/" },
    dir_dialog_macos = function(i, c) "/Users/bia/audio/",
    dir_dialog_tcltk = function(i, c) "/home/bia/audio")
  local_mocked_bindings(dir_dialog_os = function() "Windows")
  expect_identical(choose_dir("/no/such/folder"), "C:/audio")
  expect_identical(inicio, path.expand("~"))
  d <- withr::local_tempdir()
  choose_dir(d)
  expect_identical(inicio, d)
  local_mocked_bindings(dir_dialog_os = function() "Darwin")
  expect_identical(choose_dir(), "/Users/bia/audio")
  local_mocked_bindings(dir_dialog_os = function() "Linux")
  expect_identical(choose_dir(), "/home/bia/audio")
  local_mocked_bindings(dir_dialog_tcltk_available = function() FALSE)
  expect_null(choose_dir())
  local_mocked_bindings(dir_dialog_os = function() "SunOS")
  expect_null(choose_dir())
  # no RStudio, a janela dele vale em qualquer sistema
  local_mocked_bindings(dir_dialog_rstudio_available = function() TRUE,
                        dir_dialog_rstudio = function(c, i) "/r/audio")
  expect_identical(choose_dir(), "/r/audio")
  # nada escolhido
  local_mocked_bindings(dir_dialog_rstudio = function(c, i) NULL)
  expect_null(choose_dir())
  local_mocked_bindings(dir_dialog_rstudio = function(c, i) NA_character_)
  expect_null(choose_dir())
  local_mocked_bindings(dir_dialog_rstudio = function(c, i) "")
  expect_null(choose_dir())
})

test_that("run_app() checks its arguments before starting", {
  skip_if_not_installed("shiny")
  skip_if_not_installed("av")
  expect_error(run_app(manifest = "m.csv"), "clips_dir")
  expect_error(run_app(manifest = data.frame(), clips_dir = tempdir()),
               "verdicts_file")
  saida <- withr::local_tempdir()
  local_mocked_bindings(runApp = function(appDir, ...) appDir,
                        .package = "shiny")
  app <- suppressMessages(run_app(selection_dir = ex_birdnet(),
                                  output_dir = saida,
                                  site_pattern = "([A-Z]+)[0-9]+_",
                                  launch.browser = FALSE))
  expect_s3_class(app, "shiny.appobj")
})
