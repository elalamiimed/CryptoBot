# LOCAL EVIDENCE — v9 research: the graduated (69k-MC / pumpswap) cohort vs the launch-pool cohort

**Task:** `task-1` ("v9 local evidence: forward-return study of the graduated (69k MC / pumpswap)
cohort vs the launch cohort"). **Agent:** `data-evidence`. **Written:** 2026-10-19 (Asia/Shanghai).
**Status:** complete. **Companion deliverables in the same directory:** `ONLINE_RESEARCH.md` (task-2,
external evidence; this file deliberately cross-checks it), `VERIFICATION.md` (task-4, engine build),
`local_evidence.json` (machine-readable numbers produced by the scripts below).

**Scope of this file:** this repo's own recorded decisions (read-only) + paced GeckoTerminal (GT)
OHLCV history + DexScreener (DS) current state. It does **not** modify the engine, the live runs, the
model, or any policy. All numbers below are reproducible with the commands in §9.

---

## 0. Executive answer (blunt)

**Q1 — "Do coins that reach ~69k MC (migration) reach higher afterwards?"**
The pump is real but it is mostly **already over by the time v9's 300 s window closes**.

* Measured from the **first recorded post-migration print**, the pool's first-hour candle-high
  reached a median **1.90×** the first price (IQR 1.39–3.80, n=75); confirmed genuine graduates
  **1.97×** (n=22). So yes, graduates do move after migration.
* Measured from the **decision mark** (the moment v9 can buy: median 480 s after pool birth,
  `decision_target_ts`), the forward peak within 24 h is a median **1.33×** for all sampled pumpswap
  tickets (n=59), and **1.38×** for the tradeable subset (cap ≥ $1k, n=46, 95 % CI 1.28–1.93).
  Hit rates for cap ≥ $1k: **≥1.5× 45.7 %**, **≥2× 32.6 %**, **≥4× 15.2 %**; 30 % collapse to
  ≤0.2× within 24 h; only 10 % still print a trade at +24 h.
* For the **confirmed-genuine** subset (launch-pool-backed or curve-read `migrated`, n=22) the
  decision-time forward peak is a median **0.85×** (IQR 0.38–1.28): after the decision mark they
  *typically never trade above the decision price again*. Their post-decision nadir is a median
  **0.25×** — the dump-after-migration pattern the online task describes.

**Q2 — "Are they more legit?"**
**Yes on participation/integrity, and the local record measures it clearly; no on forward P&L evidence.**

* On the 300 s decision window (tickets with a complete tape), pumpswap pools vs pump-fun launch
  pools: distinct wallets p50 **93 vs 9** (MW p≈2e-92), tx count **184 vs 39**, top-3 buyer-volume
  share **35 % vs 85 %**, volume HHI **0.075 vs 0.335**, reserve **80 vs 12 SOL**, in-window
  drawdown-from-max **0.85 vs 0.58**, `p_rug` **0.576 vs 0.626** (p≈7e-14), `p_pump` 0.396 vs 0.404
  (p=0.006). The graduated venue is a genuinely thicker, less concentrated market.
* **But** "pumpswap venue" is a **weak graduation proxy**: 55.6 % of v8's pumpswap decisions are
  mints that do not even end in `pump` (not pump.fun launches), and only **25.0 %** carry a
  curve read of `migrated`. This matches the online finding (~1 in 10 PumpSwap pools historically
  genuine; 451k curve-skip pools, 99 % dev-emptied). Do **not** read `dex == pumpswap` as "graduated".
* And "more legit" ≠ "safer to buy late": the confirmed-genuine cohort is *more* likely to be in
  post-migration decline at the decision mark (nadir p50 0.25× in 24 h).

**Q3 — "Does the literal $69k MC gate select a better subset than the migration event?"**
**No measurable forward edge, and it selects a worse downside profile.**

* At SOL ≈ $103.42 (measured live), pump.fun graduation is a **410.8 SOL FDV** event = **$42.5k**;
  $69k is the same event only at **SOL ≈ $168**. So `--min-market-cap-usd 69000` at today's price is
  a **667 SOL FDV / +62 % post-migration momentum filter**, exactly as SPEC §0 says.
* In the forward sample, **22.7 %** of all pumpswap tickets (17/75, 95 % CI 14.7–33.3 %) and
  **25 %** of v8's tape-complete pumpswap tickets (6/24) had a decision-time cap ≥ $69k.
* Gate-pass vs gate-fail, from the decision mark: 24 h forward peak p50 **1.24× vs 1.38×**
  (median difference −0.13, MW p=0.30 — no edge), hit ≥1.5× **26.7 % vs 45.5 %**, collapse ≤0.2×
  **46.7 % vs 22.7 %**, 24 h nadir p50 **0.43× vs 1.13×** (MW p=0.011 — significantly worse).
  The gate buys tokens that are already a median **3.3× the migration cap** (gate pass cap p50
  $149k = 1,360 SOL) and then dumps them.
* Cross-check from the current state (DexScreener, n=184 still-listed v8 pumpswap pools): current
  cap p50 **$9.8k**, i.e. **below** the $42.5k structural migration cap; only 66/184 (35.9 %) are
  currently above the structural cap and 45/184 (24.5 %) above $69k.

**The v9 design's own measurement machinery is the biggest risk (measured, not speculation):**

* **48.1 % of v8's pumpswap tickets died on the 300-print GT trade-page cap** (`tape_incomplete`:
  the endpoint has no backward pagination, so the first 300 s of a *hot* migrated pool cannot be
  collected). That is **70.6 pumpswap decisions/day** adopted and then dropped (v8 ran 268 in
  1.855 days). So **v9 cannot even quote more than ~51 % of its own decided pumpswap tickets** —
  the pre-registered acceptance threshold "quote-obtained share ≥ 70 %" is arithmetically
  unreachable if the denominator includes the tape-dropped tickets.
* Adverse selection: the tape-dropped (hot) half does **better** forward than the half v9 would
  keep — 24 h forward peak p50 **1.38× vs 1.10×** (difference +0.28, 95 % CI 0.07–0.94; 1 h
  difference +0.31, p=0.047). v9 as designed systematically trades the *slower* migrated pools.

**One-line verdict:** *Worth a PAPER test this week as a measurement run — the pumpswap population
is observably different from the launch population and that difference is worth quantifying — but
not because the design is expected to be profitable. As specified (300 s window on GT's 300-print
tape cap, $69k = +62 % momentum filter), it will measure a biased, late slice of the population;
the pre-registered quote-coverage seal will likely trip before any strategy conclusion is valid.*

---

## 1. What was measured, and how

### 1.1 Data sources

| source | role | volume / quota |
|---|---|---|
| `strategy_runs/paper_segment_v8_20261017/decisions_log.csv` etc. (snapshotted 2026-10-19 12:22 local to `tmp/v9_research/snapshot/`) | all cohort definitions + in-window features + shadow outcomes | v8 1,752 decisions (2026-10-17 07:46 → 10-19 04:14 UTC, 1.855 d); v5 5,641 (4.061 d); v6/v4/v3 963. 8,356 total |
| `coin_database.sqlite3` (read-only, `mode=ro`) | discovery/pool composition cross-checks | 11,408 pools, 13,780 discoveries |
| **GeckoTerminal** `/networks/solana/pools/{pool}/ohlcv/minute?aggregate=5&limit=1000&before_timestamp=…` | forward 5-min candles: 1 h / 6 h / 24 h peaks, drawdown, survival | **116 calls**, 15 s pacing, 1× HTTP 429 (auto 25 s recovery), 1 timeout; v8's own `gt_penalised` stayed **1 → 1** |
| **DexScreener** `/latest/dex/tokens/{≤30 mints}` | wide current state (still listed? current cap/liquidity/24 h volume) + weak launch-pair signature | 82 calls, ~2,437 mints |
| GeckoTerminal `/networks/solana/tokens/{mint}/pools` | launch-pool verification: does a pump.fun pool exist with an earlier `pool_created_at` than the PumpSwap pool? | 20 calls (+6 for the M cohort) |

Quota calibration (measured this session, `tmp/v9_research/rate_probe.json`): 6 calls at 5 s spacing
gave `200,200,200,200,429,200` — a **global** IP budget of roughly 4–5 req/min shared with the
running v8. This is why the forward sample is 111 tickets, not the 80+80 target (see §7).

### 1.2 Cohort definitions

| tag | definition (local record) | v8 n | pooled n (v3–v8) |
|---|---|---|---|
| **P** (v9 universe) | `dex == "pumpswap"` — the pools v9's `--entry-venue-allow pumpswap` would adopt | **268** | 851 |
| **M** | `curve_status == "migrated"` at the decision (engine read the curve as complete) | 98 | 207 |
| **C** (control) | `dex == "pump-fun"` — the launch-pool population v8 trades | **951** | 5,714 |
| **O** | every other venue (meteora-*, raydium-*, …) | 435 | 1,715 |

Note the overlap: 67 of v8's 268 P rows are also M (pumpswap pool + curve read migrated). Cohort
tables in §3 treat M as taking precedence for the "migrated" count; the P-only numbers in §3.1
exclude those 67.

### 1.3 Measurement definitions (forward, all from the decision mark)

* `t_dec` = `decision_target_ts` (the moment the 300 s window closed / v9 would decide), median
  pool age 406 s for P rows, 444 s for C rows.
* `entry` = close of the **last fully-completed 5-min candle** at `t_dec`; if none, the **open** of
  the candle containing `t_dec` (no look-ahead: the containing bucket's close would include
  post-decision trades — this bug was found and fixed during the study).
* `peak_1h/6h/24h` = max **close** in the window / entry (primary, robust). Candle **high**-based
  peaks are kept as an upper bound: one GT candle contained a 53,733× mispriced print inside a rug
  bucket, so close-based is the defensible measure.
* `nadir_24h` = min **close** / entry over 24 h; `collapse ≤ 0.2×` = share of tickets whose nadir
  is ≤ 0.2×; `survival_24h` = any candle in +24 h ± 4 h; `end_24h` = last close ≤ +24 h / entry.
* `cap_decision_usd` = entry × 1e9 tokens (all these launches are 1e9 supply); `cap_decision_sol` =
  cap / SOL-USD at that decision (hourly SOL/USDC history, 400 candles); cap at the historic
  $69k-defining SOL = `cap_decision_sol × 168`.
* **birth arm** (only possible for P/M, where the fetched window reaches pool creation): the same
  peaks measured from the **first recorded post-migration trade** — the best-case "buy at migration"
  benchmark. It is not the migration seed price: a liquidity add is not a trade, so the first print
  can already be away from it.
* Candles are USD (verified against `/pools` attributes: OHLCV close == `base_token_price_usd`).

### 1.4 Sample (systematic, time-covering, deterministic)

Sample rule: within each run and cohort, de-duplicate by mint and take the i-th of n equally spaced
rows over decision time (all of the segment is covered; no seed needed). `sample.json` lists every
ticket. Planned 75 P (45 v8 + 30 v5), 30 C (25 v8 + 5 v5), 6 M. Delivered: 111 tickets with 110
OHLCV reads (1 timeout), 0 selected-for-cause; per-ticket rows are in `local_evidence.json`.

---

## 2. The arithmetic of "$69k" at today's SOL

| quantity | value | basis |
|---|---|---|
| pump.fun graduation FDV | **410.8 SOL** | 85 SOL raise, 206.9M of 1B supply seeds the PumpSwap pool (online task, academic curve constants) |
| SOL/USD measured live (2026-10-19) | **$103.42** | GT `quote_token_price_usd` of the probe pool; hourly SOL/USDC history used to convert per-decision caps |
| graduation FDV at today's SOL | **$42,485** | 410.8 × 103.42 |
| graduation FDV at SOL ≈ $168 | **$69,014** | this is where the user's "$69k" comes from |
| `--min-market-cap-usd 69000` at today's SOL | **667.2 SOL FDV** | 69,000 / 103.42 |
| gate as a multiple of the migration event | **+62.4 %** | 667.2 / 410.8 |
| same gate at SOL ≈ $105 (Lead's figure) | 657 SOL = +60 % | 69,000 / 105 |

Every ticket in `local_evidence.json` carries the cap in all three units (SOL FDV, USD at current
SOL, USD at the historic $168 SOL). The one-sentence version for the docs: **"$69k" is the 410.8
SOL migration cap re-priced at SOL $168; at SOL $104 it is +62 %, a momentum filter.**

---

## 3. The local record

### 3.1 v8's realised pumpswap universe = v9's operating cohort

Measured on the 268 v8 pumpswap decisions (1.855 days):

| metric | value |
|---|---|
| pumpswap decisions / day | **144.5** (15.3 % of all v8 decisions; pump-fun launch = 512.8/day) |
| share of mints that are pump.fun mints (`…pump` suffix) | **44.0 %** |
| curve read at decision | `migrated` 25.0 %, `unreadable` 25.7 %, blank/not read 49.3 % |
| **tape-complete** (300 s window fully captured) | **51.1 %** |
| tape-page-saturated flag | 69.4 % |
| **dropped with `tape_incomplete`** (page cap lost the launch prints) | **48.1 % = 70.6 decisions/day** |
| quote requested | 67/268 = 25.0 % |
| **quote OK when requested** | **67/67 = 100 %** |
| model approved (`intended_action == buy`) | 50/268 = 18.7 % |
| bought | 5 |

The 48 % tape-cap casualty is structural, not a feed hiccup: GT `/trades` returns at most 300 rows
newest-first and has no backward pagination (`TAPE_CAP = 300` in `live_paper_trader.py`). A migrated
token's PumpSwap pool is typically *busier* than a fresh launch curve, so its first 300 s are
exactly what the page cap cannot serve. **The hotter the migration, the more likely v9 drops it.**

### 3.2 Refusal funnel and the quote-coverage criterion

v8's funnel on pumpswap tickets (log fields `reason` / `entry_rejection_reason`):

| stage | n | note |
|---|---|---|
| adopted + decided | 268 | = 144.5/day |
| dropped `tape_incomplete` | 129 | 48.1 % — page cap |
| dropped `quiet` (<5 trades) | 3 | |
| reached curve read | 136 | 50.7 % of all decisions |
| refused `entry_progress_unknown` | 69 | the v8-only 3 % curve-progress gate; **v9 sets this to 0** |
| quote requested → OK | 67 → 67 | 100 % quote success when requested |
| v8 bought | 5 | (2.7/day) |

Implication for the SPEC §5 acceptance seal "quote-obtained share of decided pumpswap tickets
≥ 70 %": because the tape cap removes 48 % before the quote is ever requested, the **maximum
achievable share is ~51 %** under the current data source. If "decided" means every decision row
(including `tape_incomplete` skips), the v9 segment would trip its own infrastructure kill switch
on day 1–2. If it means "tickets that reached the decision machinery", measured quote success is
~100 %. **The acceptance criterion should be restated before the run** (Lead/engine decision).

A crude v9 buys/day estimate from the same funnel: 144.5 × 0.507 (tape) × ~0.25 (MC ≥ $69k among
tape-complete) × 0.368 (v8 model approval among tape-passing) ≈ **6.7 model-approved/day**, but only
**5 of v8's 50 model-approved pumpswap tickets survived the quote-stage gates** (impact cap 23,
price disagreement 18, concentration 4), so the realistic range is **1–7 buys/day** and the
pre-registered "≥ 5 buys/day" is not safe.

### 3.3 "More legit": pumpswap vs launch population on the decision window

Complete-tape subset only (P 261, C 4,764 pooled; medians, Mann-Whitney two-sided):

| feature | pumpswap P | pump-fun C | MW p |
|---|---|---|---|
| distinct wallets in window | **93** | **9** | 2e-92 |
| trades in window | 183.5 | 39 | 2e-60 |
| top-3 buyer volume share | 0.351 | 0.852 | 2e-54 |
| volume HHI | 0.075 | 0.335 | 4e-48 |
| reserve (SOL, where quoted) | 79.9 | 11.6 | 8e-18 |
| total window SOL volume | 35.4 | 9.6 | 8e-06 |
| `p_rug` model probability | 0.576 | 0.626 | 7e-14 |
| `p_pump` model probability | 0.396 | 0.404 | 0.006 |
| in-window drawdown-from-max | 0.853 | 0.578 | — |
| in-window price change (last/first) | +2.1 % | −12.3 % | 2e-06 |
| `dev_sold_at_s` observed rate | 0 % (0/207 P rows read) | 41 % (2,367/5,714) | — |

Reading: the migrated venue is a **much thicker, much less concentrated market** — the opposite of
the one-wallet launch pools v8 trades. The rug-probability model gives it a slightly better score;
pump probability is indistinguishable. Caveat: this table is conditioned on tape completion, and
P's complete-tape rate is only 34 % pooled / 51 % v8, so it describes the *measurable* pumpswap
pools, not all of them (the dropped hot ones are measured in §5.4 and are not worse).

### 3.4 The migrated-at-decision cohort (M) — why the user's observation was right

n=207 pooled / 98 v8. By construction `curve_status == "migrated"`: the engine looked at a token
that had **already completed the curve**, but often through the **frozen pump-fun launch pool**:
`dex` = pumpswap 131, pump-fun 57, others 19. Evidence that this is a broken place to price:

* tape complete **100 %** (launch pools are quiet — they stopped printing at migration);
* quote OK **92 %**; but the refusals are dominated by the *mismatch* between the frozen tape and
  the venue quote: `entry_impact_cap` 45, `entry_price_disagreement_low` 44,
  `entry_unknown_depth` 37 — i.e. the engine's mark and the real market are not the same thing.
* v8 bought 7 of 207 (3.4 %); model approval 11.1 %.

Forward from the decision mark for the 6 sampled M tickets (measured on the PumpSwap pool, which is
where the token actually trades): 24 h peak p50 **0.21×**, 5/6 collapse ≤0.2×, 24 h nadir p50
0.033×. This is consistent with SPEC §9: pricing a migrated token off its frozen launch pool is
pricing a dead market. v9's pumpswap-venue discovery is the correct fix for *that* specific defect.

### 3.5 Why the local shadow record cannot answer the forward question

536 shadow outcomes exist (v5 401, v8 65, …), but only **0.7 % (v5) / 6.2 % (v8) have a complete
1 h observation**, and 437/466 rows with data are censored for `print_silence`: the engine keeps
polling the **adopted pool**, which goes silent at migration/death, so `peak_mult` is truncated at
the last print and the median collapses to 1.0. **The shadow cohort cannot be used to say "graduated
coins do/don't reach higher"** — this is the honest reason the whole forward question needs GT
history. (The ≤10 complete rows are suggestive: migrated cohort p50 1.70×, n=4 — far too small, and
selected by shadow admission rank.)

---

## 4. Wide current state (DexScreener, 2,437 mints, 2026-10-19 12:34 local)

DexScreener has no OHLCV, so this section answers **survival and current state**, not peaks.
Coverage caveat: DS drops pairs over time; 42 % of the 2,437 mints had no pair at query time, and
"no pair" is **missing data**, not proof of death.

* **Graduation rate of the launch cohort v8 actually saw:** of 951 pump-fun launch decisions
  (age ~300 s), **49 (5.2 %, Wilson 3.9–6.7 %) now have a PumpSwap pair**; restricting to the 744
  mints DS still indexes, 6.6 % (5.0–8.6 %). So ≈ **1 in 15–19 of the launch bets v8 makes ever
  graduates** (within ≤2 days). The online research's platform-wide 1-in-58 is the same story with
  a different denominator. This is the quantitative answer to "most coins do not reach 69k": among
  v8's adopted-at-300 s launch population, **~5 % ever migrate**.
* Where both pairs are still visible the migration delay was short (n=6, p50 **192 s**, min 152 s) —
  instant graduations exist, but n is too small to characterise the delay distribution.
* **Current state of v8's pumpswap cohort** (268): 193 still listed on PumpSwap; current cap p50
  **$9,770** (p25 $1,853, p75 $67,895); 66/184 above the $42.5k structural cap, 45/184 above $69k;
  only 56/193 (29 %) have >$1k liquidity; median 24 h volume $28k. **Most of the cohort is below the
  migration cap today** — the distribution is heavily right-tailed (p90 cap $171,876).
* **Current state of the migrated-at-decision cohort** (98): 75 still listed; current cap p50
  **$2,017**; 5/71 above $69k.

---

## 5. Forward returns (GeckoTerminal history, n=111)

Full per-ticket data in `local_evidence.json` → `forward_study`. `n` is always reported; CIs are
bootstrap 95 % for medians and Wilson for hit rates. **Censoring:** 44 % of P and 47 % of C tickets
have no 1 h of forward candles (pool silent), so peak fields have smaller n than the cohort size;
P/M tickets that reached pool creation also carry the birth arm.

### 5.1 Pumpswap (v9 universe) vs launch-pool control — from the decision mark

| group | n / n with 24 h data | 24 h peak p50 [bootstrap CI] | ≥1.5× | ≥2× | ≥4× | collapse ≤0.2× | nadir p50 | survival 24 h |
|---|---|---|---|---|---|---|---|---|
| **P all** (cap≥$0) | 75 / 59 | **1.33** [1.16, 1.75] | 40.7 % (24/59) | 28.8 % | 13.6 % | 28.8 % (17/59) | 1.02 | 10.7 % |
| **P cap≥$1k** (tradeable) | 61 / 46 | **1.38** [1.28, 1.93] | 45.7 % (21/46) | 32.6 % | 15.2 % | 30.4 % (14/46) | 1.08 | 9.8 % |
| P genuine-confirmed | 22 / 22 | **0.85** [0.43, 1.19] | 22.7 % (5/22) | 18.2 % | 13.6 % | 45.5 % (10/22) | 0.25 | 27.3 % |
| P weak-proxy (non-pump / unconfirmed) | 53 / 37 | 1.63 [1.33, 2.20] | 51.4 % | 35.1 % | 13.5 % | 18.9 % (7/37) | 1.19 | 3.8 % |
| **C launch control** | 30 / 19 | **0.84** [0.50, 1.00] | 5.3 % (1/19) | 0 % | 0 % | 10.5 % (2/19) | 0.81 | 7.1 % |
| M (migrated-at-decision, PumpSwap follow) | 6 / 6 | 0.21 | 0 % | 0 % | 0 % | 83.3 % | 0.03 | 66.7 % |

Cohort test (P all vs C all, 24 h peak median difference): **+0.50, 95 % CI [0.22, 0.98],**
MW p=0.0037; the 1 h difference is +0.55 [0.23, 0.94], p=0.004. **The graduated venue does reach
higher multiples than the launch population after the bot's decision time** — the strongest
positive evidence in this study. Caveats: (i) C's forward path is censored at migration/death
(47 % no 1 h data), so C is *not* a fair "what the launch token could have become" benchmark;
(ii) the P/C difference is largest for the *non-pump-mint* pumpswap pools, i.e. it partly measures
"curve-skip pools pump afterwards", which is exactly what the online research warns about;
(iii) P's cap is 10× C's, so this is a multiple comparison, not a risk-adjusted one.

Per-run robustness (same measurement, 24 h peak p50): v8 P tradeable **1.63×** (n=32) vs v8 C
**0.76×** (n=16); v5 P tradeable 1.35× (n=14) vs v5 C 0.76× (n=2, too small). The v8 slice — the
one matching current market conditions and the clean quota regime — shows the widest separation.

### 5.2 Genuine graduates vs weak proxies (label triangulation)

Labels are three independent local signals, reported separately and combined as tiers
(`local_evidence.json` → `P_label_classification`):

| signal | P sample (75) | full v8 P cohort (268) |
|---|---|---|
| pump.fun mint suffix (`…pump`) | 25 (33.3 %) | 44.0 % |
| curve read `migrated` | 15 (20.0 %) | 25.0 % |
| GT launch-pool verified (a pump.fun pool exists and predates the PumpSwap pool) | 19 looked up → **7 launch-backed** (36.8 % of the 19; all 7 were pump-suffix mints) | n/a |
| decision-time cap consistent with the 410.8 SOL migration cap (structural cap inside the first 5-min bucket's price range) | 31 (41.3 %) | n/a |
| **genuine-confirmed tier** (launch-backed OR curve-migrated) | **22 (29.3 %)** | ≥25 % (197 unread) |

For the 19 successful launch-lookups: **7/10 unconfirmed pump-suffix mints had a pump.fun launch
pool (launch-backed), 0/9 non-pump mints did**. One non-pump token (AE) did have pump.fun pools but
they post-date its PumpSwap pool by 5.3 h, so it is not launch-backed; the `…pump` suffix is a good
but not perfect launchpad proxy. The full v8 cohort shows
**44 % pump-mint / 25 % curve-migrated / 50 % no curve read at all** — so "how many of these are
genuine graduates" cannot be resolved beyond a floor of ~25 %; the online estimate (~1 in 10
PumpSwap pools genuinely graduated) is compatible with our data because our denominator is the
*feed-offered* pumpswap pools, where every fresh migration appears as a "new pool".

Forward, the split is stark: genuine-confirmed reached *higher from birth* (1 h birth-peak p50
**1.97×**) but from the decision mark they did **not** reach higher (p50 **0.85×**, collapse 45.5 %,
nadir 0.25×) — i.e. the genuine graduates' move happens **inside the 5–8 minutes between migration
and the decision mark**, and the decision mark is usually the top. Weak proxies (curve-skip-style)
do the opposite: +11.5 % from birth to decision, then a median 1.63× *further* within 24 h. That is
a pump-and-dump pattern, not a graduation-quality signal.

### 5.3 The entry timing: what the 300 s window costs

| group | birth→decision time p50 | price change birth→decision p50 (IQR) | 1 h peak from first print p50 | 1 h peak from decision p50 |
|---|---|---|---|---|
| P all | 480 s | **+6.6 %** (0.0 % … +20.9 %) | **1.90×** [1.63, 2.54] | 1.31× [1.11, 1.63] |
| P genuine-confirmed | 475 s | **−13.3 %** (−92.4 % … +10.9 %) | **1.97×** [1.48, 3.06] | **0.84×** [0.37, 1.08] |

Interpretation: for the average pumpswap ticket, the decision mark is already a median +6.6 % above
the first recorded post-migration trade; the pool's best 1 h print *from birth* is 1.90×, but the
best *from the decision mark* is 1.31× — roughly the first moves are consumed by the observation
window. For the genuine subset the pattern is qualitatively worse: the first-hour peak from birth
is 1.97× but from the decision mark it is 0.84× — the typical genuine graduate is already past its
post-migration peak when v9 can buy. (Birth arm caveat: the first *recorded trade* can already be
away from the 410.8 SOL migration seed; it is a best-case benchmark, not the exact migration price.)

### 5.4 The tape-cap stratum: v9 keeps the slower half

| stratum (v8 definition applied to the sample) | n | 24 h peak p50 | 1 h peak p50 | ≥2× | collapse ≤0.2× | cap at decision p50 |
|---|---|---|---|---|---|---|
| **P tape-page-saturated** (v9 would DROP: 300-print cap) | 50 | **1.38×** [1.26, 1.91] | 1.38× | 30.0 % (12/40) | 30.0 % | $40.4k |
| **P tape-complete** (v9 would KEEP) | 36 | **1.10×** [0.80, 1.28] | 1.06× | 25.0 % (7/28) | 25.0 % | $9.8k |

Median difference (saturated − complete): 24 h **+0.28** [0.09, 0.94], 1 h **+0.31** [0.13, 0.94]
(MW p=0.047 at 1 h). The pools v9's own 300-print tape cap excludes are the ones that move more
after the decision mark. This is a **design-level adverse selection**, and it compounds the entry
timing problem: the survival set is simultaneously later and slower.

### 5.5 The $69k gate: pass vs fail

| group | n | 24 h peak p50 | ≥1.5× | ≥2× | collapse ≤0.2× | nadir p50 | cap at decision p50 (SOL FDV) |
|---|---|---|---|---|---|---|---|
| **cap ≥ $69k at decision** | 17 | 1.24× [0.19, 1.93] | 26.7 % (4/15) | 20.0 % | 46.7 % (7/15) | **0.43×** | $149,411 = **1,360 SOL** |
| cap < $69k | 58 | 1.38× [1.16, 1.88] | 45.5 % (20/44) | 31.8 % | 22.7 % (10/44) | **1.13×** | $16,438 = **150 SOL** |

The gate-pass group has no forward-peak advantage (MW p=0.30) and a **significantly worse drawdown**
(nadir MW p=0.011; collapse 46.7 % vs 22.7 %). It is selecting tokens already at a median 3.3× the
migration cap. In other words, the literal 69k filter is a **late-momentum filter**, and the local
evidence gives it no forward edge — this is the single most important answer to Q3.

Cap distribution at the decision mark (three units) for the v9 universe (P, cap≥$1k, n=61):
USD p25/p50/p75 = **$16.7k / $41.2k / $80.2k**; SOL FDV = **152 / 399 / 772 SOL**; USD at historic
$168 SOL = **$25.5k / $67.0k / $129.7k**. So the median tradeable pumpswap ticket sits just below
the $69k gate in "old-SOL dollars" — the gate is a real filter, as SPEC §9 said (only 22.7 % pass),
but passing it selects the worse tail.

### 5.6 Gate sizing, per day

From the v8 funnel: 144.5 pumpswap decisions/day → **73.3/day** pass the tape cap → ~25 % of those
have a decision-time cap ≥ $69k (**~18/day**, 95 % CI from 6/24 ≈ 8–32/day) → v8 model approval
among tape-passing 36.8 % (**~6.7/day** model-approved) → only 10 % of those survived v8's
quote-stage gates (impact cap / price disagreement / concentration): **~1–3 buys/day realistic**,
with a best case of ~7/day if MC-passing tickets quote cleanly. The SPEC §5 acceptance "≥ 5
buys/day" is therefore at risk from the tape cap alone, before any strategy question is asked.

---

## 6. Verdict on testing v9 this week

**Worth a paper test — as a measurement run, not as a profit thesis.** The design asks a question
this repo cannot answer otherwise: does the post-migration population behave differently from the
launch population? The answer is **yes, measurably** — thicker participation, far lower
concentration, better in-window drawdown, and a 24 h forward peak distribution shifted **+0.50×**
(p=0.004) above the launch control. That is a real population difference worth one week of paper
data, and v9 is the cheapest way this project can observe it.

**But the design as specified has three measured defects that will limit what the week can prove:**

1. **The $69k admission, at today's SOL, is a +62 % momentum filter with no measured forward edge
   and a worse drawdown profile.** It will systematically buy the late tail. If the goal is
   "graduation cohort", the flag should be ~$42–43k (410.8 SOL × SOL) or expressed in SOL; the
   launcher pinning 69,000 is the user's literal request, so run it — but pre-register that the
   gate is a momentum filter and read the result as such.
2. **The 300 s window + GT's 300-print tape cap structurally drops the hotter half of its own
   universe** (48 % of v8 pumpswap tickets; ~71/day), and the dropped half performs better forward.
   Before the week is judged, either the tape source/collection is fixed (paginated or
   prefetch-anchored) or the quote-coverage seal must be restated (max ~51 % under the current
   implementation, not 70 %).
3. **Entry is late relative to the event**: median 480 s after pool birth, by which time the
   confirmed-genuine cohort has typically already printed its post-migration peak (1 h peak from
   birth 1.97× vs 0.84× from the decision mark). The week will therefore measure a *late-entry*
   strategy, not "the graduation trade". That is a valid experiment, but its result cannot be read
   as evidence that graduation itself is/isn't profitable.

**What would falsify the case for continuing after the week:** admitted cohort's 24 h forward peak
p50 ≈ 1.0× with collapse ≤0.2× ≥ 40 %, or quote coverage < 50 % for two consecutive days (the
pre-registered infrastructure kill), or ≤ 2 buys/day after day 3. The measured expectations above
suggest the second is the most likely failure mode.

---

## 7. Honesty / limitations (read before quoting any single number)

1. **The forward sample is smaller than the task target** (75 P + 30 C + 6 M = 111, not 80 + 80).
   The GT key-less quota is IP-global (~4–5 req/min measured: `200,200,200,200,429,200` at 5 s
   spacing) and is shared with the running v8, which must not be harmed (its `gt_penalised`
   counter stayed 1 before/after; the whole forward fetch used 116 calls at 15 s pacing with one
   429). Everything is reported with n and CIs; sub-group n of 5–22 cannot support strong claims.
2. **Survivorship/selection in P**: the frames are "pumpswap pools the discovery feed offered and
   v8 adopted" (≤6 watchers, ≤3 adoptions/cycle), not all PumpSwap pools. Adoption is roughly
   time-ordered but not random.
3. **Censoring in C**: 47 % of control ticks have no 1 h forward candle and the launch pool stops
   printing at migration/death. C's forward numbers are a *lower bound* on what a launch token
   could become; the C/P difference is therefore not a clean "launch vs graduate" causal gap.
4. **Pumpswap ≠ graduated** (55.6 % of v8's pumpswap decisions are not pump.fun mints at all; only
   25 % have a readable `migrated` flag). Labels are triangulated and reported per signal; the
   "genuine-confirmed" tier is small (n=22).
5. **5-min candles** only: +5/+15/+60 min prices are ±5-min bucket approximations; close-based peaks
   are robust to the mispriced wick we found, high-based peaks are reported only as an upper bound.
6. **The local shadow cannot measure forward peaks** (≤6 % complete 1 h observations; print
   silence at migration/death). Any earlier "shadow p50 1.70×, n=4" reading should not be repeated
   as evidence.
7. **DexScreener current-state coverage decays** (42 % of mints had no pair at query time) and its
   absence is missing data, not death.
8. **BOOST regime (online task, §7):** since ~29–30 Jul 2026 pump.fun injects migration liquidity
   as market buys within ~5 min post-migration. That overlaps v9's window and can inflate first-
   minutes move sizes/volumes relative to older regimes; treat §5.1's early-minute numbers as
   regime-specific, and do not compare them to 2024–25 studies.

---

## 8. What this file adds to the other two deliverables

* **`ONLINE_RESEARCH.md`** establishes the mechanism (410.8 SOL FDV, 1-in-58 graduation, 1-in-10
  genuine PumpSwap share, 99 %-dev-emptied curve-skip pools, BOOST regime). This file **measures the
  local equivalents**: 5.2 % of v8's launch decisions eventually migrate; 44–25 % of its pumpswap
  tickets are pump.fun-mint/curve-confirmed (not 1 in 10, but the local feed is migration-heavy and
  the denominator differs; unclassifiable 50 % is the honest gap); and the forward/drawdown outcomes
  of each label tier. Where they could conflict, the local record and the external record agree on
  direction (venue ≠ graduation; most launch coins never graduate; post-migration flow is
  dev/sniper-dominated).
* **`VERIFICATION.md`** covers the engine build; the only build-relevant findings here are the
  tape-cap casualty rate and the ~51 % maximum quote coverage (see §3.2), which affect the
  acceptance/kill criteria rather than the code.

---

## 9. Reproduce

```powershell
# local record (no network)
.\.venv\Scripts\python.exe -X utf8 -B tmp\v9_research\local_cohorts.py
.\.venv\Scripts\python.exe -X utf8 -B tmp\v9_research\local_legitimacy.py
.\.venv\Scripts\python.exe -X utf8 -B tmp\v9_research\build_sample.py

# network: paced GeckoTerminal (quota-shared with v8; ~20 min at 15 s/call)
.\.venv\Scripts\python.exe -X utf8 -B tmp\v9_research\probe_api.py     # 5-call semantics probe
.\.venv\Scripts\python.exe -X utf8 -B tmp\v9_research\rate_probe.py    # 6-call quota calibration
.\.venv\Scripts\python.exe -X utf8 -B tmp\v9_research\fetch_gt.py --max-calls 120 --interval 15
.\.venv\Scripts\python.exe -X utf8 -B tmp\v9_research\fetch_launchpools.py

# network: cheap wide current state (DexScreener, ~2 min)
.\.venv\Scripts\python.exe -X utf8 -B tmp\v9_research\fetch_ds.py

# analysis + deliverable JSON
.\.venv\Scripts\python.exe -X utf8 -B tmp\v9_research\analyze_ds.py
.\.venv\Scripts\python.exe -X utf8 -B tmp\v9_research\analyze_forecasts.py
.\.venv\Scripts\python.exe -X utf8 -B tmp\v9_research\assemble_evidence.py
```

Deterministic except the network steps, which are resume-safe JSONL (`raw/gt_raw.jsonl`,
`raw/ds_state.json`, `raw/launch_pools.jsonl`). Environment: Windows, Python 3.13 venv,
`-X utf8 -B`; all local reads are read-only; the running v8 was never touched (its dashboard
`/api/book` counters were sampled before/after every network phase).

---

*Files: this report; `local_evidence.json` (machine-readable, per-ticket + per-cohort); scripts in
`tmp/v9_research/`; raw network captures in `tmp/v9_research/raw/`.*
