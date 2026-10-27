# Step 12: robustness and proposed finance case packets

All analyses retain the committed pre-test plan and primary predictions. The
technical work is complete; Ayush's case selection and finance interpretation
remain pending. No contact or approval is claimed.

## Uncertainty and sensitivity

The paired bootstrap resamples connected CERT/RSSD institution components and
calendar-year blocks independently, multiplying their row counts. The same
weights compare each model with XGBoost. There are 500 draws, not 500 independent
banking populations. Only four positive test banks and four report-year blocks
(2025 partial) are available. AP is undefined in 82 draws without weighted
positives. AP percentiles condition on the 418 defined draws and do not have
established nominal 95% coverage. Brier uses all 500. See
`results/robustness/crossed_intervals.csv` and `paired_differences_vs_xgboost.csv`.

The primary current-input mean conditional/pipeline gap is 0.015143 percentage
points; its exploratory resampling range is 0.011311--0.020608 pp. For one-lag
historical edits the mean is 0.006993 pp and range 0.004830--0.009989 pp. These
are probability percentage points, not relative percentage changes or causal
financial effects. All 500 mean-gap draws are defined. Seed ranges and
report-year strata are sensitivity checks, not independent-event confidence
intervals. A report year with no positive forecast windows can still contain a
failure observed/predicted from an earlier report year.

No prespecified graph variant establishes useful warning superiority. At fixed
development thresholds, all graph variants and XGBoost miss all four test banks;
logistic detects one at an achieved test FPR of 2.005%. No test threshold is
retuned. The result limits the practical relevance of explanation comparisons.

## Case packets

The proposed register covers CERT24735 Silicon Valley Bank (2023), CERT57053
Signature Bank (2023), CERT59017 First Republic Bank (2023) and CERT27332 Republic
Bank (2024). Republic Bank and First Republic are distinct entities. These are
retrospective illustrative selections from the test outcomes, not a new primary
evaluation or evidence that forecasts were issued prospectively.

Controls use the same pre-event report and charter, assets within a factor of
two, nearest log assets, an observed nonfailure horizon, and a different connected
identity component. `results/case_studies/` contains the matching register,
forecast trajectories, exact financial/edge explanation extracts and an explicit
review-status record. Ayush should check source/entity meaning, matching,
plausibility and interpretation. The primary ML work was completed under Atharva's
stream. The later user instruction now assigns Ayush independent baseline ML
replication and development explanation work; see revised_work_allocation.md.
Those newly assigned tasks are not claimed complete.

`scripts/build_figures.py` creates four PNG/SVG pairs directly from saved outputs.
All four have been visually inspected; the revised case figure uses explicit
quarter/half-year date ticks. Brier comparisons should be made within a split
because event prevalence differs between development and test. Financial gaps
use donor-matched denominators; complete-ranking denominators are separate.

## Execution

```powershell
.venv\Scripts\risktrace.exe robustness
.venv\Scripts\python.exe scripts/build_figures.py
```

The `robustness` command also creates the case packets; the saved run is already
complete. Replaying descriptive analysis does not authorize test-driven tuning,
new scientific targets or an expansion of the project.
