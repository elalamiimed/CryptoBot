# The families against the ACTUAL objective: they add nothing

Three rounds of family measurement used targets that were not the project's
objective. This one uses the closest available thing to it — and the answer is
negative.

Probes: `tmp/_families_tape_labels.py`, `tmp/_families_witness_target.py`.

## Two corrections to my own earlier claims

**1. The frame's labels are MELT's, not the tape rule's.** Round 18 said the
project's tape rule was "already wired" and used it. It is wired in *code*
(`train_gates_real.py` `label_definitions`), but the frame this work measures on
carries MELT's columns. Verified exactly:

| check | agreement |
| --- | ---: |
| stored `rug_label` == (`melt_min_ratio` ≤ 0.2) | **1.0000** on 40,031 rows |
| stored `pump_label` == (`melt_return_ratio` > 0) | **1.0000** on 40,031 rows |

**2. The 85 % tape 4× rate is not my discovery.** Round 16 presented it as new.
`train_gates_real.py` line 791 already documents it, and already names the fix:

> "the raw tape calls a 4x on 85 % of tokens whose hour it covers ... so a peak
> label without the witness labels the splice, not the market. Requiring both
> drops the base rate to ~2.7 %, which is what a real 4x-or-nothing exit can act
> on."

So the project had the finding **and** the correction. I re-derived a known result
and reported it as a discovery, which is the second time this track has done that
(the funder graph in round 9 was the first). **Lesson recorded: search the
codebase's own comments before treating a measurement as new.**

## The measurement that was missing

Round 18 established two rug targets exist and must not be conflated. The same is
true of the **pump** target, and worse: a tape-only peak label is a splice
artefact at an 85 % base rate. The usable definition is `peak_witnessed` — the tape
must show the spike **and** MELT's independent trace must confirm it.

The part the frame can express is the witness: **`melt_return_ratio ≥ 3.0`**.

| target | n | positives | base rate |
| --- | ---: | ---: | ---: |
| `y_witness_4x` (`return_ratio ≥ 3`) | 4,279 | **130** | **3.04 %** |
| `y_witness_up` (`return_ratio > 0`) | 4,279 | 826 | 19.3 % |

(That 3.04 % lines up with the code comment's "~2.7 %", which is a good sign the
definition is right.)

## Result: no incremental signal

Chronological split (60/40), deployed features as the baseline:

| target | baseline (17 deployed) | families only | + families | **Δ** |
| --- | ---: | ---: | ---: | ---: |
| `y_witness_4x` | **0.6126** | 0.5106 | 0.6054 | **−0.0072** |
| `y_witness_up` | 0.6320 | 0.5336 | 0.6395 | **+0.0075** |

- **On the 4× witness the families make it marginally WORSE.**
- **On the up/down witness they add +0.0075** — indistinguishable from noise.
- **Alone they are worse than the deployed set on both** (0.51 and 0.53 against
  0.61 and 0.63). The families are not a substitute for the deployed vector, let
  alone an improvement on it.

Univariate, on the same target, nothing exceeds **0.585**.

## Why this contradicts the earlier rounds, and which is right

Rounds 7–15 found the tape-computed concentration and activity families reaching
**0.77–0.80** — and those were measured against **MELT's label**. Against the
rulebook-matching objective they reach **0.51–0.61** and add nothing.

Both are true. What the earlier numbers were mostly detecting is **MELT's label
construction**, not the economic outcome the gate is supposed to predict. That is
precisely the failure mode `MEMORY.md` §20j recorded ("the label was not the
money"), now measured on the target that matters and with the answer being
negative rather than promising.

## What this does and does not settle

**Does:** for this cohort, with these features, the brief's proposed families add
no incremental value over the deployed vector on the objective the pump gate is
actually fitted to. Feature engineering within these families is not where the
headroom is.

**Does not:** it is one cohort (Dec 2024 – Feb 2025) and it is **still
survivor-conditioned** — 4a.18 stands, and the witnessed target here is built from
MELT's trace, so it inherits that selection. It also uses only the *witness half*
of `peak_witnessed`, because the frame carries no post-window price for the tape
half; the true definition is stricter still. And 130 positives / 50 test positives
means the 4× column is underpowered — which is why the honest reading is "no
detectable increment", not "a precisely-measured zero".
