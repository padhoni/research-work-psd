# Example datasets

`documentation.csv` contains **5,000 synthetic clinician pairs**, not collected
research observations. The first five rows retain the original proof-of-concept
values. The other 4,995 rows are generated with seed 42, with variation in both
baseline times and pre/post changes. Some post times exceed pre times.

Import this file with **Documentation time (minutes)** and
**Simulated / demonstration** selected in the application. Its computed results
will differ from the original five-row demo, which is unchanged in the app.
Increasing the synthetic record count does not increase clinical evidence.

Regenerate with Python 3.12:

```sh
python3 examples/generate_documentation.py
```

`documentation.metadata.json` records the seed, model, units, and provenance.
`workload.csv` is also simulated.
