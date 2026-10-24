# NOTICE — data provenance and third-party attribution

This repository is a research-only edition of a Solana memecoin research
project. It contains reports, derived datasets, provenance records and the
standalone scripts needed to reproduce the headline prize study. The
paper-trading engine, its execution/accounting code and its run directories are
not part of this repository.

## MELT dataset (CC BY-NC 4.0)

A substantial part of the fake-memecoin / rug-detection work uses the **MELT**
dataset:

> Hu et al., *MELT: A Behavioral Trace Dataset for High-Risk Memecoin Launch
> Detection*, arXiv:2602.13480v2 (2026).
> Dataset repository: <https://github.com/git-disl/MELT>

MELT is licensed under the **Creative Commons Attribution-NonCommercial 4.0
International Licence (CC BY-NC 4.0)**:
<https://creativecommons.org/licenses/by-nc/4.0/>

MELT-derived files redistributed here:

| File | What it is | Changes made |
| --- | --- | --- |
| `data/melt/melt_label.csv` | A copy of MELT's `data/label/label.csv` (41,470 labelled migrated launches) | None; byte-identical, SHA-256 recorded in `data/melt/melt_label_sha256.json` |
| `data/melt/corpus_files.tsv.gz` | Per-file manifest of the 91,402 raw corpus files (name, size, mtime) | Derived listing; gzip-compressed here |
| `data/melt/corpus_totals.json`, `data/melt/corpus_fingerprint.json` | Scale and fingerprint of the downloaded corpus | Derived |
| `data/melt/frame_meta.json`, `data/melt/frame_sha256.json` | Provenance and shape of the feature frame built from MELT | Derived |
| `data/melt/pre_migration_tx_sample200.sha256`, `data/melt/post_migration_tx_1hour_sample200.sha256` | Hashes of a 200-file sample of each raw tape | Derived |
| `data/melt/provenance/*.provenance.json` | Per-model provenance (label/frame hashes, cohort) | Derived |
| `data/melt/gate_policy_study.json` | Archive copy of the MELT-run policy study (development policy search + final metrics) | None; copy of the MELT archive |
| `data/models/melt_v5_witness/*` | Rug/pump classifiers and policy study trained on the MELT frame | Trained models / study outputs |
| `data/models/legacy/*` | Earlier models trained on a small locally collected sample | Legacy artifacts |

These MELT-derived files may **not** be used for commercial purposes.
Commercial reuse requires separate permission from the MELT authors. If you use
these files, cite MELT and this repository. The 89 GB raw corpus and the
1.735 GB feature frame are **not** redistributed; they are pinned by the hashes
above and must be re-downloaded from MELT to rebuild them.

## Public market data

The winners study and the graduation/migration study used public, key-less
endpoints: CoinGecko (token universe, ATH/ATL, SOL/USD), pump.fun (launch
metadata and 12-hour candles), DexScreener (earliest pool / venue / graduation)
and GeckoTerminal (forward post-migration OHLCV). No API keys or credentials are
included in this repository.

The per-token enriched snapshots `data/winners/winners_raw.json` and
`data/winners/winners_universe.json` are included so that the published winners
study can be recomputed without re-collecting moving public data. They were
collected for non-commercial academic research on 2026-09-14 and remain subject
to the providers' terms of service; they are not an official redistribution of
any provider's dataset. Other raw API caches and the large per-token scan outputs
(`atomic_scan.json`, `markout_scan.json`, replay/capacity scans) are **not**
included. Re-collection may be subject to rate limits and changing terms.

## Third-party papers

The documents reviewed in `docs/RESEARCH_NOTES.md` (four research papers and one secondary synthesis) are not redistributed.
`docs/SOURCES.md` records the citation metadata and SHA-256 hashes of the local
copies that were read; only summaries and analysis are included. Cite the
original papers, not this repository, for their results.

## Model artifacts

The `.joblib` files are Python pickle-based artifacts. Only load them from a
source you trust: deserialising a joblib file can execute arbitrary code.

## Not financial advice

Nothing in this repository is investment advice, and no profitability claim is
made or implied. The trading activity described in the reports was paper-only
(simulated); no live capital was deployed.
