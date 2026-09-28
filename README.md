# EPIC Research Lab — simulation-based proof of concept

A local research prototype for paired documentation-time analysis and synthetic
CDS override counts. It does not connect to Epic, implement an ambient scribe,
or evaluate clinical effectiveness. No measured burnout, workload, diagnostic
accuracy, medication safety, or patient engagement outcomes are reported.

## Author deliverables

- **Proof of Concept.docx**: revised methods, limitations, results, figures, and sources.
- **publication/Suggested_Results.docx** and **.md**: suggested replacement paper text. The journal manuscript has not been edited.
- **publication/Manuscript_Change_Guide.md**: changes to apply elsewhere in the paper.
- **publication/results.json**: machine-readable source of all canonical results.
- **publication/figures/**: PNG (300 dpi), PDF, and SVG figures.
- **publication/monte_carlo.csv**: all 24 numerical-simulation scenarios and Monte Carlo uncertainty.
- **archive/pre_sync/**: preserved original Word document and earlier figure-generation code.

Earlier files under `results/` are historical outputs. In particular,
`results/paper/` contains the unverified manuscript screenshot transcription and
is **not** the current publication result set. The current canonical outputs are
under `publication/`.

## Install, rebuild, and run

Python 3.12 on macOS was used for this package. Use a fresh environment if the
older `.venv` has filesystem/startup problems:

```sh
python3 -m venv .venv-research
.venv-research/bin/pip install -r requirements-publication.txt
MPLCONFIGDIR=/tmp/epic-matplotlib .venv-research/bin/python publication/build.py
.venv-research/bin/python server.py --port 8766
```

Open http://127.0.0.1:8766. Choose a free port if another app instance is running.
The app has a five-pair demo and a **Load 5,000 synthetic pairs** button. The
**Simulation results** link opens `/paper`, generated from the same calculations
as the Word document and suggested Results text. All assets are local.

`publication/build.py` recalculates results, regenerates figures, rewrites
`Proof of Concept.docx`, regenerates the suggested text, and creates a SHA-256
manifest. It does not open or modify a journal manuscript. The original Word
file is backed up once; edit the generator if you want edits retained on rebuild.
`paper_results.py` is a compatibility entry point to this same build.

## Analysis definitions

1. **Original example**: five fixed synthetic pairs, with means 5.11 and 4.16
   minutes and an 18.59% relative reduction. CSV: `examples/documentation_original.csv`.
2. **Expanded example**: 5,000 synthetic rows, preserving the first five and
   generating the other 4,995. CSV: `examples/documentation.csv`; model and seed
   are in `examples/documentation.metadata.json`. This is a demonstration dataset,
   not 5,000 recruited clinicians and not 5,000 Monte Carlo repetitions.
3. **CDS simulation**: 10,000 hypothetical alerts per group, assumed override
   probabilities 0.89 and 0.34, NumPy default_rng seed 42, direct binomial totals,
   Wilson 95% intervals. No six-month deployment or predictive accuracy is modeled.
4. **Repeated numerical evaluation**: 24 normal-difference scenarios; n in
   {5,50,332}, true differences in {−0.50,0,0.50,0.95}, SD in {0.65,1.30}, 1,000
   repetitions each, seed 20260927. Reports bias, coverage, rejection, and Monte
   Carlo SE. This assesses the t procedure under its assumptions, not clinical AI.

The paired analysis uses pre minus post, a two-sided paired t-test, 95% Student t
CI, and Cohen's dz. Missing, duplicate, negative, or nonfinite rows are rejected.
Zero variance yields undefined inference. P-values that underflow numerically
are labeled accordingly, never interpreted as exactly zero. Data processing is
in memory. Use de-identified data for any optional observed-data CSV import.

The workload CSV option accepts documented 0–100 NASA-TLX aggregate scores, but
no workload outcome is part of the canonical simulation study. The original
461.3→25 workload model was withdrawn, not silently rescaled.

## Verify

After rebuilding, run:

```sh
.venv-research/bin/python -m unittest discover -s tests -v
.venv-research/bin/pip check
```

API tests briefly bind an ephemeral localhost port. Word-content verification
uses python-docx from `requirements-publication.txt`. Browser tests require
Playwright and Chrome:

```sh
npm install --prefix /tmp/epic-browser playwright
APP_URL=http://127.0.0.1:8766 NODE_PATH=/tmp/epic-browser/node_modules node tests/browser.cjs
APP_URL=http://127.0.0.1:8766 NODE_PATH=/tmp/epic-browser/node_modules node tests/large_dataset.cjs
APP_URL=http://127.0.0.1:8766 NODE_PATH=/tmp/epic-browser/node_modules node tests/publication.cjs
```

The macOS Chrome executable is the browser-test default. Test outcomes and any
remaining limitations are recorded in `publication/VALIDATION.md`.

## Submission scope

These artifacts support an author-reviewed simulation/prototype manuscript.
They do not by themselves establish journal suitability, methodological novelty,
or clinical validity. Apply the suggested changes consistently to the abstract,
Methods, Results, Discussion, Conclusion, and figure captions. Keep cited clinical
studies distinct from this project's synthetic experiments.
