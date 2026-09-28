"""Generate 5,000 synthetic clinician pairs for application testing.

Run with Python 3.12: python3 examples/generate_documentation.py
The original five simulated pairs are retained verbatim. Additional rows
are artificial examples, not observations or evidence of clinical benefit.
"""
import csv
import json
import random
from pathlib import Path


ORIGINAL = [
    ('C01', '5.30', '4.30'),
    ('C02', '4.90', '4.00'),
    ('C03', '5.50', '4.50'),
    ('C04', '4.80', '3.90'),
    ('C05', '5.05', '4.10'),
]
SEED = 42
RECORD_COUNT = 5000


def main():
    rng = random.Random(SEED)
    rows = list(ORIGINAL)
    for number in range(6, RECORD_COUNT + 1):
        # Correlated pairs with heterogeneous changes, including increases.
        pre = max(0.50, rng.gauss(5.11, 0.50))
        change = rng.gauss(0.95, 0.65)
        post = max(0.10, pre - change)
        rows.append((f'C{number:02d}', f'{pre:.2f}', f'{post:.2f}'))

    folder = Path(__file__).resolve().parent
    with (folder / 'documentation.csv').open('w', newline='') as handle:
        writer = csv.writer(handle, lineterminator='\n')
        writer.writerow(['clinician_id', 'pre', 'post'])
        writer.writerows(rows)
    metadata = {
        'source': 'simulated',
        'purpose': 'Application testing and statistical method demonstration',
        'record_count': RECORD_COUNT,
        'original_simulated_records_preserved': 5,
        'additional_synthetic_records': RECORD_COUNT - 5,
        'seed': SEED,
        'generator': 'Python 3.12 random.Random(seed).gauss',
        'units': 'minutes per encounter',
        'model': {
            'pre': 'max(0.50, Normal(mean=5.11, sd=0.50))',
            'change': 'Normal(mean=0.95, sd=0.65), independent of pre',
            'post': 'max(0.10, pre - change)',
            'rounding': 'Two decimal places after generating both values',
        },
        'interpretation': 'All records are synthetic, including the original five. '
                          'Generated sample size and p-values are not clinical evidence. '
                          'Select Simulated / demonstration when importing this CSV.',
    }
    (folder / 'documentation.metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(f'Wrote {len(rows):,} synthetic records to {folder / "documentation.csv"}')


if __name__ == '__main__':
    main()
