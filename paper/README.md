# paper/

Prose for the report. This directory and `figures/` are what Overleaf shows;
everything else in the repo is the pipeline that produces them.

**Figures are never defined here.** They are built from `raw/` by `../run.sh`
and written to `../figures/`, which `\graphicspath` points at. To change a
figure, edit its script in `build/` and re-run. Pasting plot data into a `.tex`
file creates a second copy of the numbers that will silently go stale.

## Working in Overleaf

Overleaf syncs the whole repository, so the census scans and build scripts are
visible there too. Only `main.tex` and `figures/` matter for compiling.

Pull from GitHub before starting a writing session, and push when finished, so
figure rebuilds and prose edits do not diverge.
