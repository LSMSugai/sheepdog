#' Review the clips in a local app
#'
#' Opens a 'shiny' app, in the browser, to review the clips of a manifest
#' one at a time: the spectrogram and a player for each clip, its site,
#' night, hour, score and design, and buttons to mark it positive, negative
#' or uncertain. Each verdict is written at once to `verdicts_file`, so an
#' interrupted session loses nothing and can be resumed. The app replaces
#' moving the clips into `Positive` and `Negative` folders in the BirdNET
#' GUI; [app_verdicts()] turns `verdicts_file` into the table that
#' [classify_review()] returns.
#'
#' The app runs on the reviewer's computer and reads the clips from disk;
#' nothing is uploaded.
#'
#' @section Keyboard:
#' `p` positive, `n` negative, `u` uncertain, right arrow or space next
#' clip, left arrow previous clip.
#'
#' @section Verdicts file:
#' A CSV with one line per click: `clip_file`, `species_folder`,
#' `reviewer`, `verdict` (`"positive"`, `"negative"` or `"uncertain"`) and
#' `time`. Lines are only appended; when a clip is marked again, the last
#' verdict of the reviewer counts. Several reviewers can share one file or
#' keep one each.
#'
#' @param manifest Clip manifest: a data frame or the path to
#'   `clip_manifest.csv` (from [select_clips()], [cut_clips()] or
#'   [assign_reviewers()]).
#' @param clips_dir Folder of the cut clips, with one subfolder per
#'   species (`<clips_dir>/<species_folder>/<clip_file>`, as written by
#'   [cut_clips()]).
#' @param verdicts_file CSV where the verdicts are written. By default,
#'   `verdicts.csv` next to `manifest` when it is a path.
#' @param reviewer Name of the reviewer, written with each verdict. With a
#'   manifest from [assign_reviewers()], only the clips assigned to this
#'   reviewer (as first or second reviewer) are shown.
#' @param max_freq Optional upper limit of the spectrogram, in kHz (e.g.
#'   `8` for most anuran calls). The whole band by default.
#' @param launch.browser Open the app in the browser? Passed to
#'   [shiny::runApp()].
#' @param ... Further arguments to [shiny::runApp()], e.g. `port`.
#'
#' @return Called for its side effect; returns when the app is closed.
#' @seealso [app_verdicts()], `vignette("review-app")`.
#' @export
#' @examples
#' \dontrun{
#' run_app("validation/clip_manifest.csv", "validation/clips",
#'         reviewer = "liliana")
#' }
run_app <- function(manifest, clips_dir, verdicts_file = NULL,
                    reviewer = NULL, max_freq = NULL,
                    launch.browser = interactive(), ...) {
  require_suggested("shiny", "to run the review app")
  require_suggested("av", "to draw the spectrograms")
  if (is.null(verdicts_file)) {
    if (!is.character(manifest)) {
      stop("Give `verdicts_file` when `manifest` is a data frame.",
           call. = FALSE)
    }
    verdicts_file <- file.path(dirname(manifest), "verdicts.csv")
  }
  fila <- review_queue(manifest, clips_dir, reviewer)
  message(nrow(fila), " clip(s) to review; verdicts written to ",
          verdicts_file, ".")
  shiny::runApp(review_app(fila, clips_dir, verdicts_file, reviewer,
                           max_freq),
                launch.browser = launch.browser, ...)
}

#' Verdicts of the review app
#'
#' Joins the verdicts written by [run_app()] to the clip manifest, giving
#' the same table as [classify_review()] (the content of
#' `validation_by_clip.csv`), so that the summaries of stage 1, the
#' agreement between reviewers and the calibration work as with a review
#' in the BirdNET GUI. `"uncertain"` verdicts are kept but, like
#' `"disagreement"`, left out of precision, thresholds and calibration,
#' which use only positive and negative verdicts.
#'
#' @inheritParams run_app
#' @param verdicts_file CSV written by [run_app()].
#' @param clips_dir Optional folder of the clips, to fill `reviewed_path`
#'   (needed by [build_training_set()]).
#' @param reviewer Optional reviewer: only their verdicts are used. With
#'   `NULL`, every reviewer's verdicts are kept, one row per clip and
#'   reviewer, ready for [reviewer_agreement()] and
#'   [consensus_verdicts()].
#'
#' @return The manifest with `verdict` (`"positive"`, `"negative"`,
#'   `"uncertain"` or `"not_reviewed"`), `reviewed_path` and `reviewer`.
#'   With `reviewer = NULL`, a clip reviewed by two reviewers has two
#'   rows, and a clip not yet reviewed has one row with `reviewer = NA`.
#' @seealso [run_app()], [classify_review()].
#' @export
app_verdicts <- function(manifest, verdicts_file, clips_dir = NULL,
                         reviewer = NULL) {
  manifesto <- read_manifest(manifest)
  log <- read_verdict_log(verdicts_file)
  if (!is.null(reviewer)) log <- log[log$reviewer %in% reviewer, ]
  fora <- setdiff(log$clip_file, manifesto$clip_file)
  if (length(fora) > 0) {
    warning(length(fora), " clip(s) of `verdicts_file` are not in the ",
            "manifest and were left out.", call. = FALSE)
  }
  log <- select(log, clip_file, species_folder, reviewer, verdict)
  chave <- intersect(c("clip_file", "species_folder"), names(manifesto))
  base <- select(manifesto, -any_of(c("verdict", "reviewed_path",
                                      "reviewer", "second_reviewer")))
  out <- left_join(base, log[c(chave, "reviewer", "verdict")], by = chave,
                   relationship = "one-to-many") |>
    mutate(verdict = replace_na(verdict, "not_reviewed"),
           reviewed_path = if (is.null(clips_dir)) NA_character_ else
             file.path(clips_dir, species_folder, clip_file))
  if (!is.null(reviewer)) out$reviewer <- reviewer
  contagem <- count(out, verdict)
  message("Clips in the manifest: ", nrow(manifesto), "\n",
          paste0("  ", contagem$verdict, ": ", contagem$n, collapse = "\n"))
  out
}

# Clipes da fila do app: os do revisor (com assign_reviewers()) e o
# caminho de cada um
review_queue <- function(manifest, clips_dir, reviewer = NULL) {
  fila <- read_manifest(manifest)
  faltam <- setdiff(c("clip_file", "species_folder"), names(fila))
  if (length(faltam) > 0) {
    stop("`manifest` lacks the column(s): ", paste(faltam, collapse = ", "),
         call. = FALSE)
  }
  if (!is.null(reviewer) && "reviewer" %in% names(fila)) {
    segundo <- if ("second_reviewer" %in% names(fila)) {
      fila$second_reviewer %in% reviewer
    } else {
      FALSE
    }
    fila <- fila[fila$reviewer %in% reviewer | segundo, ]
    if (nrow(fila) == 0) {
      stop("No clip of the manifest is assigned to reviewer `", reviewer,
           "`.", call. = FALSE)
    }
  }
  for (col in c("site", "night", "recording_hour", "confidence",
                "sampling_mode", "species_code")) {
    if (!col %in% names(fila)) fila[[col]] <- NA
  }
  fila$path <- file.path(clips_dir, fila$species_folder, fila$clip_file)
  ausentes <- sum(!file.exists(fila$path))
  if (ausentes == nrow(fila)) {
    stop("None of the clips was found in `clips_dir` (",
         clips_dir, "/<species_folder>/<clip_file>).", call. = FALSE)
  }
  if (ausentes > 0) {
    warning(ausentes, " clip(s) not found in `clips_dir`; they are shown ",
            "without audio.", call. = FALSE)
  }
  fila
}

verdict_columns <- c("clip_file", "species_folder", "reviewer", "verdict",
                     "time")

# Acrescenta um veredito ao arquivo (cria com cabecalho se nao existe)
append_verdict <- function(file, clip_file, species_folder, reviewer,
                           verdict) {
  linha <- tibble(clip_file = clip_file, species_folder = species_folder,
                  reviewer = if (is.null(reviewer)) NA_character_ else
                    reviewer,
                  verdict = verdict,
                  time = format(Sys.time(), "%Y-%m-%dT%H:%M:%S%z"))
  novo <- !file.exists(file)
  if (novo) dir.create(dirname(file), recursive = TRUE, showWarnings = FALSE)
  write_csv(linha, file, append = !novo, col_names = novo, na = "")
  invisible(linha)
}

# Ultimo veredito de cada clipe e revisor
read_verdict_log <- function(file) {
  vazio <- tibble(clip_file = character(), species_folder = character(),
                  reviewer = character(), verdict = character(),
                  time = character())
  if (!file.exists(file)) return(vazio)
  log <- read_csv(file, na = "", show_col_types = FALSE,
                  col_types = readr::cols(.default = readr::col_character()))
  faltam <- setdiff(verdict_columns, names(log))
  if (length(faltam) > 0) {
    stop("`verdicts_file` lacks the column(s): ",
         paste(faltam, collapse = ", "), call. = FALSE)
  }
  invalidos <- setdiff(log$verdict, c("positive", "negative", "uncertain"))
  if (length(invalidos) > 0) {
    stop("Unknown verdict(s) in `verdicts_file`: ",
         paste(invalidos, collapse = ", "), call. = FALSE)
  }
  # a ordem das linhas e a ordem dos cliques: vale a ultima
  log$.ordem <- seq_len(nrow(log))
  log |>
    arrange(desc(.ordem)) |>
    distinct(clip_file, species_folder, reviewer, .keep_all = TRUE) |>
    arrange(.ordem) |>
    select(-.ordem)
}

# Espectrograma de um clipe (av), com margens pequenas para caber no app.
# O av devolve valores menores onde o som e mais forte, entao a escala de
# cinza vai do preto (forte) ao branco (silencio)
plot_spectrogram <- function(path, max_freq = NULL) {
  x <- av::read_audio_fft(path)
  freq <- attr(x, "frequency") / 1000
  manter <- if (is.null(max_freq)) TRUE else freq <= max_freq
  z <- t(x[manter, , drop = FALSE])
  # contraste: a metade mais silenciosa dos pixels fica branca
  teto <- stats::quantile(z, 0.5, names = FALSE)
  op <- graphics::par(mar = c(4, 4, 0.5, 0.5))
  on.exit(graphics::par(op))
  graphics::image(attr(x, "time"), freq[manter], pmin(z, teto),
                  col = grDevices::gray.colors(64, start = 0, end = 1),
                  xlab = "Time (s)", ylab = "Frequency (kHz)",
                  useRaster = TRUE)
}

# Teclas do app
review_keys <- c(p = "positive", n = "negative", u = "uncertain")

# O app: interface e servidor
review_app <- function(fila, clips_dir, verdicts_file, reviewer,
                       max_freq = NULL) {
  recurso <- "sheepdog_clips"
  shiny::addResourcePath(recurso, normalizePath(clips_dir))
  shiny::shinyApp(
    ui = review_ui("review", fila, reviewer),
    server = function(input, output, session) {
      review_server("review", fila, verdicts_file, reviewer, recurso,
                    max_freq)
    })
}

review_ui <- function(id, fila, reviewer) {
  ns <- shiny::NS(id)
  especies <- sort(unique(fila$species_folder))
  teclas <- sprintf(
    "document.addEventListener('keydown', function(e) {
       if (['INPUT', 'SELECT', 'TEXTAREA'].includes(e.target.tagName)) return;
       Shiny.setInputValue('%s', e.key, {priority: 'event'});
     });", ns("key"))
  shiny::fluidPage(
    title = "sheepdog review",
    shiny::tags$head(shiny::tags$script(shiny::HTML(teclas)),
                     shiny::tags$style(shiny::HTML(
                       paste("td { white-space: nowrap; }",
                             "td + td { white-space: normal;",
                             "word-break: break-all; }")))),
    shiny::titlePanel(paste0("sheepdog: clip review",
                             if (!is.null(reviewer)) paste0(" (", reviewer,
                                                            ")"))),
    shiny::sidebarLayout(
      shiny::sidebarPanel(
        width = 3,
        shiny::selectInput(ns("species"), "Species",
                           c("All" = "", especies)),
        shiny::checkboxInput(ns("pending"), "Only clips not yet reviewed",
                             value = TRUE),
        shiny::textOutput(ns("progress")),
        shiny::hr(),
        shiny::tableOutput(ns("info")),
        shiny::helpText("Keys: p positive, n negative, u uncertain,",
                        "right arrow or space next, left arrow previous.")
      ),
      shiny::mainPanel(
        width = 9,
        shiny::plotOutput(ns("spectrogram"), height = "320px"),
        shiny::uiOutput(ns("player")),
        shiny::br(),
        shiny::actionButton(ns("positive"), "Positive (p)",
                            class = "btn-success"),
        shiny::actionButton(ns("negative"), "Negative (n)",
                            class = "btn-danger"),
        shiny::actionButton(ns("uncertain"), "Uncertain (u)",
                            class = "btn-warning"),
        shiny::actionButton(ns("previous"), "< Previous"),
        shiny::actionButton(ns("next_clip"), "Next >"),
        shiny::br(), shiny::br(),
        shiny::textOutput(ns("current_verdict"))
      )
    )
  )
}

review_server <- function(id, fila, verdicts_file, reviewer, recurso = "",
                          max_freq = NULL) {
  shiny::moduleServer(id, function(input, output, session) {
    chave <- paste(fila$species_folder, fila$clip_file, sep = "/")
    lidos <- function() {
      log <- read_verdict_log(verdicts_file)
      rev <- if (is.null(reviewer)) NA_character_ else reviewer
      log <- log[log$reviewer %in% rev, ]
      stats::setNames(log$verdict,
                      paste(log$species_folder, log$clip_file, sep = "/"))
    }
    vereditos <- shiny::reactiveVal(lidos())
    atual <- shiny::reactiveVal(NA_integer_)

    # clipes visiveis com os filtros; o clipe atual continua visivel ate
    # o revisor sair dele
    visiveis <- shiny::reactive({
      ok <- rep(TRUE, nrow(fila))
      if (!is.null(input$species) && nzchar(input$species)) {
        ok <- ok & fila$species_folder == input$species
      }
      if (isTRUE(input$pending)) {
        ok <- ok & !chave %in% names(shiny::isolate(vereditos()))
      }
      which(ok)
    })
    shiny::observeEvent(list(input$species, input$pending), {
      v <- visiveis()
      atual(if (length(v) > 0) v[1] else NA_integer_)
    })

    proximo <- function(passo) {
      v <- visiveis()
      i <- atual()
      if (is.na(i)) {
        atual(if (length(v) > 0) v[1] else NA_integer_)
        return(invisible())
      }
      depois <- if (passo > 0) v[v > i] else rev(v[v < i])
      if (length(depois) > 0) atual(depois[1])
    }
    marcar <- function(veredito) {
      i <- atual()
      if (is.na(i)) return(invisible())
      append_verdict(verdicts_file, fila$clip_file[i],
                     fila$species_folder[i], reviewer, veredito)
      vv <- vereditos()
      vv[chave[i]] <- veredito
      vereditos(vv)
      proximo(1)
    }
    shiny::observeEvent(input$positive, marcar("positive"))
    shiny::observeEvent(input$negative, marcar("negative"))
    shiny::observeEvent(input$uncertain, marcar("uncertain"))
    shiny::observeEvent(input$next_clip, proximo(1))
    shiny::observeEvent(input$previous, proximo(-1))
    shiny::observeEvent(input$key, {
      k <- tolower(input$key)
      if (k %in% names(review_keys)) {
        marcar(review_keys[[k]])
      } else if (k %in% c("arrowright", " ")) {
        proximo(1)
      } else if (k == "arrowleft") {
        proximo(-1)
      }
    })

    output$progress <- shiny::renderText({
      feitos <- sum(chave %in% names(vereditos()))
      paste0(feitos, " of ", nrow(fila), " clips reviewed")
    })
    output$info <- shiny::renderTable({
      i <- atual()
      shiny::req(!is.na(i))
      tibble(field = c("Clip", "Species", "Site", "Night", "Hour",
                       "Score", "Design"),
             value = c(fila$clip_file[i], fila$species_folder[i],
                       as.character(fila$site[i]),
                       as.character(fila$night[i]),
                       as.character(fila$recording_hour[i]),
                       format(fila$confidence[i], digits = 3),
                       as.character(fila$sampling_mode[i])))
    }, colnames = FALSE)
    output$current_verdict <- shiny::renderText({
      i <- atual()
      if (is.na(i)) return("No clip left with these filters.")
      v <- vereditos()[chave[i]]
      if (is.na(v)) "Not reviewed yet." else paste("Current verdict:", v)
    })
    output$spectrogram <- shiny::renderPlot({
      i <- atual()
      shiny::req(!is.na(i), file.exists(fila$path[i]))
      plot_spectrogram(fila$path[i], max_freq)
    })
    output$player <- shiny::renderUI({
      i <- atual()
      shiny::req(!is.na(i), file.exists(fila$path[i]))
      src <- paste(recurso, utils::URLencode(fila$species_folder[i],
                                             reserved = TRUE),
                   utils::URLencode(fila$clip_file[i], reserved = TRUE),
                   sep = "/")
      shiny::tags$audio(src = src, type = "audio/wav", controls = NA,
                        autoplay = NA, style = "width: 100%;")
    })
    invisible(list(current = atual, verdicts = vereditos))
  })
}
