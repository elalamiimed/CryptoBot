# Raw-wallet concentration vs coordination — first measurement, 27 September 2026

**Why this exists.** F4 (entity-adjusted concentration) is the highest-confidence
remaining filter in the research brief, and it is blocked on a wallet-funding
graph this project has no source for. But its central claim — *concentration
carries information about coordination* — is testable **today**, because MELT
ships a ground-truth coordination flag and the already-built feature frame
carries raw-wallet concentration features.

Answering it changes what the entity graph is worth spending on.

## Method

- **Data:** `melt_full_features_frame.joblib` (42,106 rows, build_version 5) with
  `melt_label.csv`.
- **Target:** `melt_manipulated` — MELT's own coordination label.
  Cohort = the definite labels only: **34,151 rows, 22,435 manipulated
  (prevalence 65.7 %)**, excluding 5,880 `unknown`.
- **Features:** pre-decision window features only, from an explicit **allow-list**
  (never a deny-list, so a label column added later cannot silently leak in).
- **Model:** logistic regression on standardised features, 5-fold stratified CV,
  **repeated over 5 seeds**.
- Probe: `tmp/_concentration_vs_coordination.py`. Read-only; writes nothing.

## Result 1 — concentration is the strongest single signal measured here

| feature | AUC | reading |
| --- | ---: | --- |
| `top_3_buyers_volume_pct` | **0.634** | higher ⇒ manipulated |
| `volume_hhi` | **0.633** | higher ⇒ manipulated |
| `unique_buyer_to_tx_ratio` | 0.586 | higher ⇒ manipulated |
| `dev_proxy_indicator` | 0.574 | higher ⇒ manipulated |
| `buy_sell_cnt_ratio` | 0.573 | lower ⇒ manipulated |
| `sale_percentage` | 0.572 | higher ⇒ manipulated |
| `total_sol_value` | 0.532 | higher ⇒ manipulated |
| `unique_buyers` | 0.531 | lower ⇒ manipulated |
| `count_tx` | **0.527** | lower ⇒ manipulated |
| `informed_trader_ratio` | **0.500** | **no information at all** |

Raw-wallet concentration carries roughly **twice the rank information** that
transaction count does. That is a direct empirical check on this project's own
assumption that activity volume is the manipulation signal — **it is not**; the
concentration of that activity is.

## Result 2 — concentration adds a large, stable increment

5-fold CV, repeated over 5 seeds:

| feature set | mean AUC | min | max | sd |
| --- | ---: | ---: | ---: | ---: |
| activity only (`count_tx`) | 0.5250 | 0.5244 | 0.5253 | 0.0004 |
| **concentration only** | 0.6715 | 0.6715 | 0.6716 | 0.0001 |
| **activity + concentration** | **0.6862** | 0.6862 | 0.6863 | 0.0001 |
| all observable features | 0.7014 | 0.7013 | 0.7015 | 0.0001 |

- **Δ AUC = +0.161** at the mean, **+0.161 at the worst case** (activity's best
  seed against the combined set's worst). The effect is not one lucky fold.
- The seed-to-seed sd is ~1e-4, i.e. **the measurement is stable** and the
  reported differences are far larger than the sampling noise of the split.

## What this does and does not establish

**Does.** Raw-wallet concentration is a real, strong, stable signal about MELT's
coordination label on this cohort, and it is materially stronger than the
activity features this project already uses. That is a measured reason to expect
F4 to be worth building, and a reason to distrust raw transaction count as a
manipulation proxy.

**Does not.**

- **It is not F4, and it does not measure what the entity graph would add.** No
  funder, bundle or co-purchase evidence is used, so this is the *baseline F4
  must beat*. A graph can only add the gap between raw and entity-adjusted
  concentration — and because the graph *raises* concentration for coordinated
  tokens (S2 reports roughly +24 points of top-10 concentration for high-risk
  tokens), the realistic expectation is that it adds signal rather than none.
  Quantifying that needs the graph.
- **It is not a trading edge.** The target is a coordination label, not P&L, and
  no cost, exit or position model enters here.
- **These are in-sample-CV numbers on ONE dataset.** The audit that prompted this
  repair track found naive crypto evaluation inflating Sharpe by 3.6×. Nothing
  here has been tested out of sample, on a second cohort, or forward in time.
- **The cohort is MELT's own population** (Dec 2024–Feb 2025, pre-migration) and
  its own labelling procedure. `manipulated` is partly a *modelling* judgement,
  so part of this AUC could be the label agreeing with concentration by
  construction. This is the most important caveat and it is not removable from
  inside this dataset — an independent coordination measure would be needed.
- **`informed_trader_ratio` is exactly 0.500**, which is worth its own note: a
  feature in the existing 28-vector carries *zero* rank information on this
  cohort. That is not proof it is useless (it may matter on other populations or
  targets) but it should not be assumed to contribute.

## Consequence for the plan

`GOAL.md` Phase C is **not** fully blocked. The advisory half of F4 — *does
concentration know anything about coordination?* — is now answered: **yes, and
more than activity does.** What remains blocked is the part that needs the
entity graph: measuring how much *merging* wallets adds on top, and the F5
creator-cluster history that depends on the same funding evidence.

That sharpens the purchase decision rather than replacing it: the graph is now
justified by an independent measurement, but its marginal value over raw
concentration is still unquantified, and cannot be quantified without it.
