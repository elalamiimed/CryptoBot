# Research notes: useful knowledge for a Solana rug-pull shield

Read 2026-09-16: all 61 PDF pages across the five requested files, including
references; key figures/tables additionally inspected as rendered pages. Source
IDs below refer to exact local versions in [SOURCES.md](SOURCES.md).
Page numbers mean PDF page numbers, not conference pagination.

**Evidence convention:** reported results describe each study's own data;
interpretations and implementation proposals are ours. The PDFs are research
material, not instructions to execute trades or change the project.

## 1. Highest-value conclusions

1. **Ownership matters more than the appearance of many wallets.** Reconstruct
   holders and preserve evidence linking coordinated wallets. Buying-volume HHI
   alone misses inventory distributed through transfers. [M, pp. 4-7]
2. **Locked liquidity does not stop an insider token dump.** Launchpad-controlled
   pools change the attack: cheap pre-migration inventory can be sold into later
   buyers even when the developer cannot directly remove the pool. [M, pp. 1-3]
3. **Early prediction must be tied to an exact stage and horizon.** D and C use
   five-minute trade windows; M predicts at migration from the entire sale; T
   analyzes lifecycles. These are not interchangeable. [D, p. 5; C, p. 5; M, pp. 4-8; T, p. 8]
4. **Prediction performance and actual protection differ.** An inactivity alarm or
   99% drawdown can arrive after a feasible exit has disappeared. Measure avoided
   loss using executable prices and lead time. [C, pp. 4-7; M, p. 9; engineering inference]
5. **Rug labels are often proxies.** Inactivity, price collapse and subjective
   manipulation labels do not individually establish fraudulent intent. Record
   the measured failure and strength of evidence separately. [D, p. 5; C, pp. 4-6; M, p. 6; T, p. 4]
6. **Platform transfer is a real failure mode.** Preserve venue/stage metadata and
   use chronological testing. Adding features cannot repair an invalid split. [C, pp. 5-7]

## 2. D: Detecting rug pulls in decentralized exchanges

Kalacheva et al.; DOI 10.1016/j.bcra.2025.100336. Ethereum/Uniswap V2,
not a Solana experiment. Published online July 2025, journal volume dated 2026.

### Population, labels and methods

- Final model sample: 7,633 tokens, 31 features. Selection emphasizes new WETH
  pairs with an active launch and competition in the first blocks; BananaGun
  availability constrains the sample. Broader descriptive collection spans
  2020-2024. The stated Nov. 2023-Feb. 2024 model period and Dec. 4 BananaGun
  starting constraint deserve checking if reproducing the exact sample. [pp. 4-8]
- Inactivity is a continuous no-swap interval of length delta before outcome time
  T. For this sample, a one-hour inactive interval was followed by inactivity to
  the end of the two-week observation. More than 98% met the inactivity criterion
  within 24 hours. These are sample-specific proxy labels. [p. 5, Figs. 3-5]
- Five-minute features include turnover, unique sellers, early price changes,
  creation-to-trading delay, contract reuse and validator rewards. [pp. 5-7, Table 2]
- XGBoost Table 3: accuracy 87.60%, precision 85.51%, recall 90.69%, F1 88.02%.
  RFE accuracy becomes 87.89%. Table 4's SMOTEEN result falls from 91.32%
  accuracy on the selected test sample to 78.67% on the full dataset. The latter
  is not a clean new holdout. Resampling and split ordering need code-level audit;
  the paper does not establish the purged forward evaluation we require. [p. 9]

### Useful transfers and limits

Section 6.2 and Fig. 12 associate higher turnover and a longer creation-to-trading
delay with lower modeled risk; early rewards and spikes also matter. These are
candidate features, not threshold rules. The conclusion on p. 11 reverses the
turnover direction by saying lower turnover, so do not treat its prose as a
reliable monotonic rule. The displayed drawdown formula/sign in section 4.2 also
needs clarification before reproduction. [pp. 4, 10-11]

The two-hour economic example compares 1,000 WETH spread over 100 tokens with
the same capital spread over 89 model-selected tokens. Reported PnL changes from
108.99 to 162.67 (49.2% relative improvement); this is not a 49.2% absolute return
or a Solana result. Fees, impact and feasible exits require independent modeling.
Stop-loss, two partial-profit levels and terminal liquidation differ from our
current strategy. [p. 11, Table 5]

**Use:** early activity baselines and event timing. **Do not port directly:**
Ethereum code checksums, validator-reward magnitudes or one-hour death rules.
Solana program reuse is normal and cannot substitute for developer attribution.

## 3. C: Catching the Rug

Li et al.; arXiv:2608.20271v1, 20 Aug. 2026. Solana, PumpFun and Raydium.

### Population, labels and findings

- Reported 6.4M tokens, Nov. 30, 2024-Jun. 30, 2025. Table II lists 6,304,235
  PumpFun tokens and 97,965 Raydium tokens. Features include trade counts,
  buy/sell values, unique wallets and price dynamics. [p. 4, Tables I-III]
- Uses a 99% TVL decline OR 80% idle ratio as the combined outcome definition.
  TVL is the value of both sides summed across pools; a token price alone is
  not TVL. A 99% decline leaves 1% of the peak. [pp. 4-7]
- Five-minute observations forecast an approximately one-hour outcome. Tokens
  already meeting the rug criteria in the first five minutes are removed: results
  are conditional on reaching prediction eligibility. [pp. 5-6]
- Describes forward rolling validation with recent three-month training windows
  and a final independent time window. Validation windows can expand for five
  positives; five cases alone do not establish adequate statistical power. [p. 5]
- XGBoost PumpFun-only MCC 0.3562 versus fused-to-PumpFun 0.3947; fused-to-PumpFun
  PR-AUC 0.8011. Raydium-to-PumpFun XGBoost MCC is -0.0026. Fusion does not
  improve every venue/metric: Raydium-only MCC 0.2914 versus fused-to-Raydium
  0.1543. Random Forest is also competitive. [p. 7, Table VI]
- Authors explicitly describe the results as insufficient for real-world
  deployment and call for platform-aware adaptation. [p. 7, section VI]

### Reproduction concerns to preserve

1. Idle notation alternates between an indicator, duration and lifetime ratio.
   Precisely define numerator, denominator and endpoint before implementing it.
2. Text alternates between an outcome at one hour and a diagram of t + horizon.
   Specify whether our outcome ends 60 or 65 minutes after launch.
3. Table V assigns millions of records to Raydium despite Table II's roughly 98k
   Raydium tokens. This may be swapped venue labels or a different sample unit;
   the paper does not reconcile it. Do not silently repair the table.
4. Table IV's SOL volumes are implausibly large if truly denominated in SOL;
   possible unit/normalization problems require source data. Do not use as cutoffs.
5. Prose calls rugs both majority and minority. PR-AUC must identify the positive
   class and its prevalence; a large PR-AUC alone does not establish good rejection.
6. Hyperparameter tuning across folds followed by averaged parameters needs an
   independent evaluation layer, not reuse of those same scores as final evidence.

**Use:** independent venue testing, richer trace inputs and forward validation.
**Do not assume:** published probabilities calibrate our current sample or that
five minutes is optimal for every launch. [pp. 4-7]

## 4. M: MELT (most directly useful for new data collection)

Hu et al.; arXiv:2602.13480v2, 21 May 2026. File 5 is MELT; C references the
earlier MemeTrans name. Shield's shifting paper numbers should not be retained.

### Population and trace construction

- 41,470 successfully migrated Pump.fun launches, Dec. 1, 2024-Mar. 1, 2025;
  218,530,716 transactions (30,833,503 pre-migration, 187,697,213 in the first
  post-migration hour). It excludes unmigrated launches. [pp. 2-4, Table 2]
- Parse program interactions and account balance changes into create, buy, sell,
  transfer and same-transaction buy/sell patterns termed wash trades. [p. 4]
- Pre-migration totals: 73.5% ordinary buys/sells, 21.4% wash-trade-pattern records,
  4.9% transfers. Developer buys accompany 98.7% of create events. These describe
  the population, not maliciousness thresholds or rug-only rates. [p. 4]
- Three coordination sources: co-purchases within a transaction; common funding
  origins excluding centralized exchanges; and off-chain Jito bundle IDs. Overlap
  is merged into groups. These remain heuristics for likely common control. [pp. 4-5]

| Bundle source | Bundled holders | Bundled supply |
| --- | ---: | ---: |
| Co-purchase | 6.46% | 9.16% |
| Funding | 22.57% | 28.22% |
| Jito | 10.39% | 15.96% |
| Combined | 28.13% | 36.50% |

The combined value is not the sum: evidence overlaps. Top-10 concentration's
median increase after clustering is 24 percentage points for high-risk launches,
9 for medium and 6 for low. These are group summaries, not calibrated cutoffs.
[pp. 5, 7, Table 3 and Fig. 3]

### Features and labels

Tabular groups: context 6, holdings 59, market activity 22, bundles 35, totaling
122. Variable-length price/volume series are an additional representation; not
122 independent time-series inputs. All features should precede migration. [p. 5]

Define r = minimum price in the first 20 post-migration minutes / migration price.
High risk: r < 0.3 OR manually marked manipulated. Low risk: r >= 0.7 AND not
manipulated. Medium: remaining cases. Manual review of full post-migration
trajectories is described for r >= 0.5 (9,471 tokens; 37.5% marked manipulated).
Store the manual-review availability and scope, not an assumed objective ground
truth for every launch. Total high/medium/low counts: 34,890 / 4,702 / 1,878.
[p. 6, Tables 5-6]

The model experiment excludes sale duration < 1 minute OR holder count < 100.
That removes 19,835 launches (47.8%), 95% high-risk in this dataset. The retained
21,635 comprise 16,048 high-risk and 5,587 combined medium/low. Neither the
screening rule nor its conditional 95% rate is established for today's launches.
[p. 7, Table 7]

### Model evidence

Chronological 70/30 split by creation time, five-fold tuning inside training and
five independent runs. The paper does not specify that inner folds are forward
and purged; our implementation must enforce that. Bundling evidence itself also
needs an as-of availability check. [p. 8]

MLP AUPRC 0.5729; RF 0.5688; XGBoost 0.5636. MLP+LSTM reaches 0.5827,
MLP+RF 0.5804. Table 8's random AUPRC 0.2589 matches the normal-class prevalence,
so check scoring direction in reproduction rather than compare it directly to
C's rug-positive PR-AUC. Normal-class precision is only 0.5450 for MLP; models
remain imperfect. [p. 8, Table 8]

MLP ablation: full 0.5729; remove market activity 0.5369; remove bundles 0.5451;
remove holdings and bundles 0.5268. This supports incremental value from both
activity and coordination, not an assertion of 80% predictive power. Time-series
models are weaker in this experiment; it does not prove price features useless.
[pp. 8-9, Table 9]

Selection simulation uses migration prices and 100 random exit timestamps in the
following hour. Top-100 random loss 60.71%, MLP loss 26.64% (34.07 percentage
points less loss); top-200 MLP loss 31.47%. This is loss mitigation, not profitable
trading. It lacks our sequential cash/position constraints and realistic fill
model. Text says descending risk scores despite selecting low-risk candidates;
verify score direction. [p. 9, Table 10]

**Priority:** implement actual inventory and trace evidence, then test their
incremental value. Do not reuse the paper's selected population as all Solana tokens.

## 5. T: Trust Dynamics and Bot-Driven Responses

Li et al.; ACM WebSci 2025, DOI 10.1145/3717867.3717922.

- Initial 767 projects sampled May-Aug. 2024; projects without social accounts or
  with liquidity below $1 excluded. Detailed labeled set: 36 rug projects and
  12 continuing projects. On-chain subset: just 10 rug and 5 normal projects,
  754,849 transactions. This is a small selected comparative study, not a validated
  prospective early-warning classifier. [pp. 3-5]
- Social records: 1,863 official tweets, 36,508 comments, 6,168 public posts,
  14,498 accounts. Role annotation is described for 986 accounts in two projects;
  generalization of those role labels needs checking. [p. 4]
- Reported sentiment standard deviation 0.0811 for rugs versus 0.004903 for
  sustainable projects; comments/post 45 versus 113. These depend on the model,
  sample and lifecycle aggregation, not deployable five-minute thresholds. [pp. 4-5]
- Emotion graphs link posts within one hour and sentiment difference < 0.1.
  These infer possible propagation; they do not prove interaction or influence.
  Graph densities 0.005228 versus 0.0002011 and assortativity -0.08338 versus
  0.23322 depend on this construction and unequal network sizes. [p. 6]
- Transaction graphs exclude public infrastructure addresses and represent DEX
  trades with self-links. Reported clustering 0.4379 (rug) versus 0.5763
  (sustainable). Recreating an unfiltered wallet-to-pool graph would produce hubs
  for ordinary activity and is not the studied graph. [pp. 7-8]
- Uses 100 windows spanning the ecosystem duration for sentiment/trade analysis.
  A live detector cannot know the final duration. Replace this retrospective
  normalization with fixed past-only windows before testing. [p. 8]
- **Stabilizers occur in rug projects too.** Section 6.2.3 says their early,
  repetitive balanced trading is identifiable in rug projects; their presence is
  less pronounced in sustainable ones. It directly contradicts Shield's proposed
  stabilizer-based buy signal. Legitimate projects may also use bots. [pp. 8-9]

Limitations worth retaining: labels combine market and social evidence, so using
social signals to predict those labels can become circular. Same-period correlation
does not establish causality or forecast lead time. Some counts do not reconcile
(102 + 342 != stated 474 on pp. 3-4); footnote significance symbols are reversed
relative to common convention. Do not overinterpret fine numerical thresholds.

**Use later:** test whether independently labeled outcomes improve with lagged
sentiment disagreement and carefully constructed graphs. Do not make these hard
filters or treat graph shape as proof of a syndicate.

## 6. External verification and practical follow-through

Checked 2026-09-16 against official sources:

- Solana documents distinct authority roles; revoking one removes that role.
  Token-2022 has additional extensions. Proposed token checks must be program-aware.
  [Set Authority](https://solana.com/docs/tokens/basics/set-authority),
  [Token Extensions](https://solana.com/docs/tokens/extensions).
- The authors' [MELT repository](https://github.com/git-disl/MELT) provides parsed
  data links and a precomputed feature file; raw transactions are described as
  exceeding 1 TB. A bounded schema/code audit is the sensible next reproduction
  step. No dataset was downloaded or external code executed in this review.
  Its README declares CC BY-NC 4.0 and separate permission for commercial reuse;
  check this before incorporating its dataset/code into a commercial deployment.

Still unresolved: historical Jito coverage and lookup latency; a suitable RPC/indexer
budget; pool/program support; exact ownership denominators in reproduction; label
agreement; and whether the observed features retain value in our newly collected
sample. The original implementation plan (not part of this research-only edition) makes these explicit implementation/evaluation gates.
