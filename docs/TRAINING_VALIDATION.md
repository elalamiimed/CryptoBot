# Training and evaluation

## Current protocol

All five trainers use `temporal_validation.py`:

1. Sort real rows by launch timestamp (`t0`), using positional indices. Keep
   simultaneous launches in the same block. Synthetic trainers use generation
   order (`mint_id`); that is not evidence about chronological market performance.
2. Reserve the last chronological block before tuning. Real labels declare
   `label_end = t0 + observation window + outcome horizon`. Before each fit,
   remove every training row whose label ends at or after validation begins.
3. Tune hyperparameters and early stopping on early development folds only.
   Tuning labels must have matured before subsequent evaluation starts.
4. Produce development predictions on later folds, with fixed hyperparameters.
   These rows can be used to select a trading policy. Their outcome windows must
   finish before the final holdout starts.
5. Fit the candidate on matured pre-holdout rows. Evaluate the final block
   without fitting, early stopping, or threshold searching on that block.
   The exported model is this pre-holdout model; it is not refitted on test rows.

Single-class evaluation periods stay in the evaluation. Undefined AUCs are
reported as unavailable (`NaN`), rather than dropping those periods. Insufficient
chronological data produces an error; there is no random-fold fallback.

`--n-tune-folds` is an upper limit. At least one later development fold and a
separate final holdout are always reserved. Purging can leave too little data
even when there are many tokens: many launches in the same hour are not many
independent evaluation periods. Collect a longer cohort in that case.

The optional wallet-registry feature is disabled during real-data training:
the existing registry was built using outcomes from the same cohort.

## Run

```powershell
python -X utf8 -B -m unittest discover -s tests -v
python -X utf8 -B train_gates_real.py
```

The real trainer writes a new `training_runs/<UTC timestamp>/` directory:

- `rug_pull_model_real_candidate.joblib`
- `alpha_pump_model_real_candidate.joblib`
- `gate_oof.csv`: development predictions only; tuning, embargo, and final-test
  rows have missing probabilities.
- `gate_policy_study.json`: development policy search, separate final model
  metrics, audited time boundaries, and a final evaluation of the frozen policy.

`--out-dir` must name a new directory. `--out-prefix` changes filenames within
that directory. Legacy trainers default to timestamped candidate filenames and
refuse existing files or the live model filenames. Nothing promotes candidates
to the paper trader automatically.

Policy selection uses only the development probabilities. If no policy meets
the minimum development trade count, the report says the final policy was not
evaluated; it does not relax the threshold based on the final results.

`window_experiment.py` uses development predictions and suppresses final model
evaluation. Window comparisons remain exploratory: choosing a window changes
the eligible cohort, so a later prospective cohort is still needed to confirm
that choice. Downstream studies must explicitly point to the new run's OOF file;
the root-level historical artifacts are preserved.

## Interpretation

Existing root-level model scores and studies used the interleaved splitting bug
and remain historical, invalid evidence of forward performance. The new code
does not repair previously saved results. A one-trial smoke run verifies the
software path, not trading performance.

The final block is held out by this procedure, but this old dataset has already
been explored in earlier studies. A genuinely unseen test requires newly
collected future data. Do not repeatedly optimize settings against final-test
results and continue calling that period untouched.

These changes fix training chronology and evaluation separation. They do not
resolve the separately identified entry-quote mismatch, stale-fill assumptions,
data selection bias, or differences between replay and live execution.

## Strategy reassessment update

`train_gates_real.label_token` no longer turns missing prints into rug or
non-pump labels. A pump hit observed in the declared hour is positive; a
negative label needs a sampled hour with an endpoint within 30 seconds and
no observed gap over 210 seconds. The failure proxy also requires that full
sampled hour, since its terminal-price condition cannot be known earlier.
These are sampled CSV proxies, not proof of continuous coverage or an actual rug.

`strategy_reassessment.py` audits the old dataset and reports prospective
scores only from the frozen, versioned study created by `cohort_study.py`.
It compares the one-hour and seven-day policies separately against fixed
baselines. Root-level saved models and old scores are not replaced or recertified.
