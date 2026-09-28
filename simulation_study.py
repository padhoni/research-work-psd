"""Reproducible numerical validation under explicitly assumed normal differences.
No clinical intervention, clinician population, or Epic telemetry is modeled.
"""
import numpy as np
from scipy import stats


def run_study(seed=20260927, repetitions=1000):
    if isinstance(repetitions, bool) or not isinstance(repetitions, int) or repetitions < 2:
        raise ValueError('At least two integer repetitions are required.')
    rng = np.random.default_rng(seed)
    scenarios = []
    # Fixed traversal order is part of the reproducibility specification.
    for n in (5, 50, 332):
        for true_difference in (-0.5, 0.0, 0.5, 0.95):
            for sd in (0.65, 1.30):
                differences = rng.normal(true_difference, sd, size=(repetitions, n))
                estimates = differences.mean(axis=1)
                result = stats.ttest_1samp(differences, popmean=0, axis=1)
                ci = result.confidence_interval(confidence_level=0.95)
                coverage = float(np.mean((ci.low <= true_difference) & (true_difference <= ci.high)))
                rejection = float(np.mean(result.pvalue < 0.05))
                scenarios.append(dict(n=n, true_difference=true_difference, sd=sd,
                    repetitions=repetitions, bias=float(np.mean(estimates-true_difference)),
                    bias_mcse=float(np.std(estimates, ddof=1)/np.sqrt(repetitions)),
                    coverage=coverage, coverage_mcse=float(np.sqrt(coverage*(1-coverage)/repetitions)),
                    rejection_rate=rejection, rejection_mcse=float(np.sqrt(rejection*(1-rejection)/repetitions)),
                    rejection_interpretation='Type I error' if true_difference == 0 else 'Power'))
    return dict(seed=seed, repetitions=repetitions, scenario_count=len(scenarios),
        generator='NumPy default_rng; normal paired differences; order n, true_difference, sd',
        assumptions='Independent normally distributed paired differences; no missingness, confounding, or clustering. Negative differences represent worsening.',
        estimand='Mean paired difference in minutes; positive values represent a reduction.',
        method='Two-sided one-sample t-test of paired differences; equivalent to the paired t-test.',
        nominal_confidence=0.95, alpha=0.05, scenarios=scenarios)
