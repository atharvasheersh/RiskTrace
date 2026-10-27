# Pre-opening technical revision

The first `evaluate-final` call after plan commit 38f98d2 was rejected by its
committed-plan equality guard. Python's Windows text writer had emitted CRLF while
Git normalized the JSON blob to LF. The bytes differed despite identical numeric
choices. **No holdout-opening log, final-test fit or prediction was created.**

Preserve the original plan as final_analysis_plan_v1.json and in commit 38f98d2.
Fix JSON writing to emit LF explicitly and compare tracked text hashes in canonical
LF form. Raw-response, dataset, split-gzip and checkpoint hashes remain byte-exact.
Rebuild and commit the corrected pre-opening plan with unchanged dataset, split
membership, model choices, alert thresholds and analysis settings. This is an
engineering correction before any test performance, not test-driven retuning.
The failed gate and its resolution remain part of the research record.
