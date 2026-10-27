# Reproduction and package instructions

Dataset `analysis-v1-15e5448d4a96` and its original digests are preserved in
`data/manifests/analysis_v1.json` at commit51e3652. All raw snapshots stay local;
Git contains acquisition instructions, source manifests, fixed role keys, small
result tables, explanations, final model weights, figures and manuscript sources.
The final test has been opened and is not a fresh evaluation set.

## Reproduce saved inference and primary tables

Restore the exact local canonicalCSV, preprocessingJSON and public-source raw
responses at their recorded relative paths. A new FDIC API response may differ
because historical data can be revised; it is not the same snapshot merely
because its query is identical. Never suppress a checksum mismatch.

```powershell
uv sync --locked --extra dev
uv run --locked pytest -q
uv run --locked python scripts/build_manuscript.py
uv run --isolated --locked --extra dev --python .venv\Scripts\python.exe python scripts/verify_research_artifacts.py --recompute-predictions --require-clean-env
uv run --isolated --locked --extra dev --python .venv\Scripts\python.exe python scripts/reproduce_figures.py
```

Add `--offline` to `uv run` only when the locked wheels are already cached. The
verifier requires the committed plan, original51e3652 manifest and final weights;
it does not fit models or tune settings. Reproduction outputs can replace prior
reproduction logs, but primary predictions and the plan remain unchanged.

To replay descriptive robustness/case extraction:
`uv run --locked risktrace robustness`. The command also writes the proposed case
packets. To supplement detailed control ledgers, use
`uv run --locked python scripts/supplement_control_ledgers.py`; it asserts the
original outputs/counts. This is a replay, not a new scientific analysis.

Training/acquisition entry points are documented in README and stage-specific
methods. The final-evaluation command refuses a silent second opening. A full
training replication should run in a separate checkout with explicit output
provenance and comparison, without replacing or reselecting the primary study.

## Manuscript and handoff documents

`scripts/build_manuscript.py` generates Markdown, structuredJSON, TeX sources,
tables and114 empirical evidence-map entries from saved results. The TeX folder
is `paper/manuscript`; `main.tex` has compiled with the desktop compiler.
`scripts/render_manuscript.py` creates the readable review PDF from the sameJSON.
Its optional renderer dependencies are `paper/requirements-render.txt`, separate
from the frozen statistical environment. Supply a directory containing
DejaVuSerif.ttf, DejaVuSerif-Bold.ttf and DejaVuSerif-Italic.ttf with `--font-dir`
if the default matplotlib font directory is unavailable. Review-PDF pagination
differs from TeX. No official venue layout has been claimed.

`scripts/build_work_allocation.py` uses python-docx from the bundled document
runtime to create the revised five-page DOCX and matching Markdown. Its assigned
ML tasks for Ayush supersede the earlier allocation; none are reported completed.

## Local archive

`scripts/build_research_package.py` creates an ignored localZIP under
`output/research_package/`. It contains a Git history bundle, exact official raw
responses referenced by source manifests, and the preserved processed snapshot.
It excludes environments, credentials, wheel/graph caches, Git configuration and
third-party literature PDFs. Source manifests and per-file digests travel with the
archive. Public redistribution terms and software licensing remain author decisions;
the archive has not been uploaded or published externally.

Unzip to a new directory, then:

```powershell
git clone RiskTrace_history.bundle RiskTrace
Copy-Item -LiteralPath preserved_data\data -Destination RiskTrace -Recurse -Force
Set-Location RiskTrace
uv sync --locked --extra dev
```

Clone the bundled history because the verifier checks the original committed
manifest and analysis plan. Confirm the archive's recorded release commit and
digests before running commands. `results/reproduction/package_manifest.json`
records the finished archiveSHA and the code commit included in the bundle; its
later registry commit is separate. The package is for local reproduction and
author review, not an approved journal submission.
