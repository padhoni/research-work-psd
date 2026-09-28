# Test results — 27 September 2026

Validated locally on macOS with Python 3.12 and headless Google Chrome.

## Results

- **21 Python tests passed**: reference calculations, invalid/missing/duplicate pairs, NASA-TLX boundaries, zero variance, increasing outcomes, extreme values, small nonconstant differences, CSV quoting/BOM, row limits, simulation reproducibility, integer validation, HTTP routes, malformed JSON, payload limits, and cross-origin rejection.
- **Browser suite passed**: demo calculations; actual JSON and SVG download contents; CSV upload; observed provenance; workload analysis; stale export prevention; edits during an in-flight request; validation messages; escaped clinician IDs; simulation boundary probabilities and reproducibility; navigation; and layouts at 1440, 768, and 390 pixels wide.
- No JavaScript page errors occurred in the browser suite. No horizontal overflow occurred at the tested widths.
- Dependency consistency check passed (`pip check`).

## Fixes from testing

1. Reject numeric overflow with a clear validation error rather than producing non-JSON numbers.
2. Avoid classifying small, nonconstant paired differences as zero variance solely because of their absolute magnitude.
3. Report underflowed p-values as “below numerical precision” in manuscript text, rather than exactly zero. The raw numeric field remains zero as returned by SciPy.
4. Reject fractional or Boolean simulation seeds/counts instead of silently truncating or accepting them.
5. Validate that API request bodies are JSON objects.

## Repeat

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/pip check
```

HTTP tests briefly bind an ephemeral localhost port.

For browser tests, install Playwright in a temporary directory and start the app:

```sh
npm install --prefix /tmp/epic-browser playwright
.venv/bin/python server.py --port 8766
```

In another terminal, from this project directory:

```sh
NODE_PATH=/tmp/epic-browser/node_modules node tests/browser.cjs
```

The suite defaults to the installed macOS Google Chrome executable. Set `CHROME_PATH` to another Chrome executable and `APP_URL` to a different running app URL if needed.

## Limits

This validates prototype software behavior and the supplied mathematical example. It does not validate real Epic connectivity, clinical effectiveness, research study design, or regulatory compliance. Safari, Firefox, and production hosting were not tested.

## Manuscript-results update

Four additional tests passed for the new descriptive report: total versus documentation reductions, both conflicting label mappings, endpoint percentage-point changes, and invalid input rejection. The generated paper page passed Chrome checks for three SVG figures, the 64% correction, desktop/mobile layouts, and absence of JavaScript errors. The full suite and server restart were attempted but stalled in the local Python environment; those attempts were stopped. Earlier full-suite results above predate this update. The new `/paper` route is present in code but is not active in the previously running server until it is restarted successfully. The standalone `static/paper.html` and downloadable figures are available now.
