"""select_covered_cohort.py -- build the fully-observable training cohort
=======================================================================
The MELT pre-migration tape ends at each token's migration to Raydium, so the
post-decision price path ``[t0+300s, t0+3900s]`` is truncated for every token
that migrates inside the first hour.  That truncation is what leaves the
``train_gates_real.py`` policy study stuck at ``n_open > 0`` (the live exit
engine cannot close a trade whose tail series simply ends early).

We cannot download the 26 GB ``post_migration_tx.zip``, and free OHLCV APIs do
not retain minute-level history for these Dec-2024..Feb-2025 (mostly dead)
pump.fun mints.  So instead of fabricating a tail series, this script selects
the tokens whose *pre-migration* tape already spans the full decision+hold
horizon.  Their exit-rule replay closes on real data, unblocking the policy
study without any external price source.

Selection rule
--------------
A token is kept iff its last pre-migration print ``t_last`` satisfies::

    t_last >= t0 + OBS_WINDOW + HOLD_SEC        (t0 = first print timestamp)

because ``execution.advance`` only fires the ``holding limit`` exit when a mark
arrives at ``t_dec + HOLD_SEC = t0 + 3900``.  The ``label_token`` tape cap is
``ts <= t0 + 3900``, so a last print at >= 3900 guarantees a close.

Optionally the cohort is intersected with MELT ``label.csv`` so every kept row
carries a non-degenerate rug/pump target (unmatched mints are NaN targets and
are dropped by the chronological validator anyway).

Usage
-----
    python select_covered_cohort.py --csv melt_solana_trades.csv \
        --labels-csv melt_label.csv \
        --out melt_solana_trades_covered.csv

``melt_label.csv`` is a copy of MELT's own ``data/label/label.csv``; that file
works directly for ``--labels-csv`` too.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

# Mirrors synthetic_engine.OBS_WINDOW and historical_backtester.HOLD_SEC.
OBS_WINDOW = 300.0
HOLD_SEC = 3600.0
HORIZON = OBS_WINDOW + HOLD_SEC  # t0 + 3900


def _token_bounds(csv_path: Path):
    df = pd.read_csv(csv_path, usecols=["timestamp", "token_address"])
    df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
    g = df.groupby("token_address", sort=False)["timestamp"]
    t0 = g.min()
    t_last = g.max()
    return t0, t_last


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--csv", default="melt_solana_trades.csv")
    ap.add_argument("--labels-csv", default=None,
                    help="optional MELT label.csv to restrict the cohort to "
                         "tokens with a non-degenerate rug/pump target")
    ap.add_argument("--out", default="melt_solana_trades_covered.csv")
    ap.add_argument("--chunksize", type=int, default=1_000_000)
    args = ap.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"[!] not found: {csv_path}")
        return 2

    t0, t_last = _token_bounds(csv_path)
    span = t_last - t0
    covered = span >= HORIZON
    print(f"[i] {len(span)} tokens total; {int(covered.sum())} have "
          f"t_last >= t0 + {HORIZON:.0f}s")

    if args.labels_csv:
        lab = pd.read_csv(args.labels_csv, usecols=["mint_address"])
        lab_set = set(lab["mint_address"].astype(str))
        in_lab = t0.index.isin(lab_set)
        keep = set(t0.index[covered & in_lab])
        print(f"[i] of the covered tokens, {int((covered & in_lab).sum())} "
              f"are present in label.csv")
    else:
        keep = set(t0.index[covered])

    if not keep:
        print("[!] empty cohort")
        return 1

    # Stream the full CSV, emitting only the kept tokens.
    out_path = Path(args.out)
    wrote_header = True
    n_rows = 0
    n_tokens_written = set()
    for i, chunk in enumerate(pd.read_csv(csv_path, chunksize=args.chunksize)):
        sel = chunk[chunk["token_address"].astype(str).isin(keep)]
        if len(sel):
            sel.to_csv(out_path, mode="w" if wrote_header else "a",
                       header=wrote_header, index=False)
            wrote_header = False
            n_rows += len(sel)
            n_tokens_written.update(sel["token_address"].astype(str).unique())
        if (i + 1) % 20 == 0:
            print(f"[i] chunk {i + 1}: {n_rows} rows / "
                  f"{len(n_tokens_written)} tokens so far")

    print(f"[ok] wrote {n_rows} rows / {len(n_tokens_written)} tokens -> "
          f"{out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
