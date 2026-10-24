# Solana Memecoin Research — 1000x winners, pump-and-dump dynamics and fraudulent-token detection

**A research-only repository.** This project studies the behaviour of Solana memecoins: the
launch-and-pump life cycle, the price paths of extreme winners, the fingerprints of fake or
rug-pulled launches, and the graduation/migration economics of pump.fun-style launchpads.
It is **not a trading bot**, it contains **no wallet, signing or transaction-submission code**,
and it makes **no profitability claim**. All trading activity discussed in these reports was
**paper-only** (a simulator); no live capital was deployed, and none of the results below is
presented as evidence of a tradeable edge.

This edition contains the research record only: reports, derived datasets, data provenance,
trained-model artifacts and the standalone scripts needed to reproduce the headline winners
study. The paper-trading engine and everything that existed to run, account for, audit or
promote it have been removed from the public edition.

**Licence:** reports, data and model artifacts are **CC BY-NC 4.0**; the scripts in `scripts/`
are **MIT**. See [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md) (which also carries the MELT
dataset attribution). **Author:** elalamiimed · **Repository:**
<https://github.com/elalamiimed/CryptoBot> · **Contact:** open an issue on GitHub.

---

## 1. Purpose

Memecoins are the largest-volume, least-studied corner of on-chain crypto markets. Public
narratives ("most memecoins are rugs", "1000x coins are luck") are rarely tested against large,
traceable data. This repository is an empirical study of that market from four angles:

1. **The winners.** What distinguished the 598 Solana tokens that reached ≥1000x in 2025–26 from
   listed non-winners — and what do their price paths look like after the pump?
2. **The fraud.** How do fake / rug-pull tokens look *before* the dump, and how much can a
   classifier know from launch-window on-chain behaviour? (Label data: the MELT dataset.)
3. **The launchpad economy.** What happens to tokens that *graduate* from a bonding curve and
   migrate to a DEX? Is migration a legitimacy signal? Does post-migration flow pay late buyers?
4. **The methodology.** Why are these questions so hard to answer honestly? (Survivorship,
   label proxies, censoring, tiny samples, power, and the difference between predicting a
   *label* and predicting *money*.)

A navigable, one-row-per-artifact index — what each file measured, its key numbers and its
caveats — is in [FINDINGS.md](FINDINGS.md). This README summarises the corpus; FINDINGS.md is
the reference table a reader should use to navigate it.

### What is NOT in this repository

* **No paper-trading engine, execution, accounting, sizing, promotion or readiness code**, and
  no run launcher (`run_*.ps1`), no engine tests, and no paper-book run directories, databases,
  logs or dashboards (`strategy_runs/`, `coin_database*.sqlite3`, `tmp/` hidden state).
* **No engine-dependent analysis/training scripts** that imported that code: gate training
  (`train_gates_real.py`, `temporal_validation.py`), the per-token atomic/markout scans, replay
  and capacity tools, and the paper-book measurement code. The artifacts those scripts produced
  *are* included under `reports/` and `data/`, and the training protocol that produced the model
  artifacts is documented in `docs/TRAINING_VALIDATION.md`.
* **The 89 GB MELT raw corpus and the 1.735 GB feature frame are not redistributed.** They must
  be re-downloaded from MELT; they are pinned by the hashes in `data/melt/` and
  `data/melt/provenance/`.
* **The 608-token forward-collected raw trade tape** (`real_solana_trades.csv` in the original
  project) is not redistributed; its coverage, and why the chronological trainer refused it, are
  documented in `docs/DATA_COLLECTION_PLAN.md`.
* **Large per-token scan outputs** (`atomic_scan.json`, `markout_scan.json`, policy/capacity
  replay scans, 75–112 MB each) are not shipped; the analysis summaries derived from them are in
  `reports/`. Nor are any local PDFs of the reviewed papers (only summaries and SHA-256
  manifests in `docs/`), API keys, credentials or raw API caches beyond the winners snapshots.
* **No repository in this edition can sign or submit a transaction.** The environment
  deliberately excludes wallet/signing libraries (see `requirements.txt`).

### A note on the reports as historical documents

The reports under `reports/` and `docs/` are the original internal working documents, kept
verbatim so the record is auditable. They were written while the paper-trading engine was still
present, and some of them cross-reference material that is **not** part of this edition — for
example path prefixes from the old layout (`strategy_reports/…` now lives under `reports/`),
`tmp/` probe folders, `MEMORY.md`/`GOAL.md`/`FINALIZATION_STATUS.md`, engine launchers and the
v9 design doc (`docs/V9_GRADUATION_SEGMENT.md`). Those referents were part of the engine-era
project; their absence does not change any number reported here. Two reports
(`reports/v9_research_20261019/TEAM_SUMMARY.md` and `VERIFICATION.md`) carry a public-repository
note at the top saying the same thing.

---

## 2. Research questions

| # | Question | Primary artifacts |
|---|---|---|
| RQ1 | Can launch-time attributes separate 1000x winners from listed non-winners? How fast is the signal knowable? | `reports/winners_study_report.md` |
| RQ2 | What does the price path of a 1000x token actually look like — time to multiple, pre-ATH drawdowns, exit feasibility? | `reports/winners_study_report.md` §"Price path of the winners" |
| RQ3 | Which pre-migration on-chain behaviours separate high-risk (rug/manipulated) launches from low-risk ones? | `docs/RESEARCH_NOTES.md`, `reports/atomic_manipulation_20260928/`, `reports/concentration_vs_coordination_20260927/`, `reports/bundle_probe_20260928/` |
| RQ4 | Do concentration, coordination-graph evidence and atomic bundling carry information about *manipulation* — and is that the same as information about *profit*? | `reports/concentration_vs_coordination_20260927/ECONOMIC_CHECK.md`, `reports/family_signal_20260927/`, `reports/family_decisions_20260928/` |
| RQ5 | Do graduated / migrated tokens reach higher after migration, and is the migrated venue structurally "more legit"? | `reports/v9_research_20261019/` |
| RQ6 | How large are the survivorship and censoring biases of the available cohorts, and what can still be concluded? | `reports/cohort_survivorship_20260927/`, `reports/cohort_representative_20260927/` |
| RQ7 | Is there a measurable executable edge in any of this? | `reports/rung_breakeven_20260927/`, `reports/rung_recovery_20260927/`, `reports/rung_rejection_20260927/`, `reports/hit_rate_cohorts_20260927/`, `reports/trial_registry_20260927/` |

---

## 3. Datasets and collection

All data were collected from public, key-less endpoints, plus the CC BY-NC 4.0 MELT dataset.
Raw third-party datasets are not redistributed; the derived aggregates, provenance hashes,
per-token winners snapshots and model artifacts are.

| Source | Role in the project | Approx. scale |
|---|---|---|
| **CoinGecko** — `/coins/markets` categories `solana-meme-coins`, `pump-fun`, `/coins/list`, SOL/USD | Winner/control universe: ATH, ATH date, ATL, supply, market cap; keeps dead coins, which limits pure listing-survivorship | **1,370** tokens with an ATH in the era; 1,099 launchpad-born |
| **pump.fun** — frontend `api-v3/coins/{mint}`, swap API 12-h candles | Launch-time metadata (creation time, socials, description, king-of-the-hill, graduation, creator) and full price paths | 12-h candles, latest ≈1,000 bars; 335 winners with a path starting at launch |
| **DexScreener** — `/token-pairs/v1/solana/{mint}`, `/latest/dex/tokens` | Earliest pool / venue / graduation time; current cap and liquidity for still-listed tokens | ≈2,437 mints in the v9 forward study |
| **GeckoTerminal** — `/networks/solana/pools/{pool}/ohlcv/minute`, `/tokens/{mint}/pools` | Forward post-migration OHLCV (1 h / 6 h / 24 h peaks, drawdown, survival) and launch-pool verification | 116 OHLCV calls in the v9 study; public endpoint serves only the newest ~300 swaps per pool, no backward pagination |
| **MELT** — Hu et al., *MELT: A Behavioral Trace Dataset for High-Risk Memecoin Launch Detection*, arXiv:2602.13480v2; repository <https://github.com/git-disl/MELT> | The main pre/post-migration on-chain corpus: per-token wallet-level pump.fun transactions, plus the authors' labels (`min_ratio`, `return_ratio`, `manipulated`) | **45,609** pre-migration tapes (13.15 GB), **45,793** post-migration first-hour tapes (82.47 GB), **41,470** labelled migrated launches; feature frame **42,106 × 49** |
| **Own forward-collected sample** — free recent-trades collector in the original project | Early attempt at a prospective cohort on live launches | 608 tokens / 551 featured; only 17.76 h over 2 UTC days — too small for chronological validation (documented refusal in `docs/DATA_COLLECTION_PLAN.md`). **The raw tape is not redistributed.** |
| **Shipped per-token winners snapshots** — `data/winners/winners_raw.json`, `winners_universe.json` | Enriched per-token records and the CoinGecko candidate universe, included so the published winners study can be recomputed without re-collecting moving public data | ≈2.4 MB + ≈2.1 MB; collected 2026-09-14 for non-commercial research; subject to provider terms, not an official redistribution of any provider's dataset |
| **Secondary literature** (5 documents reviewed: four papers + one secondary synthesis) | Rug-detection methods, labels and metrics; full PDFs are **not** redistributed | see `docs/SOURCES.md` |

---

## 4. Headline findings

### 4.1 1000x winners and pump dynamics (`reports/winners_study_report.md`)

* **598 of 1,370** enriched tokens reached a peak multiple ≥1000x; 204 listed controls stayed
  below 200x (297 tokens in the 200–1000x band were excluded from the classifier). The top
  winner, fartcoin, peaked at ≈**385,083x** (ATH market cap $2,479.9M).
* Launch-time attributes barely separate winners: median time to king-of-the-hill **5 min vs
  18 min** for controls, time to graduation **8 min vs 61 min**, AI-agent narrative **20 % vs
  11 %**, but socials-at-launch are *less* common among winners (70 % vs 78 %). A
  gradient-boosted classifier with grouped (by creation month) cross-validation reaches
  out-of-fold ROC-AUC **0.602** on launch-time features only and **0.754** once early-life
  (KOTH/graduation timing) is added — against a 74.3 % base rate.
* The pump is **fast and brutal**: winners whose 12-h candle series starts at launch (n = 335)
  reach 1000x at a median **2.5 days**, peak at a median **6.5 days** with a median peak
  multiple of **2,552x**, but experience a largest pre-ATH drawdown of **80 % (optimistic bar
  ordering) / 99 % (pessimistic)**, and are down **99 %** from their ATH today.
* A **30 % trailing stop keeps a winner to the ATH in only 20 % (optimistic) / 7 %
  (pessimistic)** of cases (median exit 153x / 114x); the tail is only capturable with
  cost-recovered moonbags or ladders, not tight stops.
* A separate "speed filter" study finds **no material gain**: buy-all baseline −0.00217
  SOL/ticket (95 % CI −0.00509…+0.00126), and no speed filter clears the study's materiality
  bar (verdict: do not adopt). The result is archived as `data/speed_filter_study.json`.

### 4.2 Fake memecoins and rug detection

* **Labels are proxies.** Using MELT's own labels: `min_ratio` (minimum post-migration price
  over migration price) defines high risk as `<0.3` (34,890 tokens), low risk as `≥0.7`
  (1,878), medium 4,702; `manipulated` is a partly manual judgement (23,584 yes / 11,877 no /
  6,009 unknown). A naive tape reconstruction of `min_ratio` correlates with MELT's at only
  ≈**0.27** (median abs error 0.021; the JSON's own `correlation` field), so "the label" is not
  trivially reproducible.
* **Threshold choice changes the population materially**: `min_ratio ≤ 0.2` (this project's
  rule) labels 24,988 rugs vs 32,167 under the paper's high-risk definition; 4,179
  manipulated-only-high tokens are missed and 3,000 sit in the ambiguous 0.2–0.3 band
  (`reports/rug_threshold_20260927/`).
* **Atomic manipulation is detectable but rare and confounded**: 65.5 % of tokens contain at
  least one same-transaction multi-wallet split (1.72 % of 22.7M swap transactions); fan-out
  appears in 7.6 % of tokens; high-risk tokens actually show *fewer* splits (AUC 0.273) but
  more fan-out (AUC 0.540). Within activity bands the separation collapses — the apparent
  signal is largely trade-count confounded (`reports/atomic_manipulation_20260928/`).
* **Concentration predicts the label, not the money.** Independently reconstructed net-position
  concentration reaches AUC **0.769** against MELT's `manipulated` label, but only
  **0.54–0.59** against economic targets (`return_ratio > 0`, `min_ratio ≤ 0.2`). MELT's
  `manipulated` flag is in fact **anti-predictive** of a positive return (AUC 0.314) — the label
  describes *how* a token was traded, not whether it was a bad buy
  (`reports/concentration_vs_coordination_20260927/`).
* **The four proposed feature families are one factor.** Organic, breadth, concentration and
  flow families all land within **0.016 AUC** of each other on money (best ≈0.62), while each
  scores ≈**0.18 higher on the label**; against the rulebook-matching "witnessed 4x" target
  (3.04 % base rate) they add **nothing** over the deployed features (−0.007 AUC)
  (`reports/family_signal_20260927/`). The explicit promote/do-not-promote record is in
  `reports/family_decisions_20260928/family_decisions.json`.
* **Conformal abstention fails on real data.** On 402 real outcomes, split-conformal prediction
  sets have coverage *below* nominal at every α (pump coverage gap down to −0.83) and make **0
  decisive** predictions — a warning against treating model probabilities as calibrated
  (`reports/conformal_real_20260927/`).
* The curated literature review (`docs/RESEARCH_NOTES.md`) records the published baselines:
  MELT reports MLP AUPRC **0.573** (random 0.259); "Catching the Rug" reports XGBoost MCC
  **0.356** on PumpFun; "Detecting rug pulls in DEXes" reports XGBoost accuracy **87.6 %**,
  precision 85.5 %, recall 90.7 % on Ethereum data — each with its own label, population and
  split caveats.

### 4.3 Launchpad graduation and migration (`reports/v9_research_20261019/`)

* Graduation is rare and regime-dependent: **1 in 58** pump.fun launches graduated over
  Nov-2025→Oct-2026, with monthly cohorts from **1 in 144 to 1 in 32**; an independent academic
  estimate is **0.63 %** (Sept-2025); median time-to-graduation **4.4 min**. Graduating is not
  succeeding: **~43 %** of graduates still trade in week 5 vs **~1 %** of non-graduates.
* Migrated (PumpSwap) pools are structurally different from launch pools: 300-s decision
  windows show distinct wallets p50 **93 vs 9**, top-3 buyer share **35 % vs 85 %**, volume HHI
  **0.075 vs 0.335**, pool depth **80 vs 12 SOL**, and model rug probability **0.576 vs 0.626**
  (p≈7e-14). Genuine graduation pools are hard to rug: **98 %** never had SOL withdrawn
  (external evidence), while **451,402** fake "curve-skip" PumpSwap pools in 8 months were
  **99 % dev-emptied** (median 12 min) — so "listed on PumpSwap" is not proof of graduation
  (only ≈1 in 10 such pools was).
* **The post-migration pump is mostly pre-entry.** From the first recorded post-migration
  print, the first-hour candle-high median is **1.90×** (genuine graduates 1.97×); from the
  decision mark (median 480 s after pool birth) the 24 h forward peak is a median **1.38×**
  (n = 46, 95 % CI 1.28–1.93) — and **0.85×** for confirmed genuine graduates (n = 22), i.e.
  typically a **post-migration dump** by the time a late buyer can act.
* The literal **$69k market cap** gate is not the migration event: at SOL ≈ $103, graduation
  FDV is **$42.5k**, so $69k is a **+62 % momentum filter**. Measured, it shows **no forward
  edge** (peak 1.24× vs 1.38×, p = 0.30) and a **worse downside** (collapse ≤0.2× in 46.7 % vs
  22.7 %, p = 0.011).
* Measurement limits are documented as findings: **48.1 %** of migrated-pool tickets died on
  GeckoTerminal's 300-print cap (and the dropped hot half performs *better*: 24 h peak p50
  1.38× vs 1.10×), so any late-entry study is biased toward slower pools.

### 4.4 Market structure, cohorts and the honest bottom line

* **The MELT cohort is a sample of survivors, not of launches.** All 41,470 labelled mints have
  a post-migration tape (`labels ⊆ post`, verified exhaustively), i.e. every token in the
  training/evaluation cohort already graduated. On that cohort the peak multiple from launch is
  median **13.19×** and **93.6 %** reach 4x; from 360 s it is still **72.0 %** — versus **1.5 %**
  realised (2/137) 4x fills in this project's paper book. Entry timing cannot explain that gap;
  the population can (`reports/cohort_survivorship_20260927/`).
* Forward markouts on 44,862 MELT tokens: mark coverage **99.7 %** at 1 h; median mark falls
  from **0.728** (300 s) to **0.094** (1 h) while the median peak rises to **2.25×**. The
  all-token 4x hit rate is **26.0 %**, but of the 31.4 % of tokens that peak ≥4x only **36.7 %**
  are still above 1× at the end and their median end value is **0.27×** — peak ≠ profit
  (`reports/markouts_20260928/`).
* **No demonstrated edge.** On the paper books the measured 4x hit rate was **0/11** bought vs
  **1/77** declined (CIs overlap; **11,389** tokens/arm would be needed, ≈64 measurement days),
  and break-even math at a 1 % ticket requires a **11.7–14.2 %** 4x rate against an observed
  **1.14 %** (1/88). The trial registry counts **6 distinct trials over 11 run directories** —
  recorded after the fact — so the books were a search, not one confirmatory test
  (`reports/rung_breakeven_20260927/`, `reports/rung_recovery_20260927/`,
  `reports/rung_rejection_20260927/`, `reports/hit_rate_cohorts_20260927/`,
  `reports/time_to_resolve_20260927/`, `reports/trial_registry_20260927/`).

---

## 5. Methodology notes

* **Case-control design** (winners vs listed controls) with a deliberately excluded ambiguous
  200–1000x band; non-launchpad tokens are reported separately because their launch market cap
  is unknown (only a CoinGecko lower bound on the multiple).
* **Grouped cross-validation**: folds are grouped by creation month, so a month cannot appear in
  both train and test. Reported metrics are out-of-fold; per-feature importance/gain is reported
  alongside.
* **Temporal validation for supervised models**: rows are sorted by launch time; every training
  row whose label window (`label_end`) reaches the validation window is purged; hyperparameters
  and early stopping are tuned on early development folds only; the final chronological block
  is evaluated without fitting, early stopping or threshold search (protocol in
  `docs/TRAINING_VALIDATION.md`; the implementation depended on the removed engine and is not
  shipped).
* **Uncertainty**: Wilson intervals for rates; bootstrap CIs for means/medians; Mann-Whitney for
  median differences; permutation nulls where the sample is small (e.g. 400 permutations for
  the atomic fan-out signal); rule-of-three/upper-bound reasoning where the minority class is
  tiny.
* **Power and pre-specification are treated as results**: minimum-blocks and time-to-resolve
  calculations, a trial registry and explicit "not measurable" verdicts are part of the record
  (`reports/minimum_blocks_20260927/`, `reports/time_to_resolve_20260927/`,
  `reports/trial_registry_20260927/`).
* **Label proxies are named as proxies**: MELT's `min_ratio`/`return_ratio`/`manipulated` and
  the project's own tape labels are all price/behaviour-based; "predicting a label" and
  "predicting money" are measured separately because they diverge by ≈0.18 AUC.
* **Survivorship diagnostics are mandatory**: cohort composition is verified
  (`labels ⊆ post` tape), cohort representativeness is reweighted and reported, and censoring
  in every paper book is quantified before any hit rate is quoted.

---

## 6. Limitations (read before citing anything here)

1. **Survivorship.** The winner universe is conditioned on a CoinGecko listing, and the MELT
   cohort is conditioned on migration. Neither is a sample of all pump.fun launches. Academic
   estimates put graduation at ~0.2–0.6 % of launches, and the 2025–26 online measurement found
   1-in-58 cumulative (a different definition and window), so 1000x and even 4x rates reported
   here are upper-bound, conditional quantities.
2. **Labels are proxies.** `manipulated`, "rug", "pump" and 4x are defined by price paths and,
   in MELT's case, partly by manual review. A model scoring 0.77 AUC against a label may be
   scoring 0.54 against money. No fraud ground truth exists in these datasets.
3. **Small samples and censoring.** The paper books graded 11 of 79 buys; the conformal study
   has 8 pump and 33 rug calibration positives; the witnessed-4x target has 130 positives on
   4,279 tokens; the entity-graph capture covered 6 tokens. Most of these analyses are
   underpowered by construction, and say so.
4. **No demonstrated edge.** Every profitability-adjacent measurement is null or negative: speed
   filters do not help, conformal abstention never fires, atomic/entity families reduce realised
   net return when tested, and the hit-rate evidence sits below the break-even hurdle. Nothing
   here is investment advice or a validated strategy.
5. **Regime dependence.** 2024–2026 covers at least two distinct memecoin regimes (post-2024
   mania, 2025–26 rotation, and a pump.fun "BOOST" liquidity regime change from late July 2026).
   Graduation rates, price paths and flow patterns move with SOL/USD and platform rules.
6. **Data access limits.** GeckoTerminal serves only the newest ~300 swaps per pool with no
   backward pagination; the free RPC sustains roughly one request/second; key-less quotas are
   shared per IP. Several studies are biased by these caps, and the bias direction is stated
   where measured (e.g. the tape-dropped "hot half" performs better).
7. **Not every published number was reproducible.** The MELT `min_ratio` reconstruction reaches
   only ≈0.27; the literature review flags unreconciled tables in the source papers; the legacy
   models under `data/models/legacy/` were trained before the chronological-validation fix and
   must be read as historical artifacts, not evidence.
8. **Paper only.** Execution results are simulated with modelled slippage/fees; no live fills,
   wallets or capital are involved, and the removed code means they cannot be reproduced as
   trading results.

---

## 7. Repository layout

```
.
├── README.md                        this file
├── FINDINGS.md                      navigable index: artifact | measured | numbers | caveats
├── LICENSE                          CC BY-NC 4.0 (reports/data/models) + MIT (scripts)
├── NOTICE.md                        MELT attribution, data provenance, third-party notice
├── requirements.txt                 research environment (no wallet/signing libraries)
├── .gitignore, .gitattributes
│
├── data/
│   ├── winners/                     winners_study.json, winners_universe.json, winners_raw.json,
│   │                                winners_1000x.csv, winners_launchpad_all.csv,
│   │                                winners_candles_12h.jsonl.gz  (≈50 MB uncompressed)
│   ├── melt/                        melt_label.csv (+ SHA-256), corpus_files.tsv.gz,
│   │   │                            corpus_totals/fingerprint, frame_meta, frame_sha256,
│   │   │                            pre/post-migration sample hashes, gate_policy_study.json
│   │   └── provenance/              four *.provenance.json model-provenance records
│   ├── models/
│   │   ├── melt_v5_witness/         canonical (chronologically validated) MELT v5 model pair,
│   │   │                            gate_oof.csv, gate_policy_study.json
│   │   └── legacy/                  5 earlier models + root gate_policy_study.json
│   │                                (historical / pre-fix artifacts only)
│   └── speed_filter_study.json      archived result of the speed-filter study
│
├── docs/
│   ├── RESEARCH_NOTES.md            curated review of 5 rug-detection papers (incl. MELT)
│   ├── SOURCES.md                   citation + SHA-256 manifest of the reviewed PDFs
│   ├── DATA_COLLECTION_PLAN.md      data provenance and the training-coverage gate
│   └── TRAINING_VALIDATION.md       chronological validation / evaluation protocol
│
├── reports/
│   ├── winners_study_report.md      the 1000x study (primary report)
│   ├── v9_research_20261019/        graduation/migration research: TEAM_SUMMARY.md,
│   │                                LOCAL_EVIDENCE.md, local_evidence.json, ONLINE_RESEARCH.md,
│   │                                VERIFICATION.md
│   ├── atomic_manipulation_20260928/          atomic split/fan-out/entity scans
│   ├── bundle_probe_20260928/                 same-transaction bundling probe
│   ├── buy_grading_20260927/                  paper-buy grading/censoring
│   ├── cohort_representative_20260927/        graded-cohort representativeness
│   ├── cohort_survivorship_20260927/          survivor-cohort finding (FINDING.md, TRANSFER.md)
│   ├── comparison_ladder_20260928/            realised-return comparison ladder
│   ├── concentration_vs_coordination_20260927/  label vs money (REPORT.md, ECONOMIC_CHECK.md)
│   ├── conformal_real_20260927/               conformal abstention on real outcomes
│   ├── entity_graph_feasibility_20260927/     funding-graph cost/feasibility
│   ├── entity_graph_validation_20260927/      first live funding-graph capture
│   ├── family_decisions_20260928/             promote / do-not-promote record (+ f5b)
│   ├── family_signal_20260927/                the four proposed feature families
│   ├── hit_rate_cohorts_20260927/             4x hit rate by action, with CIs
│   ├── identity_span_20260928/                lifecycle identity + attribution ceiling
│   ├── markouts_20260928/                     forward markouts on 44,862 tokens
│   ├── melt_frame_peek_20260928/              feature-frame shape/provenance peek
│   ├── min_ratio_cross_20260927/              min_ratio candidate cross-check
│   ├── min_ratio_probe_20260927/              min_ratio candidate probe
│   ├── min_ratio_reproduce_20260927/          full min_ratio reproduction attempt
│   ├── minimum_blocks_20260927/               power/minimum-blocks calculation
│   ├── missingness_inventory_20260927/        label/outcome missingness catalogue
│   ├── phase_a4_min_blocks_20260928/          minimum-blocks prespecification
│   ├── rug_threshold_20260927/                rug-threshold sensitivity
│   ├── rung_breakeven_20260927/               break-even hit-rate math
│   ├── rung_recovery_20260927/                rung recovery on the paper books
│   ├── rung_rejection_20260927/               formal rejection of the deployed rule
│   ├── slot_contention_20260927/              buys lost to slot/capacity/quote contention
│   ├── time_to_resolve_20260927/              measurement time-to-resolve
│   └── trial_registry_20260927/               effective-trials registry
│
└── scripts/
    ├── README.md                    what each script does / environment
    ├── winners_collector.py         key-less universe + candle collector
    ├── winners_study.py             case-control study and price-path analysis
    ├── melt_to_csv.py               MELT JSONL → 7-column trade CSV
    └── select_covered_cohort.py     covered-cohort selection
```

`FINDINGS.md` maps every artifact above to its finding and caveat, and is the recommended entry
point after this README.

---

## 8. Reproducing the winners study

The winners study is the most self-contained result and needs only public HTTP endpoints.

```bash
# 1) environment (Python 3.11+)
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
# macOS / Linux:
# . .venv/bin/activate && pip install -r requirements.txt

# 2) run the study on the shipped snapshots.
#    The shipped candle series is gzip-compressed; python -m gzip keeps the input file.
python -m gzip -d data/winners/winners_candles_12h.jsonl.gz

python scripts/winners_study.py \
  --raw data/winners/winners_raw.json \
  --candles data/winners/winners_candles_12h.jsonl
```

The study writes its outputs to the **current working directory**:
`winners_study_report.md`, `winners_1000x.csv`, `winners_launchpad_all.csv`,
`winners_study.json`. Run it from a scratch directory if you do not want copies created at the
repository root. If the `--candles` file cannot be found the script still runs but silently
omits the price-path section, so keep the path correct. The shipped outputs were generated on
2026-09-14; re-running on the shipped snapshots (verified 2026-10-24) reproduces the report and
tables apart from the generation timestamp plus negligible snapshot/runtime nondeterminism in
one row and one logistic-regression AUC.

**Optional: re-collect the universe from public endpoints** (network-bound, rate-limited,
non-commercial research use). This overwrites the shipped per-token snapshots with fresh data,
so results will differ from the 2026-09-14 study:

```bash
python scripts/winners_collector.py \
  --out data/winners/winners_raw.json \
  --universe data/winners/winners_universe.json \
  --candles data/winners/winners_candles_12h.jsonl \
  --workers 4
```

**MELT track.** The MELT dataset must be downloaded separately (~89 GB; see `NOTICE.md`).
`scripts/melt_to_csv.py` converts the pre-migration tapes into the 7-column trade CSV and
`scripts/select_covered_cohort.py` builds the covered cohort whose survivorship effect is
measured in `reports/cohort_survivorship_20260927/`. The training script itself
(`train_gates_real.py`) is **not shipped** because it imported the removed paper-trading engine;
the resulting model artifacts (including out-of-fold predictions and the policy study) are in
`data/models/melt_v5_witness/`, and the training/evaluation protocol is documented in
`docs/TRAINING_VALIDATION.md`. Verify the label file before using it:

```bash
python -c "import hashlib;print(hashlib.sha256(open('data/melt/melt_label.csv','rb').read()).hexdigest())"
# expected: dcfcce188fb352466b76ab8345f79633766c93e96d29729282ab114133fcc09a
```

The speed-filter result (`data/speed_filter_study.json`) is archived for completeness; its
script is not shipped because it consumed the removed engine's out-of-fold file and the small
locally collected raw tape that is not redistributed.

---

## 9. Licence, attribution and citation

**Reports, data and model artifacts — CC BY-NC 4.0.** All research text, reports, figures,
aggregate datasets, provenance records and trained model artifacts in this repository are
licensed under the Creative Commons Attribution–NonCommercial 4.0 International licence. You may
share and adapt them for non-commercial purposes with attribution; commercial use requires
permission. The full terms are in [LICENSE](LICENSE).

**Scripts — MIT.** The Python source in `scripts/` is MIT-licensed; see [LICENSE](LICENSE).

**MELT attribution.** A substantial part of the fake-memecoin / rug-detection work uses the
MELT dataset:

> Hu et al., *MELT: A Behavioral Trace Dataset for High-Risk Memecoin Launch Detection*,
> arXiv:2602.13480v2 (2026). Dataset repository: <https://github.com/git-disl/MELT>.

MELT and its derivatives are **CC BY-NC 4.0**. MELT-derived files redistributed here —
`data/melt/melt_label.csv`, the corpus/frame provenance records, the MELT-trained models and
anything computed from them — remain subject to MELT's licence and must be attributed to the
MELT authors. [NOTICE.md](NOTICE.md) lists every redistributed MELT-derived file, the changes
made to it, and the non-commercial restriction. The 89 GB raw corpus and the feature frame are
not redistributed; they are pinned by hashes and must be re-downloaded from MELT.

**Public market data.** CoinGecko, pump.fun, DexScreener and GeckoTerminal data were collected
from public endpoints under their terms of service; only derived aggregates, model artifacts
and the winners snapshots are redistributed. No API keys or credentials are included.

**Third-party papers.** The five reviewed documents (four papers and a secondary synthesis) are
not redistributed; only summaries and a citation/SHA-256 manifest (`docs/SOURCES.md`) are
included. Cite the originals.

**Model artifacts.** The `.joblib` files are Python pickle-based artifacts: only load them from
a source you trust, because deserialising a joblib file can execute arbitrary code.

**Not financial advice.** Nothing in this repository is investment advice, and no profitability
claim is made or implied. The trading activity discussed in the reports was paper-only
(simulated); no live capital was deployed.

**Citation.**

```bibtex
@misc{solanamemecoinresearch2026,
  title        = {Solana Memecoin Research: 1000x winners, pump-and-dump dynamics and
                  fraudulent-token detection},
  author       = {elalamiimed},
  year         = {2026},
  howpublished = {\url{https://github.com/elalamiimed/CryptoBot}},
  note         = {Research only; no trading edge claimed. Uses the MELT dataset
                  (CC BY-NC 4.0) by Hu et al.}
}
```

Related work to cite alongside this repository: MELT (Hu et al., arXiv:2602.13480), "Catching
the Rug" (Li et al., arXiv:2608.20271), "Detecting rug pulls in decentralized exchanges"
(Kalacheva et al., DOI 10.1016/j.bcra.2025.100336), "Trust Dynamics and Bot-Driven Responses"
(Li et al., WebSci 2025, DOI 10.1145/3717867.3717922).

---

## 10. Contact

Questions about the data, the MELT licence or collaboration: **open an issue on GitHub** at
<https://github.com/elalamiimed/CryptoBot>.
