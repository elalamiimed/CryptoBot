# Entity graph: first real capture, 27 September 2026

**What this is.** The first time the funding graph has been captured from the
chain and stored. Everything before it was machinery that had never met reality:
`coordination.py` computed the edges and discarded them, and migration 6 added a
table to hold them. Probe: `tmp/_entity_graph_validate.py`.

**Result: the mechanism works, and the first measurement is null — which is the
useful part.** A concrete, fixable defect fell out of it.

## What ran

6 recent pump.fun tokens, buyer wallets from Bitquery's `realtime` DEXTrades,
funding scans against the **free** public RPC, edges stored through
`Importer.record_wallet_links` into `wallet_links`.

| measure | value |
| --- | ---: |
| tokens scanned | 6 |
| scans completed in full | 2 of 6 |
| `common_funder` edges found | 4 |
| edges stored | 4 (idempotent insert verified) |
| distinct hubs | 4 |
| **raw groups vs entity groups** | **24 vs 24** |
| **tokens with any merge** | **0** |
| mean HHI, raw and entity | 0.25 (unchanged) |

## The null result

Merging linked wallets changed nothing: 24 raw groups, 24 entity groups, zero
merges, HHI identical.

That is *not* evidence against the research claim. The sample is ~4 largest
buyers per token, equal-weighted, scanned over only their two oldest
transactions. At that size a cluster of two would be the only detectable effect,
and none appeared. The honest statement is: **the entity-merge effect is
invisible at this sample size**, and a real F4 experiment needs a materially
larger scan (the measured budget is 600 wallets/hour, so this is a cost decision,
not a blocker).

## The defect it exposed — and this one is actionable

Of the four hubs, **one `AxiomRXZAq…` funded wallets on TWO DIFFERENT TOKENS.**
A wallet that pays buyers of unrelated tokens is not a coordination hub; it is a
**service paying out withdrawals** — an exchange, bridge, router or trading bot.

The research this gate is built on removes known exchanges and services
*explicitly*. `linked_cluster` did not, so it would have merged wallets that
share nothing but their exchange. That is the same class of error as treating an
unfunded wallet as a singleton: **it manufactures a relationship out of an
infrastructure artefact.**

Two things were done about it, and they are deliberately different:

1. **`is_known_service()` and a `KNOWN_SERVICE_PREFIXES` denylist**, applied in
   `linked_cluster` so a service can never form a cluster. Kept deliberately
   short and prefix-matched: it is a denylist, so it can only ever *remove*
   edges. An unlisted service still produces false links, whereas a wrongly
   listed hub would hide a genuine one. It should grow from evidence — a hub that
   funds buyers of many unrelated tokens — not from guesswork.
2. **Service edges are still STORED, flagged `service: True`,** with evidence
   reading "…is a KNOWN SERVICE, so this is a withdrawal, not coordination".
   Dropping them silently would make a scan look empty; the edge is a fact about
   the chain, and only its *interpretation* differs.

## A second, separate limitation worth recording

**4 of 6 scans were incomplete** (`failed` counts of 3, 5, 6, 7, 10 against 6
wallets). The free endpoint rate-limits under a sustained scan, so a
funding-graph measurement is only as good as its completeness — which is exactly
why `wallet_links` stores `scan_scanned`, `scan_failed` and `scan_complete` per
edge rather than assuming a scan succeeded. Any concentration computed from these
rows must be reported as the **lower bound** it is.

## What is established, and what is not

**Established:** the capture path works end to end against mainnet — real hubs
detected, edges stored idempotently, service hubs identified. F4's input now
exists as data rather than as a computation that evaporates.

**Not established:** that entity merging raises concentration on this market.
One sample of 6 tokens at 4 wallets cannot show it either way, and reporting a
0.000 HHI uplift as if it settled the question would be the same error this
repair track has now corrected four times — a number read for more than it can
carry.

**Next measurement, in order of what it would settle:** raise wallets-per-token
toward the point where a cluster of 2–3 is plausible; then apply the entity metric
against **economic** outcomes, per `ECONOMIC_CHECK.md`, not against a
coordination label.
