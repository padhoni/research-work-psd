"""Paired, clinician-level research analyses; no clinical decision support."""
import csv
import io
import math
import hashlib
import platform
import numpy as np
import scipy
from scipy import stats

DEMO = 'clinician_id,pre,post\nC01,5.30,4.30\nC02,4.90,4.00\nC03,5.50,4.50\nC04,4.80,3.90\nC05,5.05,4.10\n'

def analyze(text, metric='time', source='simulated'):
    try:
        with np.errstate(over='raise', invalid='raise', divide='raise'):
            result = _analyze(text, metric, source)
        numbers = [v for v in result.values() if isinstance(v, float)] + (result['ci'] or [])
        if not all(math.isfinite(v) for v in numbers):
            raise FloatingPointError()
        result['reproducibility'] = {
            'python': platform.python_version(), 'numpy': np.__version__,
            'scipy': scipy.__version__,
            'input_sha256': hashlib.sha256(text.encode('utf-8')).hexdigest(),
            'test': 'Two-sided paired t-test', 'confidence_level': 0.95,
        }
        return result
    except (FloatingPointError, OverflowError):
        raise ValueError('Values exceed the supported numeric range. Check the input units and magnitudes.') from None

def _analyze(text, metric='time', source='simulated'):
    if metric not in ('time', 'workload') or source not in ('simulated', 'observed'):
        raise ValueError('Invalid metric or data source.')
    reader = csv.DictReader(io.StringIO(text.strip().lstrip('\ufeff')))
    if reader.fieldnames != ['clinician_id', 'pre', 'post']:
        raise ValueError('CSV must have exactly these columns: clinician_id,pre,post')
    rows, seen = [], set()
    for line, row in enumerate(reader, 2):
        if len(rows) >= 10000:
            raise ValueError('Maximum 10,000 clinician pairs.')
        ident = (row.get('clinician_id') or '').strip()
        if not ident or ident in seen or len(ident) > 80 or None in row:
            raise ValueError(f'Line {line}: use a unique pseudonymous clinician ID and three columns.')
        try:
            pre, post = float(row['pre']), float(row['post'])
        except (ValueError, TypeError):
            raise ValueError(f'Line {line}: pre and post must be numbers.')
        if not all(math.isfinite(x) and x >= 0 for x in (pre, post)):
            raise ValueError(f'Line {line}: values must be finite and nonnegative.')
        if metric == 'workload' and max(pre, post) > 100:
            raise ValueError(f'Line {line}: NASA-TLX scores must be between 0 and 100.')
        seen.add(ident)
        rows.append(dict(clinician_id=ident, pre=pre, post=post, difference=pre-post))
    if len(rows) < 2:
        raise ValueError('At least two complete clinician pairs are required.')
    a, b = np.array([r['pre'] for r in rows]), np.array([r['post'] for r in rows])
    d, n = a-b, len(rows)
    mean, sd = float(np.mean(d)), float(np.std(d, ddof=1))
    warnings = ['A before/after comparison does not establish causation. Independent clinicians and approximately normal paired differences are assumed. Repeated encounters must first be aggregated per clinician using a predefined rule.']
    if n < 30:
        warnings.append('Small sample: assess paired differences and study design before interpreting inference.')
    if source == 'simulated':
        warnings.append('SIMULATED DATA: these results demonstrate the method and are not clinical evidence.')
    t = p = dz = ci = None
    if sd <= np.finfo(float).eps * float(np.max(np.abs(d))) * 10:
        warnings.append('Paired differences have zero variance; t-test, effect size, and confidence interval are undefined.')
    else:
        result = stats.ttest_rel(a, b)
        interval = result.confidence_interval(confidence_level=.95)
        t, p, dz = float(result.statistic), float(result.pvalue), mean/sd
        ci = [float(interval.low), float(interval.high)]
    pre, post = float(a.mean()), float(b.mean())
    reduction = 100*mean/pre if pre else None
    unit = 'minutes' if metric == 'time' else 'NASA-TLX points'
    label = 'Simulated' if source == 'simulated' else 'User-supplied observational'
    report = f'{label} paired data from {n} clinicians were analyzed. Mean pre-intervention and post-intervention values were {pre:.3f} and {post:.3f} {unit}, respectively. The mean paired difference (pre minus post) was {mean:.3f} {unit}.'
    if ci:
        p_text = 'p below numerical precision' if p == 0 else f'p = {p:.6g}'
        report += f' The 95% confidence interval was [{ci[0]:.3f}, {ci[1]:.3f}]; two-sided paired t({n-1}) = {t:.3f}, {p_text}; Cohen dz = {dz:.3f}.'
    else:
        report += ' Inferential statistics were undefined because paired differences had zero variance.'
    report += ' These results do not establish causality or changes in burnout, patient engagement, or clinical safety.'
    return dict(n=n, pre=pre, post=post, difference=mean, sd=sd, reduction=reduction, t=t, p=p, df=n-1, ci=ci, dz=dz, rows=rows, warnings=warnings, report=report, metric=metric, source=source)

def whole_number(value):
    """Accept integer form fields without truncating fractional JSON numbers."""
    if isinstance(value, bool):
        raise ValueError('Seed and alert count must be whole numbers.')
    try:
        number = float(value)
        if not math.isfinite(number) or not number.is_integer():
            raise ValueError()
        return int(number)
    except (ValueError, TypeError, OverflowError):
        raise ValueError('Seed and alert count must be whole numbers.') from None

def simulate(seed=42, n=10000, legacy=.89, ai=.34):
    seed, n = whole_number(seed), whole_number(n)
    if not 0 <= seed <= 2**32-1 or not 10 <= n <= 100000 or not all(0 <= x <= 1 for x in (legacy, ai)):
        raise ValueError('Use seed 0–4294967295, 10–100000 alerts per group, and probabilities between 0 and 1.')
    rng = np.random.default_rng(seed)
    counts = [int(rng.binomial(n, rate)) for rate in (legacy, ai)]
    groups = []
    for name, count in zip(['Legacy CDS', 'AI-assisted CDS'], counts):
        ci = stats.binomtest(count, n).proportion_ci(method='wilson')
        groups.append(dict(name=name, overrides=count, total=n, rate=100*count/n, ci=[100*ci.low, 100*ci.high]))
    return dict(seed=seed, n=n, legacy_probability=legacy, ai_probability=ai, groups=groups, difference_pp=100*(counts[0]-counts[1])/n, source='simulated', reproducibility={'numpy': np.__version__, 'scipy': scipy.__version__, 'generator': 'default_rng (PCG64); two sequential binomial totals'}, note='Synthetic independent binomial groups, not live CDS Hooks telemetry. A lower override rate does not establish alert quality or clinical safety. Wilson 95% intervals assume independent alerts; real alerts may be clustered.')
