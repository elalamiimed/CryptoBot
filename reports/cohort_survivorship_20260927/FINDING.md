# The MELT cohort is MIGRATED-ONLY, and it invalidates the economic readings

**Every economic measurement in this project's research track is conditioned on
survival to migration.** That is not a nuance; it changes how the numbers must be
read, and it was not recorded anywhere before this document.

## The evidence

| set | mints |
| --- | ---: |
| `pre_migration_tx` (bonding-curve tape) | 45,609 |
| `post_migration_tx_1hour` (the first hour AFTER migration) | 45,792 |
| `melt_label.csv` (the labelled cohort) | 41,470 |
| **labels present in the post-migration tape** | **41,470 of 41,470** |
| pre-migration mints with NO post tape | 115 |

Stated precisely: **`labels ⊆ post` holds exactly** — all 41,470 labelled mints
have a post-migration tape. A post tape exists only for a token that *migrated*.
Most pump.fun launches never do; they die on the bonding curve. So the cohort is
**not a sample of launches. It is a sample of survivors.**

`MELT`'s own documentation says the paper samples tokens that **completed
migration**, and `strategy_reports/profitability_audit_20260927/report.md` §6
recorded the same thing in this repository's own words:

> "The MemeTrans paper cited by the project explicitly samples tokens that
> completed migration... A model evaluated on that survivor population does not
> thereby establish performance on the full population of newly launched tokens."

The warning was already on file. This document supplies the **measurement** that
shows how large its effect is.

## How large

Two independent measurements, same market, same kind of token, opposite answers:

| measurement | 4× rate | population |
| --- | ---: | --- |
| peak from launch on the labelled cohort | **93.6 %** | migrated survivors |
| peak from 360 s on the labelled cohort | **72.0 %** | migrated survivors |
| the paper book's own realised 4× fills | **1.5 %** (2 / 137) | **all** launches it saw |

Peak from launch falls to peak from 360 s at a ratio of **0.77** — real, and much
smaller than the gap that remains. **Entry timing is not the explanation.** The
rest is the population.

`peak_0 → peak_360` on the same cohort:

| entry | median peak | ≥2× | ≥4× | ≥10× |
| --- | ---: | ---: | ---: | ---: |
| launch (t=0) | 13.19 | 97.4 % | **93.6 %** | 82.0 % |
| 60 s | 9.33 | 92.0 % | 76.3 % | 47.1 % |
| 300 s | 8.22 | 88.1 % | 72.5 % | 41.6 % |
| 360 s | 8.10 | 88.0 % | **72.0 %** | 40.5 % |

A median peak of **8×** on a cohort where most tokens are supposed to die is not a
property of pump.fun launches. It is a property of tokens that already graduated.

## What this invalidates, and what it does not

**Invalidated as statements about the tradeable population** — every economic AUC
in this track, and every comparison built on one:

- `family_signal_20260927/REPORT.md` — all four families' economic AUCs (0.605–0.622
  single-feature; 0.72–0.73 multivariate), and the "families are one factor" reading.
- `concentration_vs_coordination_20260927/ECONOMIC_CHECK.md` — the
  label-vs-money gap (0.77 on `manipulated` vs ~0.58 on money).
- The conclusion "the binding constraint is the target, not the features."

Those numbers are **correct as measured**. What is wrong is treating them as
evidence about what the deployed strategy faces. On a survivor cohort almost
everything pumps, so the variation being predicted is *how much* it pumps — a
different question from *whether* a launch is worth buying at all.

**Not invalidated:**

- The **label** results. `manipulated` is defined on the same cohort, so
  concentration-vs-label at 0.77–0.80 is a valid within-cohort statement. It is
  still the wrong *objective* (see `ECONOMIC_CHECK.md`), which was already known.
- **Every repair-track result.** Nothing in the audit repair, the lifecycle
  identity, the reconciliation gate, the entity-graph capture or the RPC
  measurements depends on cohort composition.
- The **structural** findings: service hubs masquerading as coordination hubs, the
  free RPC's ~1 request/second ceiling, the deployment's redundancy.

## The consequence for the plan

**No model trained or evaluated on this cohort can answer the deployed
question** — "of the launches we see, which are worth buying?" The cohort contains
none of the tokens that make that question hard.

That is a stronger statement than "the labels are proxies", and it means the
research track's next real step is not a better feature, or a bigger RPC budget,
or the entity graph. It is **a cohort that includes the tokens that die on the
curve**, which this project can only get from its own forward collection or a
source that does not pre-select graduates.

It also explains, without appeal to any feature, why the brief's proposed filters
measured so similarly: on a population where nearly everything pumps, nearly any
plausible activity measure orders the survivors about equally well.

## Method

- Cohort composition: 45,609 pre-tapes, 45,792 post-tapes, 41,470 labels;
  `labels ⊆ post` verified exhaustively, not sampled.
- Peak multiples: `tmp/_entry_timing_target.py`, 2,999 tokens parsed from
  `pre_migration_tx`, peak taken from each candidate entry instant, entry price
  taken as the first print after that instant.
- Book comparison: `MEMORY.md` §9a — 2 of 137 closed tickets reached 4×.
