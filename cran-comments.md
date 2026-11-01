## Submission candidate

Prepared for an initial CRAN submission of sheepdog 3.3.2, which
replaces the 3.3.1, 3.3.0 and 3.2.1 candidates (never uploaded).
This file does not imply that a submission has already been uploaded.

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

crywolf is an optional Suggests dependency outside CRAN. Its repository
and the repository supplying cmdstanr (a dependency of crywolf, not of
sheepdog) are declared in Additional_repositories:
https://diogoprov.r-universe.dev and https://stan-dev.r-universe.dev.
Tests using optional dependencies are conditional. Stan fitting is opt-in
and is not run by normal CRAN checks.

## Size and benchmark material

The checked source archive is approximately 4.4 MB. The acoustic example
is simulated and contains no audio files. Cached performance tables are
small derived summaries; benchmark fitting and downloads are opt-in
scripts excluded from the source tarball. Vignette builds use the cached
tables and never download the original benchmark data or refit Stan.
Attribution and the source-data licence are recorded in
inst/benchmarks/README.md and the performance vignette.
