# Does concentration carry economic signal? — correcting round 7

**Round 7 reported that raw-wallet concentration reaches AUC 0.686 against MELT's
`manipulated` label and read that as a large increment worth acting on. This
report qualifies that result, and the qualification matters more than the number
did.**

Two independent checks were run afterward, and both cut against the round-7
reading.

## Check 1 — the association is real, not an artefact of MELT's features

Round 7 used MELT's *own* pre-built concentration columns, and MELT also produced
the label, so the result could have been circular. Concentration was therefore
recomputed **independently from the raw tape** (`pre_migration_tx/*.jsonl`),
using only signed per-wallet token sums: a wallet's holdings are its net position
across the window, and only positive nets count as ownership.

| | vs `manipulated` |
| --- | ---: |
| independently-computed `hhi` (net position) | **0.769** |
| independently-computed `top10` | 0.765 |
| independently-computed `top3` | 0.747 |
| independently-computed `top1` | 0.729 |
| MELT's own `volume_hhi` (round 7) | 0.633 |

So the association is **not** an artefact of MELT's pipeline — it is *stronger*
when the feature is built independently. Good news for the feature.

But the two measures are not the same variable, which is itself informative:

| pair | Pearson | Spearman |
| --- | ---: | ---: |
| my `hhi` vs MELT `volume_hhi` | **0.332** | 0.391 |
| my `top3` vs MELT `top_3_buyers_volume_pct` | 0.380 | 0.362 |
| my `n_holders` vs MELT `unique_buyers` | **0.014** | 0.072 |

Only ~11–15 % of variance is shared (`r²`). "Concentration" is not one variable:
**net-position concentration and volume concentration are largely different
measurements**, and the project's existing column is the weaker of the two
against this label.

## Check 2 — the label is not the money, and the project already knew

This is the finding that changes the conclusion. Against the **economic**
targets (`return_ratio` — did the trace end up; `min_ratio` — deep drawdown):

| feature | AUC vs `manipulated` | AUC vs `return_ratio > 0` | AUC vs `min_ratio ≤ 0.2` |
| --- | ---: | ---: | ---: |
| `hhi` (mine) | 0.769 | 0.540 | 0.581 |
| `top3` (mine) | 0.747 | 0.545 | 0.577 |
| `top10` (mine) | 0.765 | 0.547 | 0.586 |
| `n_holders` | 0.798 | 0.528 | 0.607 |
| `n_tx` | 0.789 | 0.529 | **0.612** |

**Concentration predicts the label at 0.77 and the money at ~0.54–0.59.** A
filter chosen on label AUC would be chosen on the wrong objective — which is the
same category of mistake this repair track has spent eight rounds removing, in a
new place.

**And MELT's `manipulated` label is anti-predictive of a positive return:**
AUC **0.314** (i.e. 0.686 the other way) for `manipulated = yes` vs
`return_ratio > 0`. Labelled-manipulated tokens are *more likely* to end up
positive, not less. `manipulated` is a statement about how a token was traded,
not about whether it was a bad buy.

**This is not new information to the repository** — `docs/FINALIZATION_STATUS.md`
§3 already recorded that fitting Gate 1 on `manipulated` bought nothing over the
deployed label (mean pnl **+0.13014** vs **+0.13228** at matched capacity, win
rates 60.9 % vs 60.7 %) despite ROC-AUC rising 0.7333 → 0.9108. That document
called the AUC gain "a change of TARGET, not a gain in capability". Round 7
reproduced that mistake by reporting a label AUC as if it were an edge.

## Corrected reading

- **The round-7 number was right and its interpretation was wrong.** Raw
  concentration genuinely carries strong information about *how* a token is
  traded — the independently-built version reaches 0.769, better than anything
  else measured here.
- **It carries only modest information about the economic outcome** (~0.54–0.59),
  and no more than raw transaction count does (0.53–0.61).
- **`n_tx` — the feature this project was inclined to distrust — is the best of
  them against deep drawdown (0.612).** The brief's warning that "transaction
  counts are not necessarily organic activity" is a caution about interpretation,
  not evidence that the count is uninformative.
- **Any F4 filter must be selected on economic outcomes**, not on coordination
  labels, whatever the label's AUC.

## What this does NOT establish

- Not out-of-sample in time: the same Dec 2024–Feb 2025 cohort throughout.
- Not a trading edge: `return_ratio` is end-of-trace and cannot express the
  strategy's 4× *peak* rung; no costs, exits or sizing enter.
- Not a refutation of F4: entity merging could raise concentration's economic AUC
  even though raw concentration's is modest. That is still untested and still
  needs the funder graph.
- Not a claim that MELT's label is bad — `FINALIZATION_STATUS.md` shows it is
  economically meaningful (42.1 % vs 60.7 % win rates). It is a *proxy*, and the
  point is that it is a proxy for a different question than P&L sign.

## Consequence for the plan

F4's advisory question is answered in two parts, and they point the same way:
**build the filter only if it can be evaluated on money.** The measured case for
the entity graph is now weaker than round 7 implied in economic terms and
unchanged in mechanism terms — merging wallets raises concentration for
coordinated tokens, but raw concentration's *economic* AUC is only ~0.58, so the
headroom a graph could win is bounded by how much of the remaining gap it closes.
That is testable the moment funding data exists, and not before.
