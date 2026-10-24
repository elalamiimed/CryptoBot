# v9 — team summary (Lead synthesis)

> **Public-repository note.** This report was written while the paper-trading engine was still
> part of the project; references to engine files, run directories and documents
> (`run_paper_segment_v9.ps1`, `docs/V9_GRADUATION_SEGMENT.md`, `tmp/`, `strategy_runs/`) are
> historical — those files are not included in this research-only edition. The research numbers
> and findings below are unchanged.

**Date:** 2026-10-19 (Asia/Shanghai) · **Lead:** `lead` · **Build:** `engine-v9` ·
**Independent verification:** `v9-verifier` · **Local evidence:** `data-evidence` ·
**Online research:** `web-research`

Read in this order: this summary → `docs/V9_GRADUATION_SEGMENT.md` (the engine-era v9 design and
runbook; not included in this edition) → [`VERIFICATION.md`](VERIFICATION.md) →
[`LOCAL_EVIDENCE.md`](LOCAL_EVIDENCE.md) → [`ONLINE_RESEARCH.md`](ONLINE_RESEARCH.md).

---

## 0. Bottom line

* **v8 is still running untouched** (PID 24828, dashboard http://127.0.0.1:8789/) and kept
  making decisions throughout the build and the one 9-minute live pilot
  (1,697 → 1,790 logged decisions in the verification window; +1 buy; pin unchanged).
* **v9 is built, tested and pilot-verified: READY WITH CAVEATS.** It is a *separate* paper
  segment that trades only the **migration (pumpswap) cohort** and only admits a ticket whose
  entry quote shows **market cap ≥ $69,000**. It has not been started — starting it is one
  command (below) and is deliberately left to you because both books share one key-less
  GeckoTerminal budget.
* **Research answer, short:** yes, migrated tokens **do** reach higher *after migration* (first
  post-migration 1 h high median **1.90×**), and the migrated venue is structurally **more legit**
  (93 vs 9 distinct wallets in the window, top-3 share 35 % vs 85 %, 80 vs 12 SOL depth, lower rug
  probability). **But almost all of that move happens before v9 can buy**: from v9's decision mark
  (median 480 s after the pool opens) the 24 h forward peak is median **1.38×**, and for
  *confirmed-genuine* graduates it is **0.85×** — i.e. typically a post-migration dump by then.
* **The literal $69k gate is not the migration event any more.** At today's SOL ($103.42),
  graduation FDV is **$42.5k**; $69k = +62 % above it = a *momentum* filter. Measured, that filter
  showed **no forward-peak edge** (1.24× vs 1.38×, p=0.30) and a **worse downside**
  (collapse ≤0.2× 46.7 % vs 22.7 %, p=0.011).
* **Two measured design risks dominate any result:** (1) 48.1 % of v8's pumpswap tickets died on
  GeckoTerminal's 300-print trade-page cap before a quote, and the dropped hot half performs
  *better*, so v9 as built trades a slower, biased slice and cannot reach its own ≥70 % quote-
  coverage seal; (2) v8 and v9 split one per-IP GeckoTerminal quota (~4–5 calls/min).

---

## 1. What you asked for, and what exists now

| your request | state |
|---|---|
| Only buy at **69k $ MC + migration** | Built. `--entry-venue-allow pumpswap` (adopt only migrated-venue pools), `--graduated-venues pumpswap` (graduation admission: curve `migrated` OR pumpswap venue), `--min-market-cap-usd 69000` (entry-quote cap ≥ $69k; unknown cap is a refusal). Unknown is never a pass. Refusals are priced off tape and shadow-followed. |
| Give up on the **first-5-min** approach | Built. v9 never adopts pump.fun launch pools: the allowlist drops them **before** adoption, so no tape budget or watch slot is spent on them. In the live pilot it dropped 49 offered pools and adopted exactly 5 — all `pumpswap`. |
| Make the other changes so v9 **functions and runs** | Built: launcher `run_paper_segment_v9.ps1` (own run dir, own SQLite file, own dashboard port 8790), design doc, 65 new tests, 3 new decision-log columns, counters/banner/summary. **Policy-hash compatibility** added so growing the policy field set (48→51) does not refuse the running v8's resume — proven against the real v8 pin. |
| **Research** the 69k cohort | Two independent reports: 110-ticket forward study on local + GeckoTerminal history, and a 17-source online study. |

PAPER ONLY: no wallet, signing, or transaction submission exists on this path.

---

## 2. Research answer (detailed)

### 2.1 Do coins that reach ~69k MC / migrate reach higher?

**Yes, but the money is before v9's entry point.**

| measurement (from the **decision mark**, i.e. when v9 can buy) | pumpswap cohort | launch-pool control |
|---|---|---|
| 24 h forward peak, median | **1.38×** [95 % CI 1.28–1.93], n=46 | **0.84×**, n=19 |
| hits ≥ 2× | **32.6 %** | 0 % |
| hits ≥ 1.5× | 45.7 % | — |
| collapse ≤ 0.2× within 24 h | 30.4 % | — |
| survives 24 h (still printing) | 10 % | — |

The pumpswap−launch median difference is **+0.50× (Mann-Whitney p = 0.0037)** — the clearest
positive evidence produced this session. **But:**
* From the **first recorded post-migration print**, the first-hour candle-high is 1.90× (genuine
  graduates 1.97×); from the decision mark it is 1.31× (genuine **0.84×**). The pump is mostly
  over ~480 s before v9 decides.
* The **confirmed-genuine** subsample (launch-pool-backed / curve `migrated`, n=22) peaks at
  **0.85×** after the decision mark, with a 24 h nadir of **0.25×** — the post-migration dump.

### 2.2 Are they more legit?

**Structurally yes; "more legit" is not the same as "safer to buy late".** On complete-tape
300 s windows, pumpswap vs pump-fun launch pools: distinct wallets p50 **93 vs 9**, tx **184 vs
39**, top-3 buyer share **35 % vs 85 %**, volume HHI **0.075 vs 0.335**, pool depth **80 vs 12
SOL**, model rug-probability **0.576 vs 0.626** (p≈7e-14). This is a genuinely thicker market.

**But the venue label is a weak graduation proof.** In v8's record only 25.0 % of pumpswap
decisions had the curve read as `migrated`, 44 % were pump.fun mints, and 55.6 % were not
pump.fun launches at all. The online study independently reports that only ~1 in 10 PumpSwap
pools historically came from a real 85-SOL graduation (there are hundreds of thousands of
"curve-skip" pools, ~99 % dev-emptied). v9 therefore records **which proof** admitted a ticket
(`entry_graduation = migrated | venue`) and relies on the cap gate as the real discriminator.

### 2.3 Does the literal 69k-USD gate select a better subset?

**No, and it selects a worse downside.** The "69k" is the 2024-era price of the *same* fixed
85-SOL graduation event: 410.8 SOL FDV; at SOL≈$103.4 that is **$42.5k**; 69k USD = **667 SOL
FDV = +62 %** over migration. In the forward sample the gate passed 22.7 % (17/75). Gate-pass vs
gate-fail: peak 1.24× vs 1.38× (p=0.30, no edge), collapse 46.7 % vs 22.7 % (p=0.011, worse),
24 h nadir 0.43× vs 1.13×. The gate buys tokens already a median **3.3×** the migration cap.

**So the correct reading of the v9 launcher's pinned 69000 is: "buy migration tokens that have
already run +60 %".** That is what you asked to test and it is pinned; the doc and launcher say
so. To test the *migration event itself* instead, the knob is `--min-market-cap-usd 43000` in a
**new** run directory (a new policy, never a rewrite of the 69000 book).

### 2.4 External evidence (online research, 17 sources)

* Graduation rate: **1 in 58** launches cumulative Nov-25→Oct-26; month cohorts 1/144 → 1/32; an
  independent academic measurement is 0.63 % (Sept-25); median time-to-graduation **4.4 min**.
* Graduating ≠ succeeding: ~43 % of graduates still trade in week 5 vs ~1 % of non-graduates.
* **BOOST regime (from late Jul-2026):** the previously-locked migration liquidity can execute
  market buys + burn within the first ~5 min after migration. v9's 0–300 s post-migration window
  can therefore contain non-organic demand — documented as a confounder, not fixed.
* Late entry: 74 % of ordinary memecoin buyers lose over 2 weeks; profitability falls with entry
  lateness; initial PumpSwap depth ~85 SOL (~$8.9k) makes slippage the real cost.
* The post-migration multiple distribution has **no method-transparent public dataset**; v9's own
  shadow cohort is the instrument.

---

## 3. What is still risky (measured, not speculative)

1. **Tape cap / adverse selection.** 48.1 % of v8's pumpswap decisions died `tape_incomplete`
   because the GeckoTerminal trade endpoint returns only the newest ~300 swaps and has no
   backward pagination — a hot migrated pool's first 300 s cannot be collected. That is ~70.6
   pumpswap decisions/day adopted and dropped. The dropped (hot) half does **better**
   (24 h peak p50 **1.38× vs 1.10×**, difference CI 0.07–0.94), so v9 keeps the slower half.
   Consequence: maximum achievable quote coverage ≈51 %, so the pre-registered "quote coverage
   ≥70 %" **measurement-pass seal is unreachable as written**, and ≥5 buys/day is at risk
   (realistic 1–3/day; best ~6.7).
2. **Shared GeckoTerminal quota.** Key-less GT is one per-IP budget (~4–5 calls/min measured).
   With v8 running, v9 splits it; expect displaced throughput and 429 cooldowns in both books.
   The 9-minute pilot did **not** degrade v8 (it logged +8 decisions/+5 decided/+1 buy during the
   pilot and kept advancing after; no new 429 penalty), but the full segment runs far longer.
   **Never "fix" this by stopping v8.**
3. **$69k gate is a momentum filter** (above) and the venue proof is weak (above).
4. **Full suite is not green:** 1,673 tests, 3 failures in `test_return_denominator`, all
   **proven pre-existing** live-DB drift (they grade the book v8 is writing; same 3 fail on the
   git-HEAD engine against the same DB). 7 skips are optional research artifacts. No v9
   regression; new tests 65/65 green.

---

## 4. How to run it (paper only)

Full v9 segment (own run dir / SQL / port; **run in its own PowerShell window**):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_paper_segment_v9.ps1
```

* Dashboard: **http://127.0.0.1:8790/** — run dir `strategy_runs/paper_segment_v9_20261019`,
  SQL `coin_database_v9.sqlite3` (kept separate so two writers cannot contaminate v8's book).
* The policy is frozen by hash on first start; restarting the same command resumes. Changing any
  pinned flag (including `--min-market-cap-usd`) requires a **new** `--run-directory`.
* Time-boxed pilot / re-test (own run dir, SQL and port):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_paper_segment_v9.ps1 `
  -RunDirectory tmp\v9_pilot_<date> -SqlDb tmp\v9_pilot_<date>.sqlite3 `
  -HttpPort 8791 -PilotSeconds 540
```

* Acceptance / kill criteria are pinned in the launcher header and
  `docs/V9_GRADUATION_SEGMENT.md` (not included in this edition): ≥100 pumpswap
  decisions/day; quote coverage ≥70 % (infra-kill <50 % for two days); ≥5 buys/day admitted;
  edge pass = shadow peak p50 ≥1.05× and ≥20 % reach 1.5× within 1 h, net-of-fee bootstrap lower
  bound >0 on ≥60 closed tickets; kill after ~150 admitted tickets or 7 days if flat/negative.
  Always compare with v8's concurrent launch book — the cohort difference is the finding.

**Recommendation:** start it as a **measurement run**, not as an expected-profit run. The
population difference is real and worth quantifying; the as-built slice is late and tape-biased,
so the most likely honest outcome is another rigorous negative. If you want a cleaner v9, the
follow-up build that matters most is forcing the mid-window pre-fetch for graduated venues (so
the hot half stops dying on the tape cap); that needs its own build/verification and a new run
directory.

---

## 5. v8 status (kept running, untouched)

* PID **24828** alive; dashboard **http://127.0.0.1:8789/** HTTP 200; state saved continuously.
* At handover: **1,791** decisions logged, **143** ledger rows, 1 open position, realized
  **−0.2063 SOL** (paper). Its pinned policy sha `1b0159fb…4afd6009` (48 fields, mtime
  2026-10-17 18:10:58) is unchanged, its launcher has **zero** git diff, and nothing in v9's
  build or pilot wrote to its run dir, SQL, port or process.
* A future v8 restart will import this build: it will (a) log one yellow line saying the three
  new policy fields are held at their defaults, (b) on its first decision append, migrate
  `decisions_log.csv` once to add the 3 new columns (old rows empty) — atomic and loss-free
  (verified 10/10 on a copy of the live log). This is expected, not an error.

---

## 6. File index

| file | what |
|---|---|
| `docs/V9_GRADUATION_SEGMENT.md` | engine-era v9 design, policy fields, runbook, acceptance/kill, falsification — not included in this research-only edition |
| `run_paper_segment_v9.ps1` | v9 launcher (paper-trading engine) — not included in this research-only edition |
| `live_paper_trader.py` / `entry_validation.py` | engine changes: policy-hash compat, venue allowlist, graduation + market-cap gates, decision columns — not included |
| `tests/test_v9_graduation_entry.py` / `tests/test_run_policy_compat.py` | 65 new tests — not included |
| [`LOCAL_EVIDENCE.md`](LOCAL_EVIDENCE.md) / [`local_evidence.json`](local_evidence.json) | forward-return study (110 tickets, CIs, cap units) |
| [`ONLINE_RESEARCH.md`](ONLINE_RESEARCH.md) | external evidence, 17 sources, conflicts/stale-figures table |
| [`VERIFICATION.md`](VERIFICATION.md) | independent verification, live pilot, v8 health, verdict |
| `tmp/v9_build/`, `tmp/v9_verify/`, `tmp/v9_research/` | raw evidence, scripts and logs behind every number (original-project directories; not included) |
