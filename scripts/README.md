# Research scripts

These four standalone scripts are the analysis code the published studies need
and that does **not** import the paper-trading engine (removed from this
research-only edition):

| script | what it does |
| --- | --- |
| `winners_collector.py` | Key-less, resumable collector that builds the 2025–26 Solana memecoin universe from public endpoints (CoinGecko, pump.fun, DexScreener) and the 12-hour candle paths. Writes the `winners_*.json`/`.csv` inputs shipped under `data/winners/`. |
| `winners_study.py` | The case-control study: definitions, launch-time and early-life features, grouped cross-validation classifiers, price-path and trailing-stop analysis. Produces `winners_study_report.md`, `winners_study.json`, `winners_1000x.csv`, `winners_launchpad_all.csv`. |
| `melt_to_csv.py` | Converts a MELT release (`pre_migration_tx/*.jsonl`, optional `post_migration_tx_1hour/`) into the 7-column trade CSV used by the MELT models. |
| `select_covered_cohort.py` | Keeps only tokens whose collected tape spans the decision + holding horizon (the "covered cohort" whose survivorship effect is measured in `reports/cohort_survivorship_20260927/`). |

## Environment

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

See the repository README for the exact reproduction commands and for the
licence terms (scripts: MIT; data/reports: CC BY-NC 4.0).

## Not included

The paper-trading engine, its execution/accounting/audit code, launchers, tests
and run directories are not part of this repository. Analysis and training
scripts that imported that engine (gate training, per-token atomic/markout
scans, paper-book measurement, replay tools) are therefore not shipped; the
artifacts they produced are in `reports/` and `data/`.
