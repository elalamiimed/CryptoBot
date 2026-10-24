"""
melt_to_csv.py  -- MELT dataset -> trainer 7-column trade CSV
================================================================
Converts the MELT dataset (Georgia Tech, CC BY-NC 4.0) pre-migration
(bonding-curve) wallet-level pump.fun trades into the exact CSV schema the
trainer / backtester consume:

    timestamp, wallet, direction, sol_amount, token_amount,
    block_number, token_address

SOURCE -- MELT pre-migration transactions
------------------------------------------
https://github.com/git-disl/MELT

The parsed transactions live in ``MELT/data/tx/pre_migration_tx/`` as one
JSON-lines file per token, named ``<mint_address>.jsonl``.  Each line is one
on-chain transaction with:

    "type"        e.g. "mint", "swap", "mint&swap", "transfer", "zero"
    "timestamp"   unix seconds
    "price"       SOL per token at this swap
    "trader_map"  { wallet: signed_token_amount, ... }
    "signature"   transaction signature

Direction uses the sign of ``value``: positive = trader received tokens
(buy), negative = trader sent tokens (sell).  SOL notional is reconstructed
as ``abs(value) * price`` -- the same relation ``feat_gen.py`` uses when it
computes ``cost[trader] += value * abs(price)``.

Only rows whose ``type`` contains "swap" are emitted (mint / transfer / zero
rows are not trades).

``block_number`` is absent in MELT; the trainer only uses it as a secondary
sort key (see ``label_token``'s ``sort_values(["timestamp", "block_number"])``).
We therefore assign a monotonically increasing index per token in file order,
which preserves the launch -> migration chronology.

OUTPUT
------
  melt_solana_trades.csv            (append-mode, write-through per file)
  melt_solana_trades.csv.runs.json  fingerprint of every run that wrote it

The CSV is append-only, so re-running a command must not silently duplicate the
dataset into it.  Each run therefore records a fingerprint (input dirs, mints
file, limit, sample, seed, horizon, discovered file count) in the sidecar next
to the output, and a NON-EMPTY output is never appended to unless ``--force`` is
passed; the recorded fingerprints are what let the refusal say why (this exact
run already completed, a previous attempt of it was interrupted, or the file was
written by a different run).

RUN
---
Download the MELT dataset first (pre_migration_tx.zip is REQUIRED, bundle.zip
is NOT needed for this converter):

    https://drive.google.com/file/d/1rqzkaVoc1FG8XRp-hBxECjiG_PxAn5Cp/view

Unzip it so the JSON-lines files sit under ``MELT/data/tx/pre_migration_tx/``,
then:

    python melt_to_csv.py --tx-dir MELT/data/tx/pre_migration_tx

This checkout extracted ``pre_migration_tx.zip`` to ``./pre_migration_tx``, so
the working command here is:

    python melt_to_csv.py --tx-dir pre_migration_tx

The rug/pump targets are NOT derived here: MELT ships them ready-made in
``MELT/data/label/label.csv`` (columns ``mint_address``, ``label``,
``min_ratio``, ``return_ratio``, ``manipulated``), which
``train_gates_real.py --labels-csv`` consumes directly.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

import pandas as pd

CSV_SCHEMA = ["timestamp", "wallet", "direction", "sol_amount",
              "token_amount", "block_number", "token_address"]
# ``convert_merged`` appends this eighth column to mark which market a row
# belongs to.  The bonding curve and the DEX are two different markets, and the
# trainer has to know where the splice is: a price path that jumps 15x at the
# splice is not a market move, and an entry priced on one market may not be
# comparable with an exit priced on the other.  ``convert_file`` (pre-only runs)
# leaves the column out, so the 7-column schema is unchanged for those.
MERGED_SCHEMA = CSV_SCHEMA + ["source"]


def _f(v) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def tx_to_rows(tx: dict, token_address: str, block_number: int) -> Iterator[dict]:
    """Expand one MELT transaction line into zero or more 7-column rows.

    A single swap transaction may carry several traders in ``trader_map``;
    each (wallet, signed amount) pair becomes one row.
    """
    ttype = str(tx.get("type", ""))
    if "swap" not in ttype:
        return
    trader_map = tx.get("trader_map") or {}
    if not isinstance(trader_map, dict):
        return
    timestamp = _f(tx.get("timestamp"))
    price = abs(_f(tx.get("price")))
    for wallet, value in trader_map.items():
        v = _f(value)
        if v == 0.0:
            continue
        direction = "buy" if v > 0.0 else "sell"
        token_amount = abs(v)
        yield {
            "timestamp": timestamp,
            "wallet": str(wallet),
            "direction": direction,
            "sol_amount": token_amount * price,
            "token_amount": token_amount,
            "block_number": block_number,
            "token_address": str(token_address),
        }


def convert_file(path: Path) -> List[dict]:
    """Convert a single <mint>.jsonl file into schema rows (block_number = line idx)."""
    token_address = path.stem
    rows: List[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for block_number, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                tx = json.loads(line)
            except json.JSONDecodeError:
                continue
            rows.extend(tx_to_rows(tx, token_address, block_number))
    return rows


def convert_merged(pre_path: Path, post_path: Optional[Path], *,
                   horizon_s: Optional[float] = None) -> List[dict]:
    """Merge one token's bonding-curve tape with its 1-hour post-migration tape.

    The pre-migration tape ends at migration, which truncates the
    decision+hold path for every token that migrates inside it.  The
    post-migration tape carries the next hour of Raydium trading, so the two
    together cover the trainer's ``window + HOLD_SEC`` horizon without the
    survivorship filter ``select_covered_cohort.py`` has to apply.

    Rows are returned in chronological order with ``block_number`` renumbered
    per token so ``label_token``'s ``sort_values(["timestamp",
    "block_number"])`` stays meaningful.  ``horizon_s`` (measured from the
    first pre-migration swap) drops post-horizon rows that the trainer trims
    anyway, which keeps the merged tape small.
    """
    rows = convert_file(pre_path)
    for r in rows:
        r["source"] = "pre"
    if post_path is not None:
        post_rows = convert_file(post_path)
        base = (max((r["block_number"] for r in rows), default=-1) + 1)
        for i, r in enumerate(post_rows):
            r["block_number"] = base + i
            r["source"] = "post"
        rows.extend(post_rows)
    if not rows:
        return []
    rows.sort(key=lambda r: (r["timestamp"], r["block_number"]))
    if horizon_s:
        t0 = rows[0]["timestamp"]
        rows = [r for r in rows if r["timestamp"] <= t0 + horizon_s + 1e-9]
    for i, r in enumerate(rows):
        r["block_number"] = i
    return rows


def discover_files(tx_dir: Path) -> List[Path]:
    if not tx_dir.is_dir():
        raise SystemExit(f"[melt_to_csv] tx dir not found: {tx_dir}")
    # No ``Path.is_file()`` here on purpose: each one is an extra stat, and on
    # a cloud-synced directory ~46k of them can stall the run for hours.  The
    # directory listing already carries the names, and only the per-token
    # ``*.jsonl`` files can match the suffix.
    files = sorted(p for p in tx_dir.iterdir()
                   if p.suffix.lower() in (".jsonl", ".json", ".txt"))
    if not files:
        raise SystemExit(f"[melt_to_csv] no *.jsonl files found under {tx_dir}")
    return files


# --------------------------------------------------------------------------- #
# Append idempotency guard
# --------------------------------------------------------------------------- #
# EVIDENCE: main() appended to --out unconditionally, so re-running the same
# command duplicated the whole dataset into the same file with nothing on disk
# to show that it had happened.  The run fingerprint sidecar below is the record
# that makes a repeat visible; the guard refuses the append unless --force.
RUNS_SUFFIX = ".runs.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run_fingerprint(args, tx_dir: Path, post_dir: Optional[Path],
                    files: List[Path]) -> dict:
    """Identity of one conversion run: everything that decides what is written."""
    spec = {
        "tx_dir": str(Path(tx_dir).resolve()),
        "post_dir": str(Path(post_dir).resolve()) if post_dir else None,
        "mints": str(Path(args.mints).resolve()) if args.mints else None,
        "limit": int(args.limit),
        "sample": int(args.sample),
        "seed": int(args.seed),
        "horizon_s": float(args.horizon_s),
        "n_token_files": len(files),
    }
    spec["sha256"] = hashlib.sha256(
        json.dumps(spec, sort_keys=True).encode("utf-8")).hexdigest()
    return spec


def read_runs(guard_path: Path) -> List[dict]:
    """The recorded runs of one output file (an unreadable sidecar = no record)."""
    try:
        runs = json.loads(guard_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return [r for r in runs if isinstance(r, dict)] if isinstance(runs, list) else []


def write_runs(guard_path: Path, runs: List[dict]) -> None:
    guard_path.write_text(json.dumps(runs, indent=2), encoding="utf-8")


def guard_append(out_path: Path, guard_path: Path, fingerprint: dict,
                 force: bool) -> List[dict]:
    """Refuse an append that would duplicate rows already in ``out_path``.

    Returns the run log to append this run's record to.  ``--force`` bypasses
    the check (the record is still written, so the bypass stays visible).
    """
    runs = read_runs(guard_path)
    if force or not (out_path.exists() and out_path.stat().st_size > 0):
        return runs
    digest = fingerprint["sha256"]
    same = [r for r in runs if r.get("sha256") == digest]
    tail = "\n    pass --force to append anyway, or write to a fresh --out"
    if any(r.get("status") == "completed" for r in same):
        done = next(r for r in same if r.get("status") == "completed")
        raise SystemExit(
            f"[melt_to_csv] refused: {out_path} already contains this exact run "
            f"({done.get('rows', '?')} rows, completed "
            f"{done.get('finished_utc', '?')}); appending would duplicate it"
            + tail)
    if same:
        raise SystemExit(
            f"[melt_to_csv] refused: a previous attempt of this exact run was "
            f"interrupted (started {same[-1].get('started_utc', '?')}), so "
            f"{out_path} may already hold its prefix" + tail)
    if not runs:
        raise SystemExit(
            f"[melt_to_csv] refused: {out_path} is not empty and has no run "
            f"record in {guard_path.name}, so its provenance is unknown" + tail)
    known = ", ".join(sorted({f"{r.get('tx_dir')}@{r.get('sha256', '')[:8]}"
                              f"({r.get('status')})" for r in runs}))
    raise SystemExit(
        f"[melt_to_csv] refused: {out_path} was written by a different run "
        f"(this fingerprint {digest[:8]}); recorded: {known}" + tail)


def main(argv: Optional[Sequence[str]] = None) -> None:
    ap = argparse.ArgumentParser(description="MELT pre-migration tx -> trainer CSV")
    ap.add_argument("--tx-dir", required=True,
                    help="path to MELT/data/tx/pre_migration_tx")
    ap.add_argument("--out", default="melt_solana_trades.csv",
                    help="output CSV path (default: melt_solana_trades.csv)")
    ap.add_argument("--limit", type=int, default=0,
                    help="stop after this many token files (0 = all)")
    ap.add_argument("--post-dir", default=None,
                    help="MELT post_migration_tx_1hour; merges each token's "
                         "1-hour post-migration tape into the same rows")
    ap.add_argument("--mints", default=None,
                    help="text file of mint addresses (one per line) to keep")
    ap.add_argument("--sample", type=int, default=0,
                    help="randomly keep this many tokens (0 = all)")
    ap.add_argument("--seed", type=int, default=7, help="sampling seed")
    ap.add_argument("--horizon-s", type=float, default=0.0,
                    help="drop rows later than this many seconds after the "
                         "token's first swap (0 = keep everything)")
    ap.add_argument("--log", default=None,
                    help="append progress lines to this file (the sandboxed "
                         "launcher may swallow stdout)")
    ap.add_argument("--force", action="store_true",
                    help="append even when the run fingerprint recorded next to "
                         "--out says this exact run already completed, was "
                         "interrupted, or was a different run")
    args = ap.parse_args(argv)

    tx_dir = Path(args.tx_dir)
    files = discover_files(tx_dir)
    post_dir = Path(args.post_dir) if args.post_dir else None
    if post_dir is not None and not post_dir.is_dir():
        raise SystemExit(f"[melt_to_csv] post dir not found: {post_dir}")
    # One listing, then pure set lookups: a stat per token would be another
    # ~46k slow calls on a cloud-synced directory.
    post_stems = ({p.stem for p in post_dir.iterdir() if p.suffix == ".jsonl"}
                  if post_dir is not None else set())

    if args.mints:
        keep = {ln.strip() for ln in Path(args.mints).read_text(
            encoding="utf-8").splitlines() if ln.strip()}
        files = [fp for fp in files if fp.stem in keep]
    if args.sample > 0:
        import random
        rng = random.Random(args.seed)
        files = sorted(rng.sample(files, min(args.sample, len(files))))
    if args.limit > 0:
        files = files[: args.limit]

    # Refuse an append that would duplicate rows already in --out (see
    # guard_append).  This happens BEFORE the log file is opened and before a
    # single row is written, so a refused run leaves the output untouched.
    out_path = Path(args.out)
    guard_path = out_path.with_name(out_path.name + RUNS_SUFFIX)
    fingerprint = run_fingerprint(args, tx_dir, post_dir, files)
    runs = guard_append(out_path, guard_path, fingerprint, args.force)
    run_record = dict(fingerprint, out=str(out_path.resolve()), status="running",
                      rows=0, started_utc=_utc_now())
    runs.append(run_record)
    write_runs(guard_path, runs)

    log_fh = None
    if args.log:
        log_fh = Path(args.log).open("a", encoding="utf-8", buffering=1)

    def log(msg: str) -> None:
        print(msg, flush=True)
        if log_fh is not None:
            log_fh.write(msg + "\n")

    wrote_header = not out_path.exists() or out_path.stat().st_size == 0
    horizon = args.horizon_s if args.horizon_s > 0 else None

    log(f"[melt_to_csv] {len(files):,} token files; post_dir={post_dir}; "
        f"horizon_s={horizon}; out={out_path}")
    total_rows = 0
    n_merged = 0
    for i, fp in enumerate(files, 1):
        if post_dir is not None:
            post_fp = post_dir / f"{fp.stem}.jsonl" if fp.stem in post_stems else None
            if post_fp is not None:
                n_merged += 1
            rows = convert_merged(fp, post_fp, horizon_s=horizon)
        else:
            rows = convert_file(fp)
        if not rows:
            continue
        df = pd.DataFrame(rows, columns=(MERGED_SCHEMA if post_dir is not None
                                         else CSV_SCHEMA))
        df.to_csv(out_path, mode="a", header=wrote_header, index=False)
        wrote_header = False
        total_rows += len(rows)
        if i % 200 == 0 or i == len(files):
            log(f"[melt_to_csv] {i}/{len(files)} tokens, {total_rows:,} rows "
                f"({n_merged:,} with a post tape)")

    run_record.update(status="completed", rows=total_rows,
                      finished_utc=_utc_now())
    write_runs(guard_path, runs)
    log(f"[melt_to_csv] done: {total_rows:,} rows -> {out_path} "
        f"(run {fingerprint['sha256'][:8]} recorded in {guard_path.name})")
    if log_fh is not None:
        log_fh.close()


if __name__ == "__main__":
    main()
