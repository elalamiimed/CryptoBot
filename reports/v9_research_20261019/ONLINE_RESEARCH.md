# ONLINE RESEARCH — pump.fun graduation (~$69k MC): post-migration performance and legitimacy

**Task:** `task-2` (Team Lead: "lead"). **Agent:** `web-research`. **Written:** 2026-10-19 (Asia/Shanghai).
**Deliverable scope:** online research only — no engine code, no trading runs, no local-data analysis
(that is `LOCAL_EVIDENCE.md`, a different agent). All source URLs were accessed **2026-10-19** unless a
different access date is stated. Every figure is labelled with its evidence class:

| tag | meaning |
|---|---|
| **[M]** | measured on-chain / reconstructed from chain data by a named data provider or academic, method described on the source page |
| **[A]** | academic paper (peer-review status varies; preprint flagged) |
| **[D]** | derived by me by arithmetic from verified constants (shown in-line) — not a published number |
| **[X]** | vendor/analyst/marketing opinion or claim — not a measurement |
| **[S]** | **stale** figure (2024 / 2025 regime) — quoted for history only, must not be applied to Oct-2026 trading |
| **[M2]** | page-level market-data quote (price reported in an article; **not** a live API read — see §10) |
| **[X2]** | page-embedded live ticker on a news page — weakest source class, corroboration only |
| **[internal]** | project-internal measurement from the team's SPEC file — not online research and not a substitute for `LOCAL_EVIDENCE.md` |

> Honesty note up front: the decisive quantitative question — *the distribution of post-migration price
> multiples of graduated tokens* — **is not answered by any accessible public study with a transparent
> method.** Dune dashboards that appear to measure it (e.g. "Pump.fun Post-Graduation Survival Curve",
> <https://dune.com/queries/6774063>, accessed 2026-10-19) are JavaScript-rendered and their numbers could
> not be read from this environment; one secondary source gives a 2024 snapshot only. The report therefore
> gives what *is* measured (base rates, survival, pool integrity, buyer P&L, regime changes) and explicitly
> flags the multiple-distribution gap in §7. It does not pad the gap with invented numbers.

---

## Executive summary (10 lines)

1. **The "$69k market cap" is not a protocol constant.** pump.fun graduation is a fixed **85 SOL raise** that
   seeds a PumpSwap pool with **206.9M of the 1B supply**; implied FDV at migration = **410.8 SOL** [A/D].
2. At the SOL/USD price measured for this build (≈**$105**), that is **≈$43.1k**, not $69k. The $69k figure
   describes the same event at **SOL ≈ $168**, which is where SOL traded when the figure was popularised
   (2024 sources quote "$69,000 market value", "$12,000 liquidity", SOL sold at an average **$160**) [S/D].
3. Therefore `--min-market-cap-usd 69000` at today's SOL is a **+60% post-migration momentum filter**
   (≈656–657 SOL FDV vs ≈411 SOL at migration), not the graduation event itself — exactly as SPEC §0 assumes.
4. **Graduation is rare:** **1 in 58** pump.fun launches graduated over Nov-2025→Oct-2026 [M]; month-cohort
   rates ran from **1 in 144** (Nov-2025) to **1 in 32** (Aug-2026) [M]; an independent Sept-2025 academic
   dataset gives **0.63%** [A]. Graduation is also fast: median **4.4 minutes** / 457 curve events [A].
5. **Graduating is not the same as succeeding.** ~**43%** of graduated tokens still trade in their 5th week
   vs ~1% of non-graduates [M] — a real survivorship lift — but in the Aug-2024 snapshot only **18 of ~1.8M**
   launched tokens were above **$10M** MC and only **96** above **$1M** [S/D].
6. **A genuine graduation pool is structurally hard to rug:** **98%** of graduation pools never had SOL
   withdrawn [M]. Fake "graduation-look" pools are the opposite: **451,402 curve-skip PumpSwap pools** in
   8 months, **99% emptied by the dev**, median **12 minutes** [M].
7. **But "listed as a new pumpSwap pool" ≠ "graduated".** Only ~**1 in 10** PumpSwap pools in that window
   came from a graduation [M]. Also, **hollow graduations** exist: only **1 in 50** Mayhem-mode graduations
   actually filled the normal 85 SOL (median pool 0.2 SOL in Mar–Apr 2026) [M]. v9's venue-based graduation
   basis is therefore weak on its own; the MC gate is the real discriminator.
8. **Post-migration flow regime changed in mid-2026:** pump.fun **BOOST** (announced ~29-30 Jul 2026 now
   injects the previously-locked migration liquidity as **market buys within 5 minutes after migration**
   and burns the bought tokens; daily graduation rate spiked to **6.7%** (~8× June) [M/news]. This overlaps
   v9's 300 s post-migration observation window and must be treated as a regime break, not baseline.
9. **Late entry has weak public support:** 74% of ordinary memecoin buyers ended down after 2 weeks;
   first-minute entries were profitable 34% of the time vs 28% for day-later entries [M]. Buying *after* a
   +60% post-migration run is a trade the public data does not validate either way — but the profitability
   gradient, 65%-of-devs-sell-within-a-minute pattern, and shallow (~$8.9k) initial pool depth all point
   the same direction: the exit liquidity for late buyers is largely devs/bundles/snipers [M][X].
10. **Biggest caveat:** every "graduation rate" in the literature is definition- and collector-sensitive
    (period, 24 h window vs 30-day cohort, collector polling artefacts); one 2026 audit explicitly
    **retracts** earlier 24-hour graduation rates because the "graduated" label was the *collector's* label,
    not the platform's event [A]. Treat any single graduation-rate number as ±1 regime, not a constant.

---

## 1. Where "$69k" comes from, and what it is worth at today's SOL (Q2 + Q6)

### 1.1 The verified mechanism (what graduation actually is)

Verified curve constants from an academic on-chain reconstruction (sample 1 Sep–1 Oct 2025) [A]:

| constant | value | source |
|---|---|---|
| total supply | 1,000,000,000 tokens | arXiv:2602.14860v1 §III |
| sold on the virtual curve | 793.1M tokens | same |
| reserved for the PumpSwap pool at graduation | **206.9M tokens** | same |
| virtual SOL at launch | 30 SOL | same |
| total virtual reserve at graduation | 115 SOL (= 30 virtual + **85 real raised**) | same |
| SOL that actually migrates to the PumpSwap pool | **85 SOL** | same; corroborated: "a pool made by a graduation starts with about 85 SOL" [M] |
| launch-curve swap fee | 1.25% (0.30% creator + 0.95% protocol) | [A]; corroborated by [M] ("1.25% of each trade, or 0.95% on cashback coins") |

**Arithmetic [D]:** graduation price = 85 SOL ÷ 206.9M tokens = 4.1083e-7 SOL/token.
FDV = 1e9 × 4.1083e-7 = **410.8 SOL**.
(Equivalently via the curve: 115 SOL ÷ 279.9M virtual tokens × 1e9 = 410.9 SOL. Two routes agree.)

### 1.2 The USD conversion — both cohorts quantified

| SOL/USD | FDV at a *fresh* graduation pool | what the user's 69k gate means |
|---|---|---|
| **$104.97** (measured 2026-10-17) [M2] | **$43,124** | gate = 657.3 SOL FDV = **+60.0% above migration price** [D] |
| **$105.15** (site ticker on 2026-10-19) [X2] | **$43,199** | gate = 656.2 SOL = **+59.7%** [D] |
| $160 (Aug-2024 average SOL sale price of pump.fun fees) [S] | $65,733 | gate ≈ 431 SOL → ≈ the "**$69k**" the 2024 docs/guides quoted [S/D] |
| **$167.96** | **$69,000** | at this SOL price, graduation itself *is* ≈$69k [D] |

**Is the $69k figure reproducible from the 2024 record? Yes.** A 2024-08-19 Foresight News article (the
canonical origin of the "1.4% graduation rate" narrative) states: a token graduates when it "exceeds the
critical threshold of **$69,000** in market value", at which point "**$12,000 in liquidity**" is deposited to
Raydium (the migration venue before PumpSwap); it also reports pump.fun's fee account having sold 222,073 SOL
"at an average price of **$160** over the past three months" [S]. 411 SOL × $160 = **$65.7k** and
85 SOL × $160 = **$13.6k** — consistent with the quoted $69k/$12k once the era's curve vintage and
migration-fee deduction are allowed for. The $69,000 figure was still being quoted in a 2025-02-27 article,
at a time when SOL had hit an ATH of $295 (2025-01-19) before halving — so it was *approximately correct for
roughly a year*, then became stale as SOL fell [S17]. So: **the $69k is the SOL-denominated graduation FDV
priced at 2024/early-2025 SOL**, then repeated verbatim long after SOL left that range.

**How the stale figure propagates (measured evidence of the propagation):**
* A 2026-03-21 "Pump.fun Graduation Threshold Explained (2026)" guide still says "a market cap of roughly
  $69K" — but immediately admits "the curve is priced in SOL, so the USD figure moves with SOL's price" [X].
  At any SOL price below ≈$168 that headline number is too high; the page concedes the mechanism without
  correcting the number.
* The Feb-2026 academic paper says the threshold "corresponds to approximately 85 SOL raised and a market
  capitalization of about $69,000" — **"during our sample period"** (Sept 2025) [A]. It is a period-specific
  observation, not a constant, but is easy to lift out of context.
* The user's brief (and therefore the pinned v9 flag) uses the same 2024-era number. SPEC §0 is right: at
  today's SOL, `--min-market-cap-usd 69000` is **+~60% above the migration event**.

**Current SOL/USD (Q6), stated with source quality:** $104.97 at 2026-10-17 07:49 UTC from a price-analysis
article carrying intraday candles/indicators [M2]; $105.15 on a live ticker embedded in a news page fetched
2026-10-19 [X2]; the Lead's own live GeckoTerminal quote was ≈$104 (SPEC §1). **Direct public price APIs
(CoinGecko, DexScreener, Binance) are not reachable from this research environment** (see §10), so three
page-level quotes are the evidence. Range to use for conversion: **$104–$106** → graduation FDV
**$42.7k–$43.5k**.

### 1.3 The one-line answer to "is 69k the migration?"

No. At current SOL, **every genuine fresh migration pool starts at ≈$43k**; the 69k flag admits only tokens
that have already appreciated ≈60% **after** migration (or pools that are not genuine migrations at all —
see §3.4/§4.1). The flag is a *momentum/anti-dump* filter, not a graduation filter. v9's documentation and
acceptance criteria should say exactly that (SPEC §0 already does).

---

## 2. What share of launches graduate, and how fast (Q1)

### 2.1 The best current numbers (and why they differ)

| estimate | period / definition | source | class |
|---|---|---|---|
| **1 in 58** (1.72%) | launches Nov-2025 → 7-Oct-2026 that graduated by 7-Oct-2026 | Bitquery, verified 2026-10-10 | [M] |
| 1 in 144, 143, 135, 102, **63**, 108, 127, 107, **37**, **32** | share of each launch **month**'s tokens that graduated **within 30 days** (Nov-2025 → Aug-2026, in order) | Bitquery charts | [M] |
| **0.63%** (paper's stated rate; 4,338 graduated of 655,770 created — the printed counts imply 0.66%) | tokens created 1-Sep→1-Oct-2025 that reached graduation | arXiv:2602.14860v1 | [A] |
| **0.198%** (1,651 / 832,941), Wilson CI [0.189%, 0.208%] | launches 8-May→10-Jun-2026 that reached a terminal outcome **within 24 h** | Zenodo RED-PUMP-2026-v1 | [M]/[A] |
| 1.4% overall; 1–2% "recent" | Aug-2024, Dune dashboards (@evelyn233, @adam_tehc) | Foresight News 2024-08-19 | [S] |
| daily graduation **rate** 2.5% → 4.7% → **6.7%** in one week | last week of Jul 2026, *daily* rate (different denominator!) | The Block via ChainCatcher 2026-07-30 | [M/news] |

**Reconciliation (important):** these are not in conflict, they are different objects.
* The **24-hour** rate (0.198%) is much lower than the **30-day** rate (1/32–1/144) because most graduations
  need more than a day to happen or the collector misses them.
* The **1 in 58** is a *cumulative* rate over 11 months of launches, boosted by the post-June graduation surge.
* The **1.4%** is 2024, when pump.fun had ~20k launches/day and Raydium migration; do not use it for v9.
* The **6.7% daily** figure counts graduations *that day* over launches *that day* — a flow ratio, much
  higher than any cohort rate. It is evidence of the **BOOST regime change**, not of cohort survival.

### 2.2 Time-to-graduation

* Median **4.4 minutes** from creation to graduation; median **457** bonding-curve events; strong right tail
  (a minority takes tens of minutes) [A]. This is the cleanest published time distribution.
* "Most did it on their launch day" [M]; half of all pump.fun launches have their **last** trade within
  ~3 minutes, and 79% never trade after launch day [M].
* Graduation has become *cheaper/thinner*: in **September 2026, 33% of graduations took three curve trades
  or fewer** (whale/bot buys filling the curve at once), vs 2% in Nov-2025 [M]. A "graduate" is therefore
  increasingly a token that **one actor** pushed over the line — relevant to legitimacy (§4).
* Derived flow size [D]: Bitquery's method cross-checks **47,539 graduation records** up to 5-Jul-2026 over
  its ~8-month coverage → **≈190–200 graduations/day on average**; Bitquery also says September-2026 had
  >4× June-2026 graduations, so the *current* daily flow is materially higher than that average.
  The 2024 figure was **100–200/day** [S] — the same order, which is a useful sanity check.

---

## 3. What happens AFTER graduation / migration (Q3)

### 3.1 Survival is the strongest measured "after graduation" fact

* **43%** of graduated pump.fun tokens still traded in their **fifth week**; of the non-graduated tokens,
  only **1%** did [M]. That is the single most defensible "graduation is a quality filter" number available.
* Overall baseline for comparison: **79%** of pump.fun coins never trade after launch day; only **1 in 437**
  still has ≥10 trades in week 5 [M].
* Caveat: this is *trading survival*, not price survival. It says graduates remain liquid/tradeable longer;
  it does **not** say holders made money.

### 3.2 Do they "pump higher"? — what public data can and cannot show

**What is measured:** a 2024 snapshot (Foresight News, Dune data) looked at **~1.8M** deployed tokens and
found **96** currently above **$1M** MC and **18** above **$10M** MC. With the then-current 1.4% graduation
rate that implies [D]: ≈25,200 graduates → **≈0.38% of graduates ever reached $1M** and **≈0.07% reached
$10M** (snapshot counts, so tokens that peaked and fell are missed — this is a floor, but a small one).
The same article says plainly: "many of the tokens that have successfully 'graduated' have not performed
well in the subsequent market, with their market values nearing zero" [S].

**What is not publicly measured (the honest gap):** I could not find any credible, method-transparent
public source publishing the *distribution* of post-migration multiples (p50/p90 peak within 1 h / 24 h /
7 d, share that 2×/10×, share that dumps below migration MC, time-to-peak). Dune has dashboards that appear
to measure something adjacent — "Pump.fun Post-Graduation Survival Curve" <https://dune.com/queries/6774063>
— but its output is not machine-readable from here. **Treat any claim of a specific post-graduation multiple
distribution as unverified until v9 measures it on its own shadow cohort.**

**Closest on-point post-migration statement found — but 2025 regime [S]:** a 2025-02-27 ChainCatcher article
(distributed by BlockBeats) reports that on-chain data showed "**over 70% of meme coins displayed a 'peak upon
pool creation' trend during the external phase, with an average survival time of less than 48 hours**", and
that on 2025-02-24 only **one** pump.fun-graduated token that day had a market value barely above **$1M**.
Context for that quote: SOL had hit an ATH of **$295** on 2025-01-19 and then fell >50% — i.e. a different
market. Read it as *hypothesis-generating*: the modal post-migration path may be "peak at/just after pool
creation, then decay", not a sustained re-rating. It is the only public quantitative statement on the peak
pattern I could find, and it must be re-measured for Oct-2026 (v9 shadow cohort), not assumed.

**What the microstructure implies (analyst reasoning, [D]/[X]):** the migrated pool starts with **85 SOL of
real liquidity ≈ $8.9k** (85 × $105) against a $43k FDV — i.e. the pool is *shallow*. A 0.25%-fee
Uniswap-v2-style CPMM (PumpSwap fee = 0.25%, 0.20% LP / 0.05% protocol; zero migration fee, replacing
Raydium's 6 SOL migration fee) means large orders move price violently; a third-party risk review describes
"shallow initial liquidity pools from bonding curve proceeds" creating "high-slippage trading environments"
and enabling sandwich attacks, and asserts (assessment, not measurement) that "most tokens decline 90%+
from graduation price" [X].

### 3.3 BOOST — a real post-migration regime change (mid-2026) that lands inside v9's window

Per a 2026-07-30 ChainCatcher summary of The Block's reporting [M/news]:
* pump.fun's **BOOST** mechanism (launched late July 2026) targets "dead liquidity": previously about **20%
  of migration liquidity was permanently locked in the PumpSwap pool**; now that portion **automatically
  executes market buy orders within five minutes after migration**, and all purchased tokens are **burned**.
* BOOST does not mechanically raise the graduation rate; it incentivises traders to push tokens over the
  line by guaranteeing post-migration buying pressure and supply destruction.
* Reported effect: daily graduation rate hit **6.7%** on the Friday before publication (~**8×** June's
  average); the prior 4 days averaged **4.7%** vs 2.5% the week before. PUMP token +10% YTD, ~$850M MC.

**Why this matters to v9:** v9 adopts a freshly migrated pool, observes ~300 s, and decides. **BOOST's
buy+burn window is exactly the first 300 s after migration.** Consequence: part of any post-migration price
rise in the observation window is *protocol-driven*, not organic demand, and the burn mechanically reduces
future float. Do **not** stack v9's entry criterion ("+60% above migration") on top of a BOOST pump and
interpret it as organic momentum. (Exact buy size and precise BOOST launch date could not be verified from a
primary pump.fun source — the pump.fun docs pages were unreachable, see §10. Bitquery's Mayhem article
independently documents a different protocol intervention — Pump.fun's own trading bot — see §3.4.)

### 3.4 "Graduated" pools are a mixed population — three contaminating types

1. **Genuine graduations:** 85 SOL + 206.9M tokens seeded; **98% never had SOL withdrawn** [M]; ~798 of 800
   sampled were confirmed on-chain to be the protocol-created pool [M]. These are the "legit" pools.
2. **Hollow graduations (Mayhem mode):** a dev can switch on Mayhem, where pump.fun's bot trades the coin
   and repeatedly **resets the curve price**. Of **7,958** Mayhem graduations (12-Nov-2025→5-Jul-2026), only
   **158 (1 in 50)** filled a normal 85 SOL pool; median pool SOL was **7** (Dec–Feb), **0.2** (Mar–Apr),
   **2** (May–Jul); the median finished Mayhem curve quoted **28% of a fresh coin's price** [M]. These
   appear in PumpSwap pool feeds as "new pools" but are not 85-SOL graduations.
3. **Curve-skip / counterfeit pools:** permissionless PumpSwap pools opened for brand-new coins that never
   touched a launch curve: **451,402** of them (30-Oct-2025→5-Jul-2026), **99% later emptied by the dev**,
   median **12 minutes** to first withdrawal, **87% within an hour**; median opening = **85 SOL + the whole
   1B supply** (looks exactly like a graduation); **95% of the SOL buyers lost came from dev-linked wallets**
   in the 160 pools traced [M]. **Only ~1 in 10 PumpSwap pools in that window came from a real graduation** [M].

**Conclusion for Q3:** a graduated *genuine* pool is structurally hard to rug (98% untouched) and its token
survives longer (43% still trading week 5) — but the label "new PumpSwap pool" is heavily contaminated, and
the population of genuine graduates is not a population of winners: the 2024 base rate for ever reaching
$1M is well under 1% of graduates [S/D].

---

## 4. Are graduated tokens "more legit"? Rug/dev-dump/liquidity/survival (Q4)

### 4.1 What is genuinely better about real graduates

| property | genuine graduation pool | non-graduated curve token / curve-skip pool | source |
|---|---|---|---|
| LP can be pulled by dev? | **No** — protocol owns/seeds it; only 2% of graduation pools ever saw SOL withdrawn | curve-skip pool: **99% emptied**, median 12 min | [M] |
| still trading in week 5 | **43%** | **1%** | [M] |
| "official" pool confirmed on-chain | 798/800 sampled | curve-skip opens look similar but are distinguishable by first record | [M] |
| graduation cost/signal | 85 SOL of real demand had to be spent | can be opened for 85 SOL by one wallet | [M] |

So on *pool integrity and trading survival*, a genuine graduate is measurably more legitimate. That is the
"yes" part of the answer.

### 4.2 Why that "yes" is partly survivorship / selection — four distinct biases

1. **Definitional selection.** Graduation *is* "enough buyers showed up". Conditioning any return study on
   graduation selects for momentum/attention. The 43%-vs-1% survival lift is real but is measured *because*
   the token already proved it could attract 85 SOL. No public study controls for this by comparing graduates
   with a matched pre-graduation cohort.
2. **Snapshot survivorship in "reach $1M/$10M" studies.** Counts like "96 tokens above $1M" are *current*
   counts; tokens that peaked and crashed are invisible [S]. The true rate of *ever* reaching a threshold is
   higher than a snapshot implies, while the rate of *staying* there is lower.
3. **Measurement truncation in survival studies.** The widely quoted CoinGecko stat — **4.55% of pump.fun
   tokens survive >90 days** (18.67M tokens analysed; 68.67% last trade on launch day; 80.37% within 2 days)
   — explicitly **"only capture[s] transactions on Pump.fun's bonding curve and do[es] not account for tokens
   that 'graduate' to external DEXes"** [M]. So it is *not* evidence that graduates die in 90 days; it is
   blind to the post-graduation venue. Conversely, graduation studies are blind to the 98% that never
   graduate. The two literatures condition on opposite halves of the same dataset.
4. **Label-collection error in the graduation rate itself.** A 2026 preprint audits the dominant
   "top-50 feed" collector design (60 s polling of pump.fun's top-50 newest-coins feed): only mints observed
   with `complete === true` while visible are labelled GRADUATED, everything else after 24 h is TIMEOUT —
   and **"TIMEOUT does not establish that platform-side graduation did not occur."** The paper **retracts**
   its own earlier 24-hour graduation rate, "3.18× decline", and Kaplan-Meier/Cox claims because they
   depended on the collector label [A]. Its pre-registered model fails out-of-time (dev AUROC 0.8594 →
   validation 0.4642, indistinguishable from chance) [A]. Practical meaning: **the "0.198%" and similar
   24-hour rates are collector artefacts and undercount**; the 30-day/cohort rates [M] and the academic
   curve reconstruction [A] are safer anchors for base rates.

### 4.3 The dev side is not "more legit" because a token graduated

Bitquery's 11-month block-0 study (8.2M checked launches) [M]:
* dev's first sale within **1 minute** on **65%** of launches, within a day on **90%**;
* on **21%** of launches the dev's own bundled wallets bought in block 0, taking a **median 10% of supply**;
* devs + bundled wallets made **≥$579M** after fees on launches to end-June 2026 (a floor); sniper bots made
  $31.5M on what they sold ($15.2M counting unsold as worthless);
* **38%** of launches had a non-dev buyer in block 0; **28%** had sniper bots there;
* post-July, bundled wallets ramped from $56.4M (June) to **$1.2B (Sept)** in single 1,000+ SOL pool
  purchases "within about a second of launch, on coins that had already filled their launch pool" — i.e.
  large organised post-graduation buying/selling activity. (This is exactly the population v9 will meet.)

**Answer to Q4:** a genuine graduate's *liquidity and survival* are more legitimate; the *dev behaviour
upstream* is not, and the comparison is contaminated by selection + label error + truncation. "Graduated"
is a weak legitimacy signal at the margin — it certifies 85 SOL of demand at one moment, not honest devs.

---

## 5. Late entry vs early entry, costs, and whether retail loses (Q5)

### 5.1 Buyer P&L — the strongest measured evidence

Bitquery's 10-launch-week study (Nov-2025→Aug-2026, ~2.9M ordinary wallets, method excludes devs/bots,
includes pump.fun fees) [M]:
* **74%** of ordinary buyers ended with less SOL after two weeks (70–79% in *every* month);
* median buyer lost **$13**; total loss **≈$269M**; buyers losing ≥$1,000 account for 46% of all losses;
* **best 1% of buyers took 56%** of all gains; top 10% took 95%;
* sandwich bots made ≈**$13M** in the same weeks, positive in all 10;
* **timing gradient:** entries in the first minute were profitable **34%** of the time; 1–10 min 33%;
  10–60 min 32%; 1–24 h 29%; **after a day 28%**. "Earlier is slightly better" — and even the earliest
  ordinary buyers lost on ~2 in 3 coins.
* CoinGecko's competing study (73% of pump.fun traders "in profit" in April 2026) could not be reproduced
  by Bitquery: same method on the same month gave **27%** ahead; CoinGecko nets monthly sales vs purchases,
  ignores unsold coins, and does not filter bots [M]. **Conflict resolved in favour of the loser-heavy
  result** for the question "does an ordinary late buyer make money".

### 5.2 What this says about v9's exact trade ("buy at ≥$69k, i.e. after +60% post-migration")

Public data does **not** directly test that trade; the nearest measured facts are all unfavourable or neutral:
* the profitability gradient is monotonically worse the later you buy (§5.1);
* 65% of devs have already sold within a minute of launch, and 90% within a day [M];
* the first pool is ~85 SOL ≈ $8.9k deep [D], so by the time a token is +60% the marginal buyer is
  price-impact-sensitive and sandwich-bait (third-party risk assessment explicitly flags this) [X];
* protocol interventions (BOOST buys in the first 5 min; Mayhem bot) distort the first-minutes price path,
  so "+60% in the window" is not cleanly interpretable as organic demand (§3.3/§3.4).
* The academic breakeven analysis for the *pre*-graduation side is also worth stating: under a naive
  buy-and-hold-until-graduation rule on the curve, expected return > 0 requires graduation probability
  `p > (vSol/115)²`; the unconditional empirical curve lies **below** that breakeven, i.e. even with the
  curve-state known, naive buy-and-hold does not clear its own hurdle [A]. There is no "free" graduation
  premium in the public data.

**Costs on PumpSwap (for the engine's friction assumptions):** 0.25% swap fee (0.20% LP / 0.05% protocol),
zero migration fee, Uniswap-v2-style CPMM; launch curve fee before migration is 1.25% [X]/[A]. Real cost of
v9's trade is dominated not by the 0.25% fee but by **slippage on an $8.9k pool** and the spread to the
migration price; v9's paper friction of ~2% total may understate the *market* cost of a $69k-MC entry by a
lot. (The engine's exact friction constants are out of scope here; flagging for the Lead.)

---

## 6. Conflicts, definitional traps and stale figures (read before quoting any number)

| # | conflict / trap | resolution used here |
|---|---|---|
| C1 | **1 in 58** vs **0.63%** vs **0.198%** vs **1.4%** graduation rates | different periods & denominators; 24 h (0.198%) < 30-day cohort (0.63%–1/32) < cumulative 11-month (1/58); 1.4% is Aug-2024 [S]. **For v9 planning use 1-in-32 to 1-in-58 as the current-regime band, and note BOOST likely pushed it higher after Jul-2026.** |
| C2 | CoinGecko **4.55% survive 90 days** vs Bitquery **43% of graduates trade in week 5** | not comparable: CoinGecko counts only bonding-curve trades and excludes graduated tokens (its own caveat); Bitquery conditions on graduates. Both "true", different populations. |
| C3 | CoinGecko **73% of traders profitable** vs Bitquery **27–28%** | method differences (period netting, unsold coins, bot inclusion); Bitquery's reproduction attempt is the stronger analysis for ordinary buyers. |
| C4 | **"$69k"** repeated by 2026 guides/paper vs SOL-denominated reality | $69k = 411 SOL at SOL≈$168; at SOL≈$105 the same event is ≈$43k. **Use $43k unless/until SOL > $160.** |
| C5 | **"graduated"** used for Mayhem hollow graduations, and PumpSwap pool creation used as proxy for graduation | 1 in 50 Mayhem graduations fill 85 SOL; only ~1 in 10 PumpSwap pools were real graduations in the measured window. Verify pool provenance (first record / 85 SOL depth), not the venue label. |
| C6 | "**Pump.fun docs**" as source of $69k | pump.fun's own docs could not be fetched from this environment (blocked). The $69k claim is documented here through third-party guides/papers and the 2024 press record, with the SOL arithmetic made explicit rather than trusted. |
| C7 | **BOOST-era daily graduation rate (6.7%)** vs cohort rates (1-in-30) | flow ratio ≠ cohort survival; only use it as evidence of a regime break, not as v9's expected graduation frequency. |
| C8 | 2024/2025 figures everywhere | labelled [S]; the memecoin market cap fell from a $150B peak (2024) to ~$30–38B (mid-2026) per the CoinGecko-study write-up [M/news] — the population is not stationary; do not fit v9 expectations on 2024 data. |

---

## 7. What is still unknown (explicit gaps)

1. **The post-migration multiple distribution.** No accessible public source gives p50/p90 peak multiple,
   % that 2×/10×, % that fall below migration MC, or time-to-peak for *genuine* graduates in the current
   regime. This is the single biggest gap, and it is exactly what v9's shadow cohort can measure. Dune
   dashboards exist (<https://dune.com/queries/6774063>) but were not machine-readable here.
2. **What fraction of genuine fresh migrations are ≥$69k within 300 s** (i.e. +60% in ≤5 min). Not published.
   Public data can only bound *starting* FDV (≈411 SOL) and show pool depth (85 SOL).
3. **How often curve-skip/Mayhem pools appear in the current `/new_pools` pumpswap feed (Oct-2026).**
   Bitquery's pool-provenance records end 5-Jul-2026; the Oct-2026 mix is unmeasured online.
4. **BOOST's exact size, timing and measured price-path effect.** Mechanism direction is reported by The Block
   via a secondary summary; the primary pump.fun docs and The Block page were not fetchable (403). The exact
   share of migration liquidity converted to buys, and its effect on the first 5 minutes, is unknown here.
5. **Whether the current (Oct-2026) graduation rate is still rising / has reversed.** BOOST evidence is
   July-2026; one search hit claimed pump.fun activity fell sharply over Q3-2026 but the page was
   unfetchable (403) — **unverified, excluded from findings**.
6. **Dev-dump behaviour specifically at/after migration** (as opposed to at launch). Bitquery measures
   launches and PumpSwap pools separately; a clean "dev sells into the migration pump" statistic was not
   found. v9's existing `--dev-dump-block` gate is the right instrument to measure it.
7. **Survivorship-controlled comparison** (graduates vs matched pre-graduation cohort with same curve
   progress). Not published; the arXiv paper's conditional-probability framework is the closest tool.

---

## 8. Implications for v9 (what the Lead asked research to quantify)

1. **Do not market v9's admission as "the migration (69k) cohort".** At SOL ≈ $105 the migration event is
   ≈ **$43k**; the pinned 69k filter admits only pools already **+60%** above migration FDV, inside a ~300 s
   window. That is a *post-migration momentum* cohort. Document both cohorts (43k migration vs 69k
   momentum) in `docs/V9_GRADUATION_SEGMENT.md` and the launcher header, as SPEC §0 requires.
2. **Graduation basis should not be "venue=pumpswap" alone.** The online evidence says most PumpSwap pools
   are not graduations, and hollow graduations exist. Without RPC, the practical proxies are: the **MC gate**
   (a fresh genuine pool starts ≈411 SOL ≈ $43k, so any 69k ticket has already moved), the **depth/impact
   gate**, and (future) a pool-provenance check. Flag "venue" as `entry_graduation=venue` honestly (it is
   what SPEC §3.3 says) and record basis per row so the shadow analysis can separate genuine vs unknown.
3. **Expect a small admitted sample.** Current total graduation flow is likely several hundred to ~1–2k/day
   across all venues, of which only genuine SOL-priced graduations matter and only a minority will be
   +60% inside 300 s. v9's acceptance criterion "≥100 pumpswap pools decided/day" may be optimistic in the
   post-BOOST/activity-decline regime; measure before judging the strategy (§5 kill criteria already handle
   an under-measured cohort — keep the infrastructure-kill rule).
4. **The shadow cohort must register the pre-MC-filter population** (SPEC §3.4 already does: skip labels
   `skip_market_cap` / `skip_graduation`). This is the *only* way to avoid conditioning on the 69k filter
   and to measure the true post-migration multiple distribution per §7.1. Preserve `entry_market_cap_usd`
   and basis in every row (SPEC §3.4 does).
5. **Treat BOOST as a confounder** in the first 300 s: log whether the observation window overlapped the
   BOOST buy window; a run that starts before/after a BOOST change is not comparable.
6. **Sanity-check SOL/USD per run** and record it with the cap basis: the same 69k flag is a $43k-equivalent
   filter today and a true graduation filter if SOL returns to ≈$168. The policy hash must not move, but the
   report must state the SOL price used.
7. **Reference numbers for the write-up (all sourced above):** graduation 1-in-32 to 1-in-58; median
   time-to-graduation 4.4 min; 43% of graduates trade week 5 vs 1%; 98% of genuine graduation pools never
   lose SOL; 99% of curve-skip pools are emptied (median 12 min); 74% of ordinary buyers lose over 2 weeks;
   65% of devs sell within a minute; PumpSwap fee 0.25%; initial pool depth ≈85 SOL ≈ $8.9k.

---

## 9. Source register (all accessed 2026-10-19 unless stated)

| id | source | URL | date/verified | class | used for |
|---|---|---|---|---|---|
| S1 | Bitquery — "Pump.fun: 1 in 58 coins graduate, 79% die after day one" | <https://bitquery.io/investigations/solana-launchpad-year> | figures verified 2026-10-10 | [M] | graduation rates by month, time/life stats, 43% week-5 survival, 98% untouched graduation pools, 451,402 curve-skip pools, 1-in-10 PumpSwap pool provenance, 47,539 graduation records |
| S2 | Bitquery — "3 in 4 Solana memecoin buyers lose money, $269M in 10 launch weeks" | <https://bitquery.io/investigations/solana-memecoin-traders-lose-money> | verified 2026-10-15 | [M] | 74% lose, median −$13, timing gradient 34%→28%, best-1% 56%, sandwich bots, CoinGecko-method conflict |
| S3 | Bitquery — "Pump.fun Mayhem mode: only 1 in 50 graduations fills the pool" | <https://bitquery.io/investigations/pump-fun-mayhem-mode> | verified 2026-10-12 | [M] | 85-SOL full graduation definition, hollow graduations (158/7,958), 0.2–7 SOL median pools, 28%-of-launch-price curves, 22× matched comparison |
| S4 | Bitquery — "Pump.fun devs' bundles made $579M+, snipers just $31.5M" | <https://bitquery.io/investigations/pump-fun-snipers-bundles> | verified 2026-10-10 | [M] | 65% devs sell <1 min, 21% bundled median 10% supply, $579M dev/bundle profit, 38% block-0 buyers, post-July $1.2B bundled pool buying |
| S5 | Marino, Naviglio, Tarantelli, Lillo — "Predicting the success of new crypto-tokens: the Pump.fun case", arXiv:2602.14860v1 (also ar5iv mirror) | <https://arxiv.org/html/2602.14860v1> · <https://ar5iv.labs.arxiv.org/html/2602.14860> | 2026-02-16 | [A] | exact curve constants (30 virtual SOL, 1.073B virtual tokens, 206.9M pool tokens, 115/85 SOL, 1.25% fee), 0.63% graduation, median 4.4 min / 457 steps, $69k "during our sample period", buy-and-hold breakeven `p>(vSol/115)²` below 1 |
| S6 | Kamat — "Auditing Collector-Generated Graduation Labels on Pump.fun: Measurement Error and Temporal Non-Generalization", arXiv:2607.02823v4 | <https://arxiv.org/html/2607.02823v4> | 2026-09-10 | [A] | top-50 collector design, TIMEOUT ≠ non-graduation, retraction of earlier 24h graduation rate/3.18× decline/KM-Cox claims, out-of-time AUROC 0.859→0.464 |
| S7 | Kamat — RED-PUMP-2026-v1 dataset record (Zenodo) | <https://zenodo.org/records/20633603> | v1.1 2026-06-10, modified 2026-10-13 | [M]/[A] | 860,213 launches, 832,941 terminal outcomes, 1,651 graduated = 0.198% within 24 h (Wilson CI given); record itself flags that the newer version no longer reports the graduation rate because it treats the collector label as the platform event |
| S8 | Foresight News via ChainCatcher — "The real data of pump.fun revealed: a graduation rate of 1.4%, only 3% of users profit over $1000" | <https://www.chaincatcher.com/en/article/2139008> | 2024-08-19 | [S] | origin of "$69,000 market value" / "$12,000 liquidity to Raydium"; 1.4% graduation; 20k launches/day, 100–200 graduations/day; 96 tokens >$1M, 18 >$10M; SOL avg $160 |
| S9 | The Block via ChainCatcher — "After the launch of BOOST by Pump.fun, the graduation rate soared to 6.7%…" (links to theblock.co/post/409815) | <https://www.chaincatcher.com/en/article/2279071> | 2026-07-30 | [M/news] | BOOST mechanism (≈20% of migration liquidity → market buys within 5 min + burn), 2.5%→4.7%→6.7% daily graduation rate, PUMP +10% YTD |
| S10 | Xanguard — "Pump.fun Graduation Threshold Explained (2026)" | <https://xanguard.tech/blog/pumpfun-graduation-alerts/> | 2026-03-21 | [X] | example of "$69K" propagation; its own caveat "curve is priced in SOL, so the USD figure moves with SOL's price"; PumpSwap-since-March-2025 claim; post-graduation playbook opinions |
| S11 | Blockchain News — "SOL Price Prediction: Momentum Flatlines at $105…" | <https://blockchain.news/PostAMP?id=20261017-price-prediction-sol-momentum-flatlines-at-105-as-bears> | 2026-10-17 07:49 UTC | [M2] | SOL = $104.97 (page-level quote, not a live API) |
| S12 | ChainCatcher article page's live ticker (RootData widget) | <https://www.chaincatcher.com/en/article/2279071> | 2026-10-19 (fetch time) | [X2] | SOL = $105.15 (page-embedded ticker; weak, corroborative only) |
| S13 | Hindenrank — "How Does PumpSwap Work? Risk Analysis" | <https://hindenrank.com/blog/how-does-pumpswap-work> | updated 2026-02-26 | [X] | PumpSwap 0.25% fee (0.20/0.05), zero migration fee vs Raydium 6 SOL, CPMM, $1B+ daily volume at peak, shallow-liquidity/slippage/sandwich risk assessment, "most tokens decline 90%+ from graduation price" (assessment) |
| S14 | Blockchain News — "Pump.fun Memecoins See 68% Die on Launch Day, Study Finds" (CoinGecko study) | <https://blockchain.news/PostAMP?id=pump-fun-memecoins-lifespan-study> | 2026-06-23 | [M/news] | 18.67M tokens analysed; 68.67% last trade launch day; 80.37% ≤2 days; 4.55% >90 days; explicit caveat that metric excludes graduated tokens/only counts bonding-curve trades |
| S15 | Dune — "Pump.fun Post-Graduation Survival Curve" | <https://dune.com/queries/6774063> | accessed 2026-10-19 | pointer only | exists but JS-rendered; **numbers not readable** — cited as the gap / future-work target |
| S16 | Project-internal (not online): SPEC §9 recon in `tmp/v9_team/SPEC.md` | local file | 2026-10-19 | [internal] | cross-check only, labelled separately: v8 decisions 266 pumpswap, 21 quoted median cap ≈$50k, 8/21 ≥$69k; shadow-followed migrated p50 ≈1.70× (n=4, selection-biased). **Not** a substitute for `LOCAL_EVIDENCE.md`. |
| S17 | ChainCatcher via BlockBeats — "Has Pump's Bullet Hit the Bullseye, Is Solana's Story Over?" | <https://en.theblockbeats.news/news/57064> | 2025-02-27 | [S]/[M/news] | 2025-regime quote: "over 70% of meme coins displayed a 'peak upon pool creation' trend … average survival time of less than 48 hours"; on 2025-02-24 only one graduated token above $1M; confirms the $69,000 threshold was still being quoted in Feb-2025 (when SOL had hit $295 on 2025-01-19); SOL ATH/context |

Search queries used (web_search): pump.fun graduation rate statistics; graduation 85 SOL/411 SOL/$69000; PumpSwap migrations Dune; post-graduation performance; "do graduated tokens pump"; CoinGecko 90-day survival; BOOST/Mayhem; dev dump/bundles; PumpSwap fees; SOL price today. Scale of this work: **9 web_search calls (~22 queries) and ~30 web_fetch attempts**, of which about a dozen failed at the transport/Cloudflare layer (The Block, CoinGecko, DexScreener, pump.fun docs, madeonsol, AInvest, BingX, HTX, CoinMarketCap community pages). Failed fetches are excluded rather than paraphrased.

---

## 10. Method and limitations (read as part of the evidence)

* **Environment:** web_search + web_fetch only. **Direct HTTP APIs failed** — CoinGecko
  `/simple/price`, DexScreener `/latest/dex/tokens/...` and Binance `/ticker/price` all failed from both
  `web_fetch` and the PowerShell sandbox (connection closed) — so the SOL/USD conversion rests on
  page-level quotes (S11, S12) plus the Lead's measured $104. Blocker reported, not worked around.
* **pump.fun primary docs unreachable** (Cloudflare/JS; `/docs/mayhem-mode` and the docs root failed), and
  The Block's article page returned HTTP 403. Where a claim traces to those, the report cites the
  secondary summary that did load and says so (S9). The $69k origin is therefore supported by the 2024
  press record + curve arithmetic (S8 + S5), not by a pump.fun doc quote.
* **Dune dashboards are not readable** without a browser/API key; the one that would most directly answer
  the post-migration multiple question (S15) is listed as an unread pointer, not as evidence.
* **All measured numbers are as-reported by their sources.** I did not re-derive Bitquery's chain queries;
  Bitquery's own pages document method and limits (archive gaps, missing v2/v3 trade formats, pool records
  ending 2026-07-05, etc.), which are reproduced where they affect a number.
* **Selection of sources:** primary/measured first (Bitquery on-chain investigations, academic
  reconstructions, protocol mechanics), then news reporting of primary data (The Block via ChainCatcher,
  CoinGecko study via Blockchain News), then vendor/analyst opinion clearly labelled [X]. Marketing content
  from alert-tool vendors (S10) is used only to document the *propagation* of the $69k claim.
* **Dates:** research executed 2026-10-19 Asia/Shanghai; the freshest measured datasets end 2026-10-07
  (Bitquery) and 2026-10-15 (Bitquery buyer study). Anything older than ~3 months is tagged stale.
* **Not financial advice.** Nothing here is a recommendation to trade; the paper-trading engine's own
  pre-registered acceptance/kill criteria (SPEC §5) govern any decision.

---

*End of ONLINE_RESEARCH.md — task-2 deliverable of `web-research`. Companion document `LOCAL_EVIDENCE.md`
(owner: data-evidence) covers the project's own measured v8/v9 data and was not read or modified.*
