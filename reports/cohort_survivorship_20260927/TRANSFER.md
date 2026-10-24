# Does the survivorship problem break the ORDERING, or only the base rates?

Round 16 (`cohort_survivorship_20260927/FINDING.md`) established that the MELT
cohort is **migrated-only** — `labels ⊆ post` holds exactly, so every economic AUC
measured on it describes tokens that already graduated. The open question it left
was whether that is fatal or merely a calibration problem:

- If the **ordering** transfers (features rank tokens the same way in both
  populations), a model trained on survivors still ranks real launches usefully
  and only its **probabilities** are wrong.
- If the ordering does **not** transfer, a model trained on survivors is being
  scored on a population it will never trade, and nothing short of a different
  cohort fixes it.

This measures which. Probe: `tmp/_survivorship_transfer.py`.

## Method

The 4,139 tapes with **no MELT label** are a different population, and they can be
labelled **from the tape** so that both cohorts are scored identically. Outcomes
are computed for both: the peak multiple after the observation window, and whether
the token ever fell to ≤20 % of its early price.

| cohort | n | peak ≥4× | `nadir ≤ 0.2` positives | median peak | median tape span |
| --- | ---: | ---: | ---: | ---: | ---: |
| survivors (labelled) | 4,145 | 85.0 % | **33** | 11.02 | 355 s |
| unlabelled | 415 | 78.3 % | **1** | 9.60 | 46,438 s |

## A correction to my own first run

The first version compared **both** targets and reported a **50 % direction
agreement (10/20)**. That number is **not usable**, and the reason is visible in
the table above: the `nadir ≤ 0.2` target has **33 positives** in one cohort and
**1** in the other. Every AUC computed on it is noise, and its direction "flips"
carry no information. Reporting 50 % would have been a strong claim built on a
target with a **single positive example**.

Re-run on the well-powered target only:

## The result: direction largely transfers, magnitude does not

Target `peak ≥ 4×` — 3,524 positives (survivors) against 325 (unlabelled):

| feature | survivors AUC | dir | unlabelled AUC | dir | move |
| --- | ---: | --- | ---: | --- | ---: |
| `hhi` | 0.709 | lower | 0.773 | lower | 0.064 |
| `top3` | 0.679 | lower | 0.782 | lower | 0.103 |
| `top10` | 0.690 | lower | 0.773 | lower | 0.083 |
| `n_holders` | 0.700 | higher | 0.654 | higher | 0.046 |
| `n_wallets` | 0.724 | higher | 0.630 | higher | 0.094 |
| `organic_tx` | 0.686 | higher | 0.619 | higher | 0.066 |
| `unique_buyers` | 0.725 | higher | 0.653 | higher | 0.071 |
| `organic_volume` | 0.517 | higher | **0.912** | higher | **0.395** |
| `ofi` | 0.759 | lower | 0.522 | lower | **0.237** |
| `buyer_breadth` | 0.754 | lower | 0.557 | **higher** | 0.197 |

- **Direction agreement: 9 of 10 (90 %).** A feature that is associated with a
  bigger peak on survivors is, nine times out of ten, associated with a bigger peak
  off them too.
- **Mean |AUC move|: 0.136. Max: 0.395.** The *magnitudes* are not stable at all.
  `organic_volume` is near-useless on survivors (0.517) and the strongest feature
  off them (0.912); `ofi` does the reverse.
- **One genuine flip:** `buyer_breadth` (0.754 "lower" → 0.557 "higher"), though at
  0.557 the unlabelled reading is close to no information.

## What this means

**Better news than round 16 implied, and worse than "just recalibrate".**

- The survivorship problem is **not primarily an ordering problem** — the sign of
  each relationship mostly survives, so a survivor-trained model would still tend
  to rank real launches in the right direction.
- It is **also not merely a calibration problem**. A 0.136 mean shift and a 0.395
  worst case mean a **feature set chosen on survivors is not the feature set that
  works off them**. Selection — not just thresholding — is what breaks.

**The practical rule:** a feature's value must be *measured on the population it
will trade*, and the survivorship cohort cannot stand in for that. This is a
sharper statement than "the labels are proxies" and it applies to the whole
research track's economic half.

## Limits, stated plainly

- The unlabelled cohort here is **415 tokens** — those among the 4,139 unlabelled
  tapes for which family features were computed (the family cache covers ~10.7 % of
  tapes). It is **not verified to be representative** of non-migrators, and it may
  be selected in an unknown direction.
- The `nadir` target is unusable on this data at any sensible threshold: only
  33/4,145 and 1/415 positives at ≤0.2, and 466/4,145 and 48/415 even at ≤0.8. Any
  future rug label here needs a different construction.
- One cohort, one period (Dec 2024 – Feb 2025), no costs or exits.
- The survivor cohort's own 85 % `peak ≥ 4×` rate is itself the round-16 artefact;
  what is being compared is how features order *within* each cohort, not the rates.
