# Figures of the reference index

The stage figures of the pkgdown site, based on the figures drawn by Larissa S. M. Sugai. Run each script from the repository root.

- `schematic_*.R`: small drawings, one idea each, from the icons in `schematic_icons.R`.
- `diagram_stage*.R`: Graphviz diagrams, used where there is a decision to follow, with the style in `diagram_style.R`.
- `plot_routes.R`: ggplot2 figures on simulated data, for the reference index and `vignettes/articles/choosing-a-route.Rmd`.

The PNGs go to `pkgdown/assets/figures/` (and `vignettes/articles/figures/`), outside the built package, because only the site uses them.
