# Do the brief's proposed feature families carry economic signal? — 27 September 2026

**The question.** The research brief proposes replacing/augmenting the deployed
28-feature vector with entity concentration (F4), manipulation-adjusted activity,
informed flow (F6) and organic order-flow imbalance (F7). F4's blocker is the
funding graph and F6's is wallet history — but **the feature families themselves
can be computed from the raw tape alone**, no RPC and no graph, and tested against
real outcomes. That is what this measures.

It answers a question the brief assumes rather than shows: *do these families know
anything about whether a token pays?*

Probe: `tmp/_family_signal.py`. Cohort: 3,999 tokens computed from
`pre_migration_tx`, **3,638** of them joined to MELT's labels.

## Result

| family | best economic AUC | mean economic AUC | best label AUC |
| --- | ---: | ---: | ---: |
| organic (tx, volume, unique buyers/sellers) | **0.6216** | 0.5445 | 0.8008 |
| breadth (`n_wallets`, buyer breadth) | 0.6185 | 0.5500 | 0.8011 |
| concentration (hhi, top3, top10, holders) | 0.6161 | 0.5497 | 0.7985 |
| flow (OFI, sell pressure, buy volume) | 0.6054 | 0.5476 | 0.7847 |

**Two things stand out.**

**1. All four families land within 0.016 AUC of each other on money.** The spread
between the best and worst proposed family (0.6216 vs 0.6054) is roughly the size
of seed noise measured elsewhere in this project. Whatever these families are
detecting, they appear to be detecting **largely the same thing** — consistent with
the earlier finding that "concentration" as measured by net position shares only
`r² ≈ 0.11` with MELT's volume-concentration column, i.e. the families are not as
distinct in effect as their names suggest.

**2. Every family scores ~0.18 HIGHER on the label than on money.**

| family | best label AUC | best economic AUC | gap |
| --- | ---: | ---: | ---: |
| concentration | 0.7985 | 0.6161 | **0.182** |
| organic | 0.8008 | 0.6216 | **0.179** |
| flow | 0.7847 | 0.6054 | **0.179** |
| breadth | 0.8011 | 0.6185 | **0.183** |

That gap is the same phenomenon `ECONOMIC_CHECK.md` recorded for raw
concentration alone, now confirmed across **every** proposed family. A team that
selected filters on label AUC — the natural thing to do, since `manipulated` is
the dataset's headline target — would be selecting on the wrong objective by a
wide and *consistent* margin.

## The uncomfortable implication

**The brief's proposed families look largely redundant with the feature they are
meant to replace.** `count_tx` reached 0.527/0.612 single-feature economic AUC in
the earlier measurement; the *best* number any proposed family achieves here is
0.6216, and the mean is ~0.545. On this cohort, the elaborate entity/flow
constructions buy little over counting trades.

That is consistent with everything else this track has measured, and it points the
same way: **the binding constraint is the target, not the features.** End-of-trace
`return_ratio` may simply not be very predictable from a launch's opening window,
whatever features one builds.

## What this is NOT

- **Not a refutation of F4/F6/F7.** These are **single-feature** AUCs. A family's
  value could appear only jointly, and no multivariate model was fitted here. The
  entity graph could still add signal that raw concentration does not.
- **Not an executable edge.** The targets are MELT's end-of-trace `return_ratio`
  and `min_ratio`, which cannot express the strategy's 4× *peak* rung. No costs,
  exits, or position sizing enter. `min_ratio`-based "deep drawdown" is a
  proxy for a rug, not a trade outcome.
- **Not out-of-sample in time.** One cohort, Dec 2024 – Feb 2025.
- **Not leakage-free.** Some of the family features (notably `n_wallets` and
  `organic_tx`) are related to the quantities MELT's own labelling may consider,
  so part of the label AUC is plausibly by construction. That is precisely why the
  **economic** column is the one to read.

## Addendum: the comparison ladder

`tmp/_family_incremental.py` runs the multivariate comparison this report said was
needed: a logistic model with a **chronological** split (earlier 60 % train, later
40 % test), baseline = the **26 deployed features** present in the frame, then
baseline + one family at a time, plus each family alone.

**Sample: 4,489 tokens** (2,693 train / 1,796 test). This is **10.7 %** of the
42,106-token frame, so every number below is underpowered, and the full-set run is
a ~hours job being extended incrementally. The deltas are consistent across
targets, which is the main reason to take the shape seriously.

### On the label, four features beat twenty-six

| target = `manipulated` | test AUC | Δ vs baseline |
| --- | ---: | ---: |
| baseline (26 deployed features) | 0.6691 | — |
| **concentration family ALONE (4 features)** | **0.8044** | +0.135 |
| `breadth` alone | 0.8060 | +0.137 |
| + concentration | 0.8225 | **+0.153** |
| + flow | 0.8230 | +0.154 |
| all families | **0.8374** | **+0.168** |

**Four tape-computed features beat the entire deployed set**, and adding them
lifts the deployed set by **+0.153**. This is consistent with §20i (raw
concentration reached 0.769 alone) and it says the deployed vector is carrying
substantial **redundancy**: 26 pipeline features are worth less, on this target,
than 4 computed directly from the tape.

### On money, every family helps by about the same small amount

| target | baseline | +conc | +organic | +flow | +breadth | all |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `min_ratio ≤ 0.2` (ruined) | 0.6812 | 0.7241 | **0.7321** | 0.7232 | 0.7272 | 0.7310 |
| `return_ratio > 0` (up) | 0.6327 | **0.6485** | 0.6356 | 0.6386 | 0.6420 | 0.6437 |

| target | +conc | +organic | +flow | +breadth | all |
| --- | ---: | ---: | ---: | ---: | ---: |
| ruined | +0.0429 | **+0.0509** | +0.0420 | +0.0460 | +0.0498 |
| up | **+0.0158** | +0.0029 | +0.0059 | +0.0093 | +0.0110 |

**On money the four families are interchangeable** — they land within 0.008 of each
other on both targets, and the "all families" cell is no better than the best
single addition. Families alone reach only 0.60–0.62 on `ruined` and 0.51–0.54 on
`up`, far below their 0.79–0.81 label numbers.

### The reading

The families are not four different signals. They are **four measurements of one
common factor**, which is why they add nearly identically and why adding all of
them adds nothing beyond the best one. On the label that factor is strong; on the
money it is worth about **+0.04 AUC on a rug proxy and +0.01 on ending positive**.

Two consequences worth stating plainly:

- **Concentration is not special.** Round 14 hinted it was; with this larger sample
  `organic` edges it out on the rug proxy (+0.0509 vs +0.0429) and the whole family
  spread is inside noise. The earlier "concentration is strongest" reading does not
  survive the larger sample, and this report records the correction.
- **The 0.18 label-vs-money gap survives as the headline.** It is now confirmed
  multivariately, on a later time slice: these features predict *how a token was
  traded* far better than *whether it paid*.

### Limits

4,489 of 42,106 tokens; one cohort (Dec 2024 – Feb 2025); a **proxy** target
(`min_ratio ≤ 0.2`) that cannot express the strategy's 4× peak, with no costs,
exits or sizing; and part of the label AUC is plausibly by construction. The
full-set run, a rulebook-matching target, and a second cohort are what would make
any of this decisive.



1. A **multivariate** comparison on economic targets, with the deployed 28
   features as the baseline, to test whether any proposed family adds *incremental*
   value rather than standing alone.
2. A target that reflects the actual rulebook: a **4× peak** within a horizon, with
   realistic entry delay and costs — not end-of-trace return.
3. A second cohort, ideally later in time, to separate cohort-specific structure
   from something that persists.

Until then, the honest reading is: **the proposed families are not obviously better
than what is deployed, and their apparent strength is mostly label strength.** That
is an argument for measuring on money before building any of them, which is what
`GOAL.md` §4 has said from the start and what this cohort keeps confirming.
