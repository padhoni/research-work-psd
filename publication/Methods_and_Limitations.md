# Suggested Methods and limitations

## Purpose and scope

This proof of concept implements a local statistical evaluation dashboard and a reproducible simulation pipeline. Its purpose is to verify calculations and illustrate conditional results. It is not a deployed Epic intervention or a new clinical efficacy study.

## Data and units

The analysis unit is a synthetic clinician-level paired value, expressed as mean active documentation minutes per encounter. The original five fixed pairs are retained in examples/documentation_original.csv. The expanded file examples/documentation.csv contains those five pairs plus 4,995 generated pairs; it is not a sample of recruited clinicians. No patient-level data are used.

## Expanded dataset generator

Python random.Random(42) generates pre = max(0.50, Normal(5.11, 0.50²)) and change = Normal(0.95, 0.65²); post = max(0.10, pre − change). Pre and change are independent draws, while pre and post are paired through the shared baseline. Both times are rounded to two decimal places after generating the pair. Negative changes are possible. This model was chosen for demonstration, not fitted to observed data; its outcome should not be interpreted as an estimated intervention effect. The original five rows are fixed, so the 5,000-row file is a mixed demonstration dataset rather than 5,000 identically generated replicates.

## Paired analysis

For d_i = pre_i − post_i, calculate mean(d), sample SD s_d, t = mean(d)/(s_d/√n), df = n − 1, and a two-sided p-value. The 95% CI is mean(d) ± t_(0.975,df) × s_d/√n. Relative reduction is 100 × (mean(pre) − mean(post))/mean(pre). Cohen’s dz is mean(d)/s_d. Independent units and approximately normal differences are the inferential assumptions. Zero variance produces undefined inference; a zero pre mean produces undefined relative reduction. Invalid, incomplete, duplicate, negative, and nonfinite inputs are rejected. Missing data are not imputed.

## CDS count model

The current application uses two sequential NumPy default_rng(42).binomial(n=10000, p) draws with p=0.89 and p=0.34 and Wilson 95% intervals. These are group totals for synthetic independent alerts, not CDS Hooks messages or real audit logs. No deployment timeline or prediction accuracy is modeled. Counts are not interchangeable with clustered clinical alerts.

## Repeated simulation specification

Aim: assess numerical estimation and inference when paired differences are normal. Data generation: independent N(delta, sigma²) differences, with n in {5,50,332}, delta in {−0.50,0,0.50,0.95}, sigma in {0.65,1.30}, and 1,000 repetitions per scenario. Seed: 20260927 with a separate NumPy default_rng; traversal order is n, delta, sigma. Estimand: mean difference. Method: two-sided one-sample t-test of differences, algebraically equivalent to the paired test. Performance: bias, 95% CI coverage, and rejection probability at alpha=0.05, interpreted as Type I error only at delta=0 and as power otherwise. Monte Carlo SE is SD(estimates)/√R for bias and √[q(1−q)/R] for proportions. No seeds or scenarios were selected to obtain desired results. Sample size 332 is an illustrative simulation setting, not a measured survey cohort. This experiment is separate from the 5,000-row demonstration.

## Removed unsupported outcomes

The original 461.3→25.0 workload simulation was removed from the publication results: its scale was undocumented, an unbounded normal model could produce invalid scores, and workload was mislabeled as burnout. The app may analyze user-supplied 0–100 NASA-TLX values, but this package reports no workload or burnout experiment. The screenshot-derived 16→4.5-minute and six-month CDS series are archived, not presented as project findings. The original 72% total-workflow claim was also inconsistent with its listed task sums (25→9 minutes would be 64%).

## Interpretation of p-values

A p-value is conditional on the statistical model and null hypothesis; it does not establish causation, clinical importance, or the truth of an intervention claim. The large differences selected in a simulation can produce small p-values by construction. Extremely small values are shown in scientific notation or labeled below numerical precision. The previous claim that p < 0.0001 mathematically proves an AI benefit is withdrawn.

## Reproducibility and original-script differences

The original script used the legacy np.random.seed(42) stream, generated two workload arrays first, and then generated individual Bernoulli alert events. The current CDS model uses a new generator and direct binomial totals, so identical numeric seeds need not give identical realized rates. The scientific assumptions and algorithm changes are explicit; the revised documents use only the current pipeline’s results. Dataset hashes and package versions are recorded in publication/results.json. Archived files document the earlier state.

## Implementation and reproduction

The statistical engine is analysis.py; simulation_study.py defines the repeated experiment; publication/build.py generates this document, suggested Results text, figures, and the application results page. Run: python -m pip install -r requirements-publication.txt; then python publication/build.py. Start the dashboard with python server.py. Verify with python -m unittest discover -s tests -v. This build used Python 3.12.6, NumPy 2.5.3, and SciPy 1.18.1; the complete environment is recorded in publication/environment.lock.txt. The journal manuscript itself is not modified by the pipeline.

## Limitations

This is a software proof of concept with a limited numerical simulation. It does not establish a new statistical method or clinical benefit. The normal-difference experiment does not test nonnormality, selection bias, clinician clustering, longitudinal confounding, measurement error, or clinical safety. The application has no live EHR integration, ambient transcription model, authentication, or deployment-grade controls. A journal submission requires author review of novelty, scope, citations, declarations, and journal-specific requirements.

- [SciPy paired t-test and confidence intervals](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_rel.html)
- [NumPy random-stream compatibility](https://numpy.org/doc/stable/reference/random/compatibility.html)
- [NASA Task Load Index manual](https://humansystems.arc.nasa.gov/groups/TLX/downloads/TLX_pappen_manual.pdf)
- [ASA Statement on p-Values: Context, Process, and Purpose](https://doi.org/10.1080/00031305.2016.1154108)
- [Morris, White, Crowther (2019). Using simulation studies to evaluate statistical methods](https://doi.org/10.1002/sim.8086)
