# Suggested manuscript changes — author applies these

The journal manuscript has **not** been modified. Only screenshots were available.
The revised proof of concept and current code use the same simulation study.

## Title and objective

Suggested framing: **A Reproducible Simulation-Based Prototype for Evaluating EHR Documentation Time and CDS Override Scenarios**.

Describe an evaluation dashboard and numerical demonstration. Do not claim a
deployed Epic-integrated AI system, a validated new clinical algorithm, or a
new statistical method. If the broader paper proposes an architecture, distinguish
that proposed architecture from the implemented local analysis prototype.

## Abstract

Replace claims of demonstrated clinical efficacy, documentation quality, or
physician burnout reduction with the actual implementation and simulation aims.
Report the original example and 5,000-row example as separate synthetic datasets.
State that no clinical deployment or patient/provider outcome evaluation occurred.

Suggested concluding sentence: “The prototype produced reproducible paired-time
and synthetic override analyses under explicit assumptions; clinical utility
requires evaluation with observed data and an appropriate study design.”

## Methods

Use `Methods_and_Limitations.md` and the revised `Proof of Concept.docx`.
Specify all four experiments separately: fixed five-pair example; 5,000-row
synthetic demonstration; independent binomial CDS counts; repeated normal-
difference evaluation. Record seeds, distributions, dimensions, rounding,
software versions, uncertainty definitions, and input hashes.

Do not describe simulated values as extracted Epic audit logs. Do not identify
332 as a recruited survey cohort: it is only one sample size in the numerical
experiment. Describe the Monte Carlo design transparently; it was added during
this revision, not performed as part of a historical deployment or preregistered
study. No prospective registration is claimed.

## Replace the Results section

Use `Suggested_Results.docx` or `Suggested_Results.md`. These are suggestions for
your review, not changes to the actual paper. They match `publication/results.json`
and the revised proof of concept exactly.

Remove from the project's Results:

- 16→4.5-minute documentation and the “up to 72%” claim;
- order-entry and chart-review reductions not evaluated by the project;
- the 54.9%→33.3% burnout result;
- the six-month 85%→25% override trajectory and 2.6%→6% interaction trajectory;
- F1=0.71 and drug-interaction error <4.8%;
- causal statements that statistical significance proves AI effectiveness.

These values may appear in a literature review only if supported by exact
citations, accurate endpoint/population definitions, and clear attribution to
those separate studies. The original NASA-TLX simulation is not retained as a
valid burnout experiment. NASA-TLX and burnout are different constructs.

## Figures

Replace the screenshot's workflow and six-month CDS graphs with canonical
figures in `publication/figures/`. Suggested numbering (adjust for the full paper):

1. **Synthetic documentation-time means.** Five fixed pairs and a separate
   5,000-row demonstration; the datasets overlap in their first five rows.
   These bars are descriptive means, without uncertainty bars.
2. **Synthetic CDS override counts.** 10,000 hypothetical alerts per group;
   assumed probabilities 0.89 and 0.34; seed 42. Error bars are Wilson 95% CIs
   under independent Bernoulli trials, not evidence of clinical effectiveness.
3. **Numerical validation under normal paired differences.** Null-scenario
   coverage and Type I error over 1,000 repetitions; error bars are ±1.96
   estimated Monte Carlo SE. The complete 24-scenario table is supplementary.

Do not reuse the earlier screenshot-derived figures as outputs of the revised
experiment. Those earlier files are retained only for traceability.

## Discussion and Conclusion

Discuss software feasibility, reproducibility, numerical behavior under model
assumptions, and limitations. Do not interpret the chosen difference means or
chosen override probabilities as discovered treatment effects. Do not equate
sample-size expansion with additional clinical evidence. Report the fixed
five-pair example's unusually small difference SD (0.05 min) and large dz (19)
as properties of that constructed example, not clinical expectations.

Suggested conclusion: “The prototype supports reproducible analysis of specified
synthetic documentation-time and CDS scenarios. Numerical findings are conditional
on the generating assumptions and do not establish clinical effectiveness.
Prospective evaluation with observed data is required before clinical claims.”

## Data/code availability and declarations

State that all datasets in this evaluation are synthetic and share the source
code, input CSVs, generation metadata, environment versions, and generated results
through your chosen repository if the journal requires access. Add the actual
repository URL only after you publish it. Do not claim a clinical ethics approval,
consent process, registration, external validation, or deployment that did not
occur. Complete funding, conflicts, authorship, and AI-assistance declarations
according to the target journal's requirements.

## Before submission

Verify the paper's novelty and fit for the target journal, apply these changes
throughout the manuscript, check all references and figure numbering, and have
the final interpretation reviewed by your supervisor or a statistical collaborator.
No editable manuscript or journal instructions were supplied, so full-manuscript
consistency and journal formatting have not been verified.
