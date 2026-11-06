# Pipeline figures

Scripts that draw the sheepdog pipeline figures. Five figures are used on the reference index (`_pkgdown.yml`), from `man/figures/`:
Figure 1 (Stage 1 · Validation, `stage1_validation.png`), Figure 2 (Stage 1 · Diagnostic,
`stage1_diagnostic.png`), Figure 3 (Stage 1 · Retraining, `stage1_retraining.png`),
Figure 4 (Stage 2 · Calibration, `stage2_calibration.png`) and Figure 5 (Stage 3 · Community
matrices, `stage3_community.png`).

```sh
data-raw/figures/make_figures.sh
```

- `gen_panels.py` draws the base SVG panels; `gen_v2.py` … `gen_v15.py` each import the previous
  file and redraw some panels (run `gen_v15.py` and the whole chain runs). Output: `panels.json`.
- `build_abstracts.py` puts the panels into one HTML page per figure (`abstracts/`), with
  `base.css` and the Figtree and IBM Plex Mono fonts embedded.
- `build_retrain.py` writes the retraining figure (Figure 3) from the same panels and styles.
- `build_routes_article.py` writes the routes figure of `vignettes/articles/choosing-a-route.Rmd`
  (`vignettes/articles/figures/routes.png`), from `routes_data.py` and `routes_graphics.py`.
- `render.js` saves each page as a PNG at 2x with Playwright.

Figures: `0_sheepdog_pipeline` (overview), `1_stage1_validation` (Figure 1),
`1y_stage1_diagnostic` (Figure 2), `1x_stage1_retraining` (Figure 3), `2_stage2_calibration` (Figure 4), `3_stage3_community` (Figure 5). Values in the drawings are illustrative.
