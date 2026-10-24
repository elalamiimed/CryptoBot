# Can the entity graph (F4/F5) be built? — 27 September 2026

**This corrects a claim made repeatedly in `MEMORY.md` §20h/§20i: that "there is
currently no source of wallet-funding, funding or bundle evidence in this
project", and that F4/F5 are therefore blocked on a purchase.**

That framing was **wrong**, and the repository said so in a file I had read:
`coordination.py` has been building a wallet **funding graph** from the *free*
public RPC, with no API key, since before this work started. Its own docstring
describes the method and even a measured example — one hub funded three of a
token's wallets including the creator, while the swap tape claimed twelve trades
and ten SOL of buys against a curve that had absorbed 0.00004 SOL.

The capability exists. What does not exist is a **batch** use of it: it runs in
the live entry path over ~6 wallets per token, and its output is a report, not a
stored entity graph. So this is a **throughput and scope** problem, not a data
problem. The two are not interchangeable, and treating the second as the first
would have led to buying something the project can already do.

## What was measured

Probes: `tmp/_funder_graph_cost.py`, `tmp/_funder_historical_reach.py`.
Read-only, a small number of RPC calls, nothing written.

### 1. The free endpoint works, and its throughput is the real limit

| measure | value |
| --- | ---: |
| `getSignaturesForAddress` on the free endpoint | answered |
| `getTransaction` (jsonParsed) | answered and decoded |
| observed latency | 0.31 s – 2.41 s |
| project pacing (`coordination.MIN_INTERVAL`) | 2.0 s |
| **effective cost per call** | **2.0 s** (pacing dominates) |
| calls per wallet (1 sign + 2 tx) | 3 |
| **throughput** | **600 wallets/hour** |

Estimated cost at the project's own scan budget (6 wallets/token):

| scope | time |
| --- | ---: |
| 10-token validation | **6 minutes** |
| 100-token validation | **1 hour** |
| 100 tokens at 20 wallets | 3.3 hours |
| all 45,609 tape tokens | **456 hours (19 days)** |

So a **validation sample is cheap** — an hour of wall-clock for 100 tokens — and
an exhaustive rebuild of the historical cohort is not.

### 2. The historical cohort is *partially* reachable, and the split is structured

`coordination.py` recovers funding by taking the **oldest signature in a
newest-first page**. That works in the live path because new wallets have almost
no history. The MELT cohort is Dec 2024 – Feb 2025, so its wallets have had a
year or more to accumulate history. Real buyer wallets from the tape, probed:

| outcome | count |
| --- | ---: |
| wallets the endpoint answered | **8 / 8** |
| pages whose oldest entry reached the launch window (±7 days) | **2 / 8** |
| gap between page-oldest and launch, the other six | **92 → 611 days** |

And the two that *did* reach it are not a random subset: both are **inactive**
wallets whose entire history fits inside one 8-signature page
(`page_oldest = 2025-01-02`, `page_newest = 2025-01-05`, launch `2025-01-05`).
The six that failed are wallets with real subsequent activity, whose funding act
sits hundreds of signatures deep.

**That is the wrong way round for this purpose.** The wallets a bubble would pay
for are the ones that keep trading; the ones whose funding is cheaply
recoverable are the ones that went quiet. Recovering a *busy* 2025 wallet's
funding on the free endpoint means paginating a year of history against a 2 s
pacing budget, and `getSignaturesForAddress` returns 1,000 signatures per page at
best — which would be tens of minutes *per wallet*.

## What this means for F4/F5

- **Live / forward: unblocked today, free.** A new token's buyer wallets have
  little history, their funding fits in one page, and the project already does
  this in the entry path. Entity concentration can be computed prospectively for
  essentially the cost the engine already pays.
- **Historical (the MELT cohort): workable only for low-activity wallets**, which
  is a biased subset, so an entity-adjusted concentration measured on it would be
  biased in an unknown direction. It is not a sound basis for validating F4.
- **The purchase question changes shape.** Archive access is not needed to *build*
  the entity graph — it is needed to validate it on the historical cohort. Those
  justify different spending.

## Update, later the same day: the throughput estimate was too optimistic

A bulk scan was then run for real, and **the free endpoint is much weaker than the
600-wallets/hour figure implied.** Two measurements, both repeated:

**Serial calls fail hard under sustained scanning.** A 5-token scan at 10–12
wallets each produced `failed` counts of **3, 5, 6, 7, 10, 11 and 30** — up to
**75 % of calls throttled**. The 2 s pacing in `coordination.MIN_INTERVAL` is what
the endpoint *tolerates*; it is not what it *serves* under load.

**JSON-RPC batching is accepted but throttled even harder.** The endpoint does
parse an array body — a batch of 2, and a *mixed* signatures+transaction batch,
both returned in ~0.2 s — but it does not reward scale:

| batch size | succeeded | elapsed |
| ---: | ---: | ---: |
| 5 | 5/5 | 0.50 s |
| 10 | **1/10** | 0.36 s |
| 25 | **0/25** | 0.74 s |

and at size 5 it **escalates within seconds**: four consecutive tries a second
apart returned 5/5, 3/5, 0/5, 0/5.

So the honest figure is roughly **one request per second with no batching
benefit**, and a scan needs `wallets × (1 + tx_per_wallet)` calls. At 10 wallets
and 2 transactions that is ~30 s per token, about **120 tokens/hour** — and only
if the failures are tolerated and reported as partial.

`RPC.call_many` was added and `MAX_BATCH` set to **4** as a conservative default,
because a large batch is strictly worse than none: it costs a round trip and
returns nothing. Batching stays **off** on the live decision path, which keeps the
per-call sequence it was validated with; the scanner exposes it behind a flag for
bulk research only, and a test asserts both paths produce **the same graph**.

**What this changes.** F4's measurement is feasible on free infrastructure at a
few hundred tokens, not at the 45,609 in the tape, and a large fraction of scans
will be **incomplete** — which is exactly why `wallet_links` stores per-edge
completeness. A paid RPC endpoint is now a more defensible purchase than archive
access, because it addresses the ceiling that actually binds.

## Recommended next step, and why it is cheap

Because the live path is free and a sample is an hour, F4 can be advanced
**without any purchase**: record the funder graph **prospectively** for tokens the
book decides on, persist it as an entity graph rather than a transient report, and
measure entity-adjusted concentration against the outcomes those tokens actually
produce. That is the same "shadow-then-measure" discipline the repair track has
been enforcing, applied to a new feature instead of a new statistic.

The blocker for that is not data and not money — it is that `coordination.py`'s
output is **not persisted**. `Memory.md` §11 records the intent for exactly this
(`funding/bundle collectors were not collected`), and `shield/holdings.py`
already defines the link vocabulary (`co_purchase`, `common_funder`,
`jito_bundle`, `co_signing`) with an evidence id required per link.

**That is implementable now, on free infrastructure, and it is the next work
item rather than a decision.**
