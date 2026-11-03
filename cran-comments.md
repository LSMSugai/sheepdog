## Resubmission

This is a resubmission of sheepdog 3.3.2 (version 3.3.3). In response to
the review by Uwe Ligges:

- https://stan-dev.r-universe.dev was removed from
  Additional_repositories; sheepdog does not need it. Only
  https://diogoprov.r-universe.dev (for crywolf, in Suggests) remains.
- The Description field now cites the methods the package implements, in
  the form Authors (year) <doi:...>: Miller et al. (2011), Chambert et al.
  (2015) and Wood and Kahl (2024).

The package code is unchanged from 3.3.2.

## Test environment

- Local macOS, aarch64-apple-darwin23, R 4.6.1.
- R CMD check --as-cran, with all package vignettes built and rebuilt.
- The same check with crywolf removed from the library
  (`_R_CHECK_FORCE_SUGGESTS_=false`): 1 NOTE (new submission), tests and
  vignettes pass, and the tests needing crywolf are skipped.
- GitHub Actions: macOS, Windows and Linux (R release) and Linux
  (R-devel).

## R CMD check results

0 errors | 0 warnings | 2 notes

- New submission; crywolf (Suggests) is available from the
  Additional_repositories. On win-builder the same NOTE flags
  "Detections" and "detections" in DESCRIPTION as possibly misspelled;
  they are spelled correctly.
- The local HTML Tidy is too old to validate the HTML manual; this NOTE
  is local only.

Tests: 1585 passed; one optional test skipped (Stan integration).

## Optional repositories

crywolf is an optional Suggests dependency outside CRAN, available from
the repository declared in Additional_repositories
(https://diogoprov.r-universe.dev). Tests using optional dependencies are
conditional. Stan fitting is opt-in and is not run by normal CRAN checks.

## Size and benchmark material

The checked source archive is approximately 4.4 MB. The acoustic example
is simulated and contains no audio files. Cached performance tables are
small derived summaries; benchmark fitting and downloads are opt-in
scripts excluded from the source tarball. Vignette builds use the cached
tables and never download the original benchmark data or refit Stan.
Attribution and the source-data licence are recorded in
inst/benchmarks/README.md and the performance vignette.
