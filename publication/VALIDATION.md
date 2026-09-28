# Synchronization validation

## Completed

- **30 Python tests passed** in a clean Python 3.12 environment. Includes original numerical checks, invalid-input handling, paired-difference equivalence, reproducible 24-scenario simulation, HTTP behavior, input hashes, full publication manifest, and exact matching of Results paragraphs across the proof-of-concept Word document, suggested Word text, and Markdown.
- **Browser regression suite passed**: CSV import, observed/simulated provenance, workload input limits, JSON/SVG export contents, zero-variance handling, escaped identifiers, stale-result protection, simulation controls, and layouts at 1440/768/390 pixels.
- **Publication browser suite passed**: the 5,000-pair button, export checksums, equality with the canonical results endpoint, new results-page navigation, three figures, responsive layout, and no JavaScript page errors.
- Dependency consistency check passed. Exact installed versions are in `environment.lock.txt`.
- Word files reopened successfully with python-docx. Both contain all expected result paragraphs and three embedded figures; the proof of concept also contains the five-row source table. Native Microsoft Word pagination was not visually tested.
- Generated plots were inspected for labeling and interpretation. All reported experiments are explicitly synthetic.

## Current application

The synchronized instance was started at http://127.0.0.1:8769. The original
instance on port 8766 may still contain older backend code. Use port 8769 for
this revision, or restart the server from the updated project.

## Scope and limits

The actual journal manuscript was not changed, as requested. Suggested Results
text and a whole-manuscript change guide are provided for the author to apply.
No journal-specific formatting, reference numbering, or full-manuscript review
was performed because no editable manuscript or journal guidelines were supplied.
These checks establish software/document consistency; they do not establish
clinical effectiveness, external validity, methodological novelty, or journal
acceptance. The statistical simulation deliberately assumes independent normal
paired differences and does not validate robustness to other clinical designs.

## Reproduction

Run `python publication/build.py` with `requirements-publication.txt` installed,
then `python -m unittest discover -s tests -v`. See the project README for the
browser commands. A clean temporary environment was used here to avoid the
previous local `.venv` startup problem; its installed versions are recorded.
