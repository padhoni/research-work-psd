# Application test: 5,000 synthetic records

Passed a real Chrome upload of `examples/documentation.csv` into the running application at http://127.0.0.1:8766.

| Metric | Result |
|---|---:|
| Paired records | 5,000 |
| Mean pre time | 5.100286 minutes |
| Mean post time | 4.152560 minutes |
| Mean paired reduction | 0.947726 minutes |
| Relative reduction | 18.5818% |
| 95% CI of paired reduction | 0.929782 to 0.965670 minutes |
| Paired t statistic | 103.543699 |
| Degrees of freedom | 4999 |
| Cohen dz | 1.464329 |

The p-value underflows to zero in floating-point computation; the UI and manuscript text correctly say “below numerical precision.” It is not an exact zero probability.

## Checks passed

- Original five-row demo loads.
- All 5,000 pairs rendered with 10,000 data points and simulated provenance.
- JSON and SVG exports saved; all input records preserved.
- No horizontal overflow at tablet and mobile widths.
- Duplicate clinician ID rejected; stale exports disabled.
- Valid analysis recovers after validation error.
- No JavaScript page errors.
- Independent Python standard-library calculations matched the app's means, difference, standard deviation, relative reduction, t statistic, and effect size to numerical tolerance.

Analysis and rendering took 186 ms in this single local run, excluding CSV upload and exports. This is not a load benchmark.

## Artifacts

- `dashboard.png`: actual application screenshot with the dataset loaded.
- `mobile.png`: mobile layout screenshot.
- `paired_outcomes.svg`: graph downloaded through the application.
- `research_bundle.json`: downloaded results and all 5,000 original input rows.
- `test_report.json`: browser checks and numerical output.
- `independent_calculations.json`: separate calculation cross-check.

All 5,000 records are synthetic. These results validate application behavior and illustrate the generating assumptions; they are not clinical evidence. This run tests the existing running instance's paired-analysis workflow, not live Epic integration or the newer manuscript route.

Repeat the browser test from the project root:

```sh
NODE_PATH=/tmp/epic-browser/node_modules node tests/large_dataset.cjs
```
