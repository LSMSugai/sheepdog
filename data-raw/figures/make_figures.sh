#!/usr/bin/env bash
# Build the sheepdog pipeline figures (HTML + PNG) and copy Figure 1 to man/figures.
# Needs: python3, node, and Playwright with Chromium (npm install playwright && npx playwright install chromium).
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -d fontpkg/node_modules/@fontsource ]; then
  mkdir -p fontpkg && (cd fontpkg && npm init -y >/dev/null && npm install @fontsource/figtree@5 @fontsource/ibm-plex-mono@5 >/dev/null)
fi
python3 gen_v15.py >/dev/null     # draws every panel (gen_panels.py -> gen_v2 ... gen_v15) into panels.json
python3 build_abstracts.py        # writes abstracts/*.html
python3 build_retrain.py >/dev/null # writes abstracts/1x_stage1_retraining.html
python3 build_routes_article.py     # writes abstracts/routes_article.html
node render.js                    # writes abstracts/*.png
cp abstracts/1_stage1_validation.png ../../man/figures/stage1_validation.png
cp abstracts/1y_stage1_diagnostic.png ../../man/figures/stage1_diagnostic.png
cp abstracts/2_stage2_calibration.png ../../man/figures/stage2_calibration.png
cp abstracts/1x_stage1_retraining.png ../../man/figures/stage1_retraining.png
cp abstracts/3_stage3_community.png ../../man/figures/stage3_community.png
mkdir -p ../../vignettes/articles/figures
cp abstracts/routes_article.png ../../vignettes/articles/figures/routes.png
echo "Figures 1 to 5 copied to man/figures/, the routes figure to vignettes/articles/figures/"
