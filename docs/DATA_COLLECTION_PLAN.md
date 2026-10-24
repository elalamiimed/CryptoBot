# Data coverage gate — 17 September 2026

The canonical trainer was executed against `real_solana_trades.csv`.
It returned its chronological coverage refusal (exit 2), writing no models.
Full output: `tmp/training_finalization.stdout.log`.

- 608 tokens; 551 featured; 33 short windows and 24 unit breaks excluded.
- Rug: 2 positive, 7 negative, 542 unobserved labels.
- Pump: 54 positive, 4 negative, 493 unobserved labels.
- 394 tokens lack post-window observation; 477 replay paths are incomplete.

## Re-verified 18 September 2026 (fresh `train_gates_real.py` run)

Re-ran the canonical trainer today; the refusal is unchanged and now precisely
quantified. The launch timestamps (`t0`) span **17.76 hours across exactly 2
distinct UTC launch days** (`2026-09-10T09:45Z` → `2026-09-11T03:30Z`), with 530
distinct launch times. `validation_plan` refuses for **every** chunk count from
8 down to 3:

- `rug_label`: 9 non-null (2 positive / 7 negative) → "Final chronological holdout
  lacks labels or usable training" at chunks 3–8.
- `pump_label`: 58 non-null (54 positive / 4 negative) → "Need separate tuning and
  evaluation folds before the holdout" (chunks 3–6) and "No usable tuning labels
  mature before evaluation" (chunks 8), because the 4 negatives cannot be spread
  over enough separated time blocks.

Root cause: the full-hour "covered" label (last print within 30 s of the hour end
and no gap > 210 s) is met by only **9 of 551** featured tokens (~1.6%). The two
calendar days are far below the multi-block separation the chronological gate
demands. No code change resolves this; only additional spread-out collection does.

## Update — 19 September 2026: the training gate was met from historical data

**The "collect more data or the gate refuses" conclusion above is superseded.**
A downloaded historical dataset removed the blocker without any forward
collection and without payment:

| Step | Script | Output |
| --- | --- | --- |
| MELT `pre_migration_tx/*.jsonl` → 7-column CSV | `melt_to_csv.py` | `melt_solana_trades.csv` — 3.07 GB, 45,589 tokens |
| Keep tokens whose tape spans `t0 + 3900 s` | `select_covered_cohort.py` | `melt_solana_trades_covered.csv` — 1.03 GB, **6,811 tokens** |
| Train with MELT full-trace labels | `train_gates_real.py --labels-csv melt_label.csv` | `training_runs/20260919T063017_910992Z/` |

Source: MELT (Georgia Tech, CC BY-NC 4.0), pre-migration pump.fun transactions.

The launch span is **56.8 days** (2025-01-03 → 2025-02-28), which clears the
multi-block separation the chronological gate demanded. Validation passed with
4 tuning folds, 1 evaluation fold and 1 untouched final holdout. Final-holdout
ROC-AUC: rug **0.701**, pump **0.616**.

Two things this does **not** settle:

1. **It is not prospective evidence.** MELT is one historic regime, it has
   already been explored, and the positive buy-all baseline (+0.0594 SOL, 64.8%
   win rate) is a reason to suspect selection in a dataset of tokens that
   reached migration. The 28-day prospective cohort below remains the only way
   to confirm the result out of sample.
2. **The gate metrics say nothing about the second gate.** On the covered cohort
   the pump gate's final-holdout ROC-AUC is 0.529 against a 0.274 base rate,
   i.e. at chance. A policy that trades most of a cohort with a positive
   baseline inherits the baseline, not gate skill.

### Update — 20 September 2026: the covered-cohort retrain ran

`melt_solana_trades_covered.csv` has now been used as a training input
(`training_runs/20260919T183907_348292Z/`), after fixing a trim defect that was
removing the print the hold exit fires on. Every position closes
(`n_open = 0`), so the selection rule is satisfied for the first time and a
policy is selected (rug gate ≤ 0.60, pump gate ≥ 0.40, trailing 50%, TP 3.0x,
idle 180 s) and frozen on the untouched holdout: n=539, mean +0.1002 SOL/trade,
90% CI [+0.0911, +0.1095]. See the original finalization report (not part of this research-only edition)
for the honest reading — the pump gate is still at chance there, and nothing
was promoted.

## Concrete collection target (now prospective confirmation, not the training gate)

Resume the original 28-day observation cohort with unchanged calendar deadlines.
Minimum assessment coverage is 100 rankable tokens across 14 distinct days,
with one-hour and seven-day completeness reported separately. At 20 eligible
tokens/day this requires 280 admissions over 14 days and at least 35.8% complete
outcomes to reach 100. This is a planning calculation, not a forecast. Report
actual admission and completion rates daily; never infer missing negatives.

A training fit additionally needs eight genuinely consecutive time blocks with
purged label ends, both classes in usable training, enough positive validation
examples for the configured minimum of two, separate tuning/evaluation folds,
and an untouched final holdout. A sample-count target does not guarantee that
class distribution. Re-run `validation_plan` without fitting to check coverage;
do not relax it if collection falls short. That condition is now met by the MELT
tape, but a prospective cohort still has to meet it on live data. No new model
has been promoted to the paper trader.

## Data needed for retraining

The frozen observer records features/scores and sampled quote outcomes; it does
not export the canonical raw-trade training schema. Preserve it as the fixed
evaluation cohort.

Forward collection has been removed (see `FORWARD_COLLECTION_REMOVAL.md`); there
is no VPS and no paid RPC/indexer, and the zero-cost chain endpoint cannot page
deep history at scale. The practical data path is therefore the existing free
recent collector `real_data_fetcher.py`, which writes the exact 7-column CSV
schema (`timestamp, wallet, direction, sol_amount, token_amount, block_number,
token_address`) that `historical_backtester.py` / `train_gates_real.py` consume.
Use `--min-age-min 90` (or similar) so the returned rows carry *matured* labels,
not the freshly launched launch-window tapes the free endpoint cannot backfill.

Honest limitation: GeckoTerminal's key-less pool-trades endpoint serves only the
~300 most recent swaps of the last 24 h with no backward pagination, and
per-wallet launch tapes of 2025 tokens are not recoverable without a paid
indexer. Reconstructed chain cost basis (the reusable `sword/` parser/ledger/
registry/evaluator components) still applies to any tape we do obtain; do not
silently label legacy feed amounts as chain-derived.

A second free path supplies exactly the deep history the live collector cannot:
a downloaded **MELT** release (research dataset, CC BY-NC 4.0) of pump.fun
pre-migration transactions, converted by `melt_to_csv.py` into the same 7-column
schema. It is historical (Jan–Feb 2025) and therefore useful for fitting, not
for prospective confirmation. Its rug/pump targets are not derived here: MELT
ships them in its own `data/label/label.csv`, a copy of which is the local
`melt_label.csv`. The trainer now records `labels_csv` and `labels_sha256`
alongside the tape's `source_sha256`, and
`check_training_coverage.py --labels-csv …` prints the labels hash before
fitting. The 19 September run predates that record, so its labels were verified
after the fact instead:
`sha256(melt_label.csv) = dcfcce188fb352466b76ab8345f79633766c93e96d29729282ab114133fcc09a`.

Budget: no per-minute RPC budget applies to the free recent collector path; the
constraint is the endpoint's rolling 24 h window, not a 28-day forward schedule.
MELT requires no network access once downloaded.

## Operational prerequisites

The free recent collector runs on the local machine with no VPS and needs only
periodic connectivity to refresh the rolling window. Re-run it and re-check
`validation_plan` coverage before fitting; do not relax the chronological gate
if collection falls short. The 30-minute discovery audit is stored separately
under `strategy_reports/finalization_discovery_20260917`. Until that gate
completes, do not describe the full new pipeline as validated or finalized.
