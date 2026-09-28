# Suggested replacement Results section

Author review required. This file does not modify the journal manuscript.

## IV. Results: simulation-based prototype evaluation

The prototype was evaluated using synthetic data and reproducible numerical experiments. No real clinicians were enrolled, no Epic deployment was evaluated, and no clinical effectiveness or documentation-quality outcomes were measured. Numerical estimates below describe the supplied examples or the specified generating models.

## A. Worked paired documentation-time example

For the original five synthetic clinician pairs, mean pre- and post-intervention times were 5.11 and 4.16 minutes. The mean paired reduction was 0.95 minutes (95% Student t confidence interval [CI], 0.888–1.012), equivalent to an 18.59% relative reduction. The two-sided paired test yielded t(4) = 42.485, p = 1.83482e-06; Cohen’s dz was 19.000. The fixed example was selected for illustration; its narrow variation and large effect size do not establish a plausible clinical effect or provide evidence about a clinician population.

## B. Expanded synthetic dataset

The 5,000-row demonstration dataset retained the five original pairs and added 4,995 generated pairs. Its mean pre- and post-intervention times were 5.100 and 4.153 minutes, respectively. The mean paired reduction was 0.948 minutes (95% CI, 0.930–0.966), corresponding to an 18.58% relative reduction. The paired statistic was t(4999) = 103.544, with Cohen’s dz = 1.464. The numerical p-value underflowed to zero in double-precision computation and is reported as below numerical precision, rather than as an exact zero. These calculations demonstrate processing of a larger synthetic input; the nominal CI and p-value are conditional model summaries, not empirical evidence of clinical benefit.

## C. Synthetic CDS override counts

Independent binomial counts were generated for two groups of 10,000 hypothetical alerts using assumed override probabilities of 0.89 and 0.34. With NumPy default_rng and seed 42, the generated counts were 8,937 and 3,315, giving rates of 89.37% (Wilson 95% CI, 88.75–89.96%) and 33.15% (Wilson 95% CI, 32.23–34.08%). The difference was 56.22 percentage points. This difference reflects the input assumptions. The simulation does not contain monthly observations, proactive interaction events, diagnostic labels, or measured medication safety outcomes.

## D. Repeated numerical simulation

A separate Monte Carlo experiment evaluated the paired-difference t procedure in 24 scenarios with 1,000 repetitions per scenario. Independent normal differences were generated for sample sizes 5, 50, and 332, true means −0.50, 0, 0.50, and 0.95 minutes, and standard deviations 0.65 and 1.30 minutes. Empirical 95% CI coverage ranged from 93.1% to 97.0%. Across null scenarios, rejection at the two-sided 0.05 level ranged from 3.3% to 5.5%. The largest estimated Monte Carlo standard error for coverage was 0.80 percentage points. Scenario-level bias, coverage, rejection rates, and Monte Carlo standard errors are supplied in monte_carlo.csv. This evaluates numerical behavior under the test’s normality assumptions, not robustness to clinical confounding or evidence that AI is effective.

## E. Interpretation and scope

The results demonstrate reproducible descriptive and inferential calculations for specified synthetic inputs. The application does not train or evaluate an AI model. Burnout, workload, documentation quality, patient engagement, diagnostic accuracy, and drug-interaction errors were not measured. Clinical utility and generalizability require a separate study using appropriately collected data and a design capable of addressing confounding and repeated observations.

## References for Methods and interpretation

- [SciPy paired t-test and confidence intervals](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_rel.html)
- [NumPy random-stream compatibility](https://numpy.org/doc/stable/reference/random/compatibility.html)
- [NASA Task Load Index manual](https://humansystems.arc.nasa.gov/groups/TLX/downloads/TLX_pappen_manual.pdf)
- [ASA Statement on p-Values: Context, Process, and Purpose](https://doi.org/10.1080/00031305.2016.1154108)
- [Morris, White, Crowther (2019). Using simulation studies to evaluate statistical methods](https://doi.org/10.1002/sim.8086)
