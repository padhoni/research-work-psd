# EPIC Research Lab

A local research prototype based on **Proof of Concept.docx**. Includes paired documentation-time and NASA-TLX analyses, a reproducible CDS override simulation, and research exports. Independent of Epic Systems; no live EHR integration or clinical recommendations.

## Run

Requires Python 3.12 or newer. From this directory:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python server.py
```

Open http://127.0.0.1:8765. Stop with Ctrl+C. Use `--port 8766` if necessary. After dependency installation, the application runs offline with no CDN or external asset requests.

## Workflow

1. Review the five simulated clinician pairs from the document.
2. Import a CSV or edit the data directly. Headers must be exactly `clinician_id,pre,post`. Example files are in `examples/`; **both are simulated**.
3. Choose documentation minutes or workload points and explicitly declare simulated or observed provenance. Use one complete paired row per clinician.
4. Run analysis. Download the research JSON bundle (input data, statistics, limitations, manuscript paragraph, SVG figure, and provenance) or the standalone SVG figure.
5. The CDS simulation tab provides adjustable seed, group sizes, and override probabilities, with a separate JSON export.

Results are not saved automatically. Export before closing or reloading. The manuscript paragraph is also displayed for copying. JSON exports can be opened in a text editor or loaded with Python's `json` module.

## Scientific interpretation

The document's example yields means 5.11 and 4.16 minutes, a mean difference of 0.95 minutes, a relative reduction of 18.59%, and t(4) ≈ 42.485. The app uses SciPy's two-sided paired t-test and 95% CI, and reports Cohen's dz. Positive differences indicate lower post values. Negative reductions indicate an increase. Missing, duplicate, invalid, and nonfinite rows are rejected. Zero variance returns undefined inference rather than a misleading significance result.

Before/after comparisons do **not** establish causation. A simulated p-value is not evidence of intervention efficacy. This prototype does not measure patient engagement or burnout. The document's 461.3 workload baseline is not a standard 0–100 NASA-TLX score; workload imports must use a documented, consistent 0–100 scoring method. The app analyzes scores, not questionnaire responses.

For actual research, prespecify windows, active-time definitions, idle thresholds, eligibility criteria, clinician aggregation, and confounder handling. Raw Epic audit events need a separate validated transformation into active documentation minutes. This app does not perform that transformation or implement SMART on FHIR, an ambient AI scribe, or CDS Hooks. Clustered alerts or encounters need study-specific statistical models beyond this proof of concept.

CDS uses NumPy `default_rng` with independent binomial counts and Wilson 95% intervals. It retains the document's default probabilities but does not reproduce its older random sequence. Lower override rates alone do not demonstrate safer care. See the in-app Methods page for sources and assumptions.

## Data handling

The server binds only to 127.0.0.1 and processes data in memory. It has no database, request logging, analytics, or automatic persistence. Use de-identified, pseudonymous data. Browser downloads contain your input rows. This is a local prototype, with no authentication or institutional hosting controls.

## Validation

```sh
.venv/bin/python -m unittest discover -s tests -v
```

Implementation: `analysis.py` (statistics), `server.py` (local HTTP API), `static/` (browser interface). Dependencies are pinned in `requirements.txt`.

Sources: [SciPy paired t-test](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_rel.html), [NASA TLX manual](https://humansystems.arc.nasa.gov/groups/TLX/downloads/TLX_pappen_manual.pdf), [AHRQ NASA-TLX overview](https://digital.ahrq.gov/health-it-tools-and-resources/evaluation-resources/workflow-assessment-health-it-toolkit/all-workflow-tools/nasa-task-load-index).

## Manuscript screenshot results

`paper_results.py` creates a separate descriptive report from `results/paper/source_data.json`. It produces PNG/PDF/SVG figures, `summary.json`, and `static/paper.html` (served at `/paper` after restarting the server). The original simulation remains separate.

Run with a Python environment containing Matplotlib:

```sh
MPLCONFIGDIR=/tmp/epic-matplotlib python3 paper_results.py --workflow-mapping paragraph
```

The manuscript paragraph and figure disagree about order-entry versus chart-review labels. `--workflow-mapping chart` reproduces the chart mapping instead. Both are marked provisional pending source confirmation. Total workflow reduction is 64%; documentation reduction is 71.875%. Source limitations and suggested wording are in `results/paper/MANUSCRIPT_REVIEW.md`. Aggregate task means are not treated as clinician pairs for significance testing.
