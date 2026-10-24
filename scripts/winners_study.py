"""
winners_study.py  -- what distinguished the 1000x Solana memecoins of 2025-26?
==============================================================================
Case-control study over the universe assembled by winners_collector.py.

Definitions (transparent, two tiers)
------------------------------------
* Launchpad-born tokens (pump.fun / bonk.fun / LaunchLab) start on a bonding
  curve whose virtual reserves imply a launch market cap of ~28 SOL.  Their
  peak multiple from launch is therefore  ATH_mcap_SOL / 28, where
  ATH_mcap_SOL = ATH price x supply / SOL-USD on the ATH date.
      WINNER  : peak multiple >= 1000   (ATH mcap >= 28,000 SOL, ~$4-7M)
      CONTROL : peak multiple <  200    (listed, noticed, never a big runner)
      the 200-1000x band is excluded from the classifier (ambiguous)
* Non-launchpad tokens (TRUMP-style Meteora/Raydium launches) have no known
  launch cap; ATH/ATL from CoinGecko is only a LOWER bound on their multiple
  and they are reported separately, never mixed into the classifier.
* Era: ATH date in 2025-01-01 .. today.

Features (launch-time = knowable at t0; early-life = first hours; post-hoc =
descriptive only, never a predictor):
  launch-time : venue, socials present at creation (twitter/telegram/web),
                description length, name/symbol shape, narrative keyword
                flags, weekday / hour UTC, SOL price + 30-d SOL return at
                creation, creator's other listed coins
  early-life  : minutes to king-of-the-hill, graduated, minutes to graduation
  post-hoc    : days to ATH, ATH mcap, retention (mcap now / ATH), pairs,
                liquidity, DexScreener boosts, reply count

Price-path block (pump.fun 12-h candles, when the series starts at launch):
  days to 10x/100x/1000x, largest drawdown BEFORE the ATH, count of >= 50 %
  pre-ATH drawdowns, and a trailing-stop survival test (30/50/70/90 %) on
  12-h lows: would the rule have exited before the ATH, and at what multiple.

Population caveat: everything here is conditional on the token having been
listed on CoinGecko.  The base rate of 1000x among ALL launches is far lower
(graduation alone is ~0.2-0.6 %; see arXiv 2607.02823).  Adding the RED-PUMP
2026 launch population (Zenodo 22286914) as controls removes that bias.

Usage:  python winners_study.py [--raw winners_raw.json] [--min-winners 20]
Output: winners_1000x.csv, winners_study_report.md, winners_study.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import warnings
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

LAUNCH_MCAP_SOL = 28.0
WIN_MULT = 1000.0
CTRL_MULT = 200.0
ERA_START = "2025-01-01"

NARRATIVE = {
    "ai_agent": r"\b(ai|agent|gpt|llm|bot|neural|terminal|truth|sentient|claude|grok|deepseek|openai|robot)\b",
    "animal": r"\b(dog|doge|inu|shib|cat|kitty|frog|pepe|peng|penguin|duck|bear|bull|monkey|ape|hamster|goat|pig|hippo|moo|deng|wif|hat|bonk|puppy|kitten|squirrel|pnut|cow|fish|bird|rat|mouse|fox|wolf|lion|tiger)\b",
    "politics": r"\b(trump|maga|melania|biden|kamala|obama|elon|musk|doge|vance|potus|president|america|usa|political|barron|rfk|putin|xi)\b",
    "celeb_culture": r"\b(kanye|ye|drake|taylor|swift|messi|ronaldo|mrbeast|tate|kardashian|celebrity|meme|viral|tiktok|twitch|stream|kol|anime|waifu|jesus|god|cult|based|chad|gigachad|sigma|npc|wojak|retard|autist)\b",
    "finance_word": r"\b(coin|token|cash|money|dollar|usd|stable|bank|fund|capital|yield|fart|useless|worthless|nothing|zero|inflation|stock|nasdaq)\b",
    "official_brand": r"\b(official|inc|corp|dao|foundation|labs|protocol|network|chain)\b",
}


def _f(x, d=np.nan) -> float:
    try:
        v = float(x)
        return v if np.isfinite(v) else d
    except (TypeError, ValueError):
        return d


def _day(ts_ms) -> Optional[datetime]:
    if not ts_ms:
        return None
    try:
        return datetime.fromtimestamp(float(ts_ms) / 1000.0, tz=timezone.utc)
    except (TypeError, ValueError, OSError):
        return None


def _iso(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None


# --------------------------------------------------------------------------- #
# 1. flatten one raw record
# --------------------------------------------------------------------------- #
def venue_of(rec: dict) -> str:
    """Launch venue from the MINT SUFFIX, not from the pump.fun API: pump.fun
    now indexes externally created tokens too (TRUMP has a record), so "the
    API knows it" does not mean "born on the curve".  pump.fun mints carry the
    vanity suffix `pump` since mid-2024, bonk.fun mints `bonk`."""
    mint = rec.get("mint") or ""
    if mint.endswith("pump"):
        return "pumpfun"
    if mint.endswith("bonk"):
        return "bonkfun"
    dex = (rec.get("dexscreener") or {}).get("first_pair_dex") or ""
    if "launchlab" in dex:
        return "launchlab"
    return "other"


def flatten(rec: dict, creators: Dict[str, int]) -> dict:
    pf = rec.get("pumpfun") or {}
    ds = rec.get("dexscreener") or {}
    venue = venue_of(rec)
    launchpad = venue in ("pumpfun", "bonkfun", "launchlab")
    created = _day(rec.get("created_ms"))
    ath_dt = _iso(rec.get("ath_date"))
    ds_created = _day(ds.get("first_pair_created"))
    # a creation date AFTER the ATH is an indexing artefact (external token
    # added to pump.fun later): fall back to the earliest DexScreener pool
    if created and ath_dt and created > ath_dt + timedelta(days=1):
        created = ds_created if (ds_created and ds_created <= ath_dt + timedelta(days=1)) else None
    if not launchpad:
        pf = {}                    # never read launch metadata for external tokens
    supply = (rec.get("total_supply") or rec.get("max_supply")
              or rec.get("circulating_supply") or (1e9 if launchpad else np.nan))
    ath_mcap_usd = _f(rec.get("ath")) * _f(supply)
    # plausibility: no memecoin FDV above $20B; larger values are dust-print
    # ATHs on CoinGecko (flagged, and superseded by the candle path below)
    cg_ath_suspect = bool(launchpad and ath_mcap_usd > 20e9)
    sol_ath = _f(rec.get("sol_usd_ath"))
    ath_mcap_sol = ath_mcap_usd / sol_ath if sol_ath > 0 else np.nan
    mult_launch = ath_mcap_sol / LAUNCH_MCAP_SOL if launchpad else np.nan
    mult_cg = _f(rec.get("ath")) / _f(rec.get("atl")) if _f(rec.get("atl")) > 0 else np.nan
    mcap_now = _f(rec.get("market_cap"))
    text = " ".join(str(x or "") for x in (rec.get("name"), rec.get("symbol"),
                                            pf.get("description"))).lower()
    row = {
        "mint": rec.get("mint"), "cg_id": rec.get("cg_id"),
        "symbol": rec.get("symbol"), "name": rec.get("name"),
        "venue": venue, "launchpad": int(launchpad),
        "created": created, "created_day": rec.get("created_day"),
        "ath_date": ath_dt, "ath_year": ath_dt.year if ath_dt else np.nan,
        "ath_price": _f(rec.get("ath")), "supply": _f(supply),
        "ath_mcap_usd": ath_mcap_usd, "ath_mcap_sol": ath_mcap_sol,
        "mult_launch": mult_launch, "mult_cg_lb": mult_cg,
        "cg_ath_suspect": int(cg_ath_suspect),
        "mcap_now": mcap_now,
        "retention": (mcap_now / ath_mcap_usd) if ath_mcap_usd > 0 else np.nan,
        "days_to_ath": ((ath_dt - created).total_seconds() / 86400.0
                        if (ath_dt and created) else np.nan),
        # ---- launch-time (pump.fun metadata) ---------------------------- #
        "has_twitter": int(bool(pf.get("twitter"))) if pf else np.nan,
        "has_telegram": int(bool(pf.get("telegram"))) if pf else np.nan,
        "has_website": int(bool(pf.get("website"))) if pf else np.nan,
        "n_socials": (int(bool(pf.get("twitter"))) + int(bool(pf.get("telegram")))
                      + int(bool(pf.get("website")))) if pf else np.nan,
        "desc_len": len(str(pf.get("description") or "")) if pf else np.nan,
        "name_len": len(str(rec.get("name") or "")),
        "symbol_len": len(str(rec.get("symbol") or "")),
        "symbol_is_upper": int(str(rec.get("symbol") or "").isupper()),
        "name_non_ascii": int(any(ord(ch) > 127 for ch in str(rec.get("name") or ""))),
        "name_words": len(str(rec.get("name") or "").split()),
        "weekday": created.weekday() if created else np.nan,
        "hour_utc": created.hour if created else np.nan,
        "sol_usd_created": _f(rec.get("sol_usd_created")),
        "creator": pf.get("creator") if pf else None,
        "creator_listed_coins": creators.get(pf.get("creator"), 0) if pf else np.nan,
        # ---- early-life ---------------------------------------------- #
        "graduated": int(bool(pf.get("complete"))) if pf else np.nan,
        "min_to_koth": ((_f(pf.get("king_of_the_hill_timestamp")) - _f(rec.get("created_ms"))) / 60000.0
                        if pf and pf.get("king_of_the_hill_timestamp") and rec.get("created_ms") else np.nan),
        "min_to_graduation": ((_f(ds.get("first_pair_created")) - _f(rec.get("created_ms"))) / 60000.0
                              if pf and ds.get("first_pair_created") and rec.get("created_ms") else np.nan),
        # ---- post-hoc descriptors ------------------------------------- #
        "reply_count": _f(pf.get("reply_count")) if pf else np.nan,
        "n_pairs": _f(ds.get("n_pairs")), "liquidity_now": _f(ds.get("liquidity_usd_max")),
        "boosts": _f(ds.get("boosts")), "n_socials_now": len(ds.get("socials_now") or []),
        "n_candles_12h": _f(rec.get("n_candles_12h"), 0),
    }
    for k, pat in NARRATIVE.items():
        row[f"kw_{k}"] = int(bool(re.search(pat, text)))
    return row


# --------------------------------------------------------------------------- #
# 2. price-path block from the 12-h candles
# --------------------------------------------------------------------------- #
def path_features(candles: List[list], created: Optional[datetime]) -> dict:
    out = {"path_full": 0, "path_days": np.nan, "peak_mult_path": np.nan,
           "days_to_10x": np.nan, "days_to_100x": np.nan, "days_to_1000x": np.nan,
           "days_to_peak": np.nan, "max_dd_pre_ath": np.nan, "n_dd50_pre_ath": np.nan,
           "dd_post_ath": np.nan}
    out["max_dd_pre_ath_pess"] = np.nan
    for s_ in (0.3, 0.5, 0.7, 0.9):
        for suffix in ("", "_pess"):
            out[f"trail{int(s_ * 100)}_exit_mult{suffix}"] = np.nan
            out[f"trail{int(s_ * 100)}_survived{suffix}"] = np.nan
    if not candles:
        return out
    c = np.asarray(candles, dtype=np.float64)
    ts, o, h, l, cl = c[:, 0] / 1000.0, c[:, 1], c[:, 2], c[:, 3], c[:, 4]
    first_ts = datetime.fromtimestamp(ts[0], tz=timezone.utc)
    full = bool(created and (first_ts - created) <= timedelta(hours=36))
    out["path_full"] = int(full)
    out["path_days"] = (ts[-1] - ts[0]) / 86400.0
    base = o[0] if o[0] > 0 else (cl[0] if cl[0] > 0 else np.nan)
    if not np.isfinite(base) or base <= 0:
        return out
    mult_h = h / base
    i_peak = int(np.argmax(mult_h))
    out["peak_mult_path"] = float(mult_h[i_peak])
    out["days_to_peak"] = (ts[i_peak] - ts[0]) / 86400.0
    for m, key in ((10, "days_to_10x"), (100, "days_to_100x"), (1000, "days_to_1000x")):
        idx = np.flatnonzero(mult_h >= m)
        if idx.size:
            out[key] = (ts[idx[0]] - ts[0]) / 86400.0
    # Drawdowns before the ATH candle.  Within a 12-h bar the order of high
    # and low is unknown, so two bounds are reported:
    #   optimistic  : a bar's low is tested against the peak of PREVIOUS bars
    #                 (a bar that runs 1x -> 100x cannot stop itself out)
    #   pessimistic : a bar's low is tested against the running peak INCLUDING
    #                 its own high (assumes high first, then low)
    prev_peak = np.maximum.accumulate(np.concatenate(([base], h[:-1])))
    dd_opt = 1.0 - l[: i_peak + 1] / np.maximum(prev_peak[: i_peak + 1], 1e-30)
    run_max = np.maximum.accumulate(h[: i_peak + 1])
    dd_pes = 1.0 - l[: i_peak + 1] / np.maximum(run_max, 1e-30)
    out["max_dd_pre_ath"] = float(np.clip(dd_opt.max(), 0.0, 1.0)) if dd_opt.size else np.nan
    out["max_dd_pre_ath_pess"] = float(np.clip(dd_pes.max(), 0.0, 1.0)) if dd_pes.size else np.nan
    n50, in_dd = 0, False
    for d_ in dd_opt:
        if d_ >= 0.5 and not in_dd:
            n50 += 1
            in_dd = True
        elif d_ < 0.25:
            in_dd = False
    out["n_dd50_pre_ath"] = n50
    if i_peak < len(cl) - 1:
        out["dd_post_ath"] = float(1.0 - cl[-1] / h[i_peak])
    # Trailing-stop survival from the first candle, both bar orderings.
    for s_ in (0.3, 0.5, 0.7, 0.9):
        tag = int(s_ * 100)
        for mode in ("opt", "pess"):
            peak = base
            exit_mult = np.nan
            k_exit = None
            for k in range(len(h)):
                if mode == "pess" and h[k] > peak:
                    peak = h[k]
                if l[k] <= peak * (1.0 - s_):
                    exit_mult = float(peak * (1.0 - s_) / base)
                    k_exit = k
                    break
                if mode == "opt" and h[k] > peak:
                    peak = h[k]
            survived = int(k_exit is None or k_exit >= i_peak)
            suffix = "" if mode == "opt" else "_pess"
            out[f"trail{tag}_survived{suffix}"] = survived
            out[f"trail{tag}_exit_mult{suffix}"] = (exit_mult if np.isfinite(exit_mult)
                                                     else float(cl[-1] / base))
    return out


# --------------------------------------------------------------------------- #
# 3. stats helpers
# --------------------------------------------------------------------------- #
def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    den = 1 + z * z / n
    ctr = (p + z * z / (2 * n)) / den
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (ctr - half, ctr + half)


def rate_table(df: pd.DataFrame, col: str, label: str = "winner") -> List[dict]:
    rows = []
    for val, g in df.groupby(col, dropna=True):
        k, n = int(g[label].sum()), int(len(g))
        lo, hi = wilson(k, n)
        rows.append({"feature": col, "value": val, "n": n, "winners": k,
                     "winner_rate": k / n if n else np.nan, "ci_lo": lo, "ci_hi": hi})
    return rows


def bucket(series: pd.Series, edges: List[float], labels: List[str]) -> pd.Series:
    return pd.cut(series, bins=edges, labels=labels, include_lowest=True).astype(str)


# --------------------------------------------------------------------------- #
# 4. main
# --------------------------------------------------------------------------- #
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--raw", default="winners_raw.json")
    ap.add_argument("--candles", default="winners_candles_12h.jsonl")
    ap.add_argument("--era-start", default=ERA_START)
    ap.add_argument("--min-winners", type=int, default=20)
    ap.add_argument("--seed", type=int, default=42)
    ns = ap.parse_args(argv)

    raw = json.loads(Path(ns.raw).read_text(encoding="utf-8"))
    candles: Dict[str, list] = {}
    if Path(ns.candles).exists():
        for line in Path(ns.candles).read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
                candles[r["mint"]] = r.get("candles") or []
            except (ValueError, KeyError):
                continue
    creators: Dict[str, int] = {}
    for rec in raw.values():
        cr = (rec.get("pumpfun") or {}).get("creator")
        if cr:
            creators[cr] = creators.get(cr, 0) + 1

    rows = [flatten(rec, creators) for rec in raw.values()]
    df = pd.DataFrame(rows)
    df = df[df["ath_date"].notna()]
    df = df[df["ath_date"] >= pd.Timestamp(ns.era_start, tz="UTC")]
    # price path block
    pth = [path_features(candles.get(m, []), c) for m, c in zip(df["mint"], df["created"])]
    df = pd.concat([df.reset_index(drop=True), pd.DataFrame(pth)], axis=1)

    # Final peak multiple from launch: the candle path (first 12-h open = the
    # curve start) when it covers the launch, else the CoinGecko-based estimate;
    # CoinGecko ATHs flagged as implausible are only trusted via the path.
    df["mult_final"] = np.where(df.path_full == 1, df.peak_mult_path, df.mult_launch)
    df.loc[(df.cg_ath_suspect == 1) & (df.path_full != 1), "mult_final"] = np.nan
    df["mult_source"] = np.where(df.path_full == 1, "candle_path", "coingecko_ath")
    lp = df[(df.launchpad == 1) & df.mult_final.notna()].copy()
    lp["winner"] = (lp.mult_final >= WIN_MULT).astype(int)
    lp["control"] = (lp.mult_final < CTRL_MULT).astype(int)
    winners = lp[lp.winner == 1].sort_values("ath_mcap_usd", ascending=False)
    controls = lp[lp.control == 1]
    other = df[df.launchpad == 0].copy()
    other_lb = other[(other.mult_cg_lb >= WIN_MULT) & (other.mult_cg_lb <= 1e5)
                     & (other.ath_mcap_usd <= 20e9)].sort_values("ath_mcap_usd", ascending=False)

    rep: List[str] = []
    P = rep.append
    P("# Solana memecoin 1000x study (2025-2026)\n")
    P(f"_Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC from "
      f"{len(raw)} enriched tokens ({len(df)} with an ATH in the era)._\n")
    P("## Universe and definitions\n")
    P(f"- Launchpad-born tokens (pump.fun / bonk.fun / LaunchLab): **{len(lp)}**; "
      f"non-launchpad: {len(other)}.")
    P(f"- Peak multiple from launch = candle-path peak / first 12-h open when the "
      f"series starts at launch ({int((lp.mult_source == 'candle_path').sum())} tokens), "
      f"else ATH market cap in SOL / {LAUNCH_MCAP_SOL:.0f} SOL (bonding-curve virtual start; "
      f"{int((lp.mult_source == 'coingecko_ath').sum())} tokens).  "
      f"**Winners (>= {WIN_MULT:.0f}x): {len(winners)}**; "
      f"controls (< {CTRL_MULT:.0f}x, listed but never a big runner): {len(controls)}; "
      f"200-1000x band (excluded from the classifier): "
      f"{int(((lp.mult_final >= CTRL_MULT) & (lp.mult_final < WIN_MULT)).sum())}.")
    P(f"- Non-launchpad tokens with a CoinGecko ATH/ATL >= 1000 (lower bound only): "
      f"{len(other_lb)}.")
    P("- Population caveat: conditional on a CoinGecko listing.  Among ALL pump.fun "
      "launches the 1000x rate is orders of magnitude lower (graduation itself is "
      "~0.2-0.6 %, arXiv 2607.02823).\n")

    # ---- winners table ------------------------------------------------- #
    P("## The winners (top 40 by ATH market cap)\n")
    P("| # | symbol | venue | created | ATH date | ATH mcap (CG) | x from launch (* = candle path) | days to ATH | "
      "now / ATH | socials at launch | min to KOTH | min to grad |")
    P("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(winners.head(40).itertuples(), 1):
        soc = "".join(ch for ch, f in (("T", r.has_twitter), ("G", r.has_telegram),
                                       ("W", r.has_website)) if f == 1) or "-"
        P(f"| {i} | {r.symbol} | {r.venue} | {r.created_day or '?'} | "
          f"{r.ath_date:%Y-%m-%d} | ${r.ath_mcap_usd / 1e6:,.1f}M | {r.mult_final:,.0f}x{'*' if r.mult_source == 'candle_path' else ''} | "
          f"{r.days_to_ath:.0f} | {r.retention:.1%} | {soc} | "
          f"{'' if pd.isna(r.min_to_koth) else f'{r.min_to_koth:.0f}'} | "
          f"{'' if pd.isna(r.min_to_graduation) else f'{r.min_to_graduation:.0f}'} |")
    P("")
    if len(other_lb):
        P("### Non-launchpad tokens with >= 1000x lower bound (ATH/ATL on CoinGecko)\n")
        P("| symbol | venue (first pool) | created | ATH date | ATH mcap | ATH/ATL |")
        P("|---|---|---|---|---|---|")
        for r in other_lb.head(15).itertuples():
            P(f"| {r.symbol} | {r.venue} | {r.created_day or '?'} | {r.ath_date:%Y-%m-%d} | "
              f"${r.ath_mcap_usd / 1e6:,.1f}M | {r.mult_cg_lb:,.0f}x |")
        P("")

    # ---- descriptive: winners vs controls ------------------------------- #
    cc = lp[(lp.winner == 1) | (lp.control == 1)].copy()
    P("## Winners vs. listed controls: launch-time attributes\n")
    P(f"n winners = {int(cc.winner.sum())}, n controls = {int((cc.winner == 0).sum())}\n")
    P("| attribute | winners | controls | note |")
    P("|---|---|---|---|")
    def pct(s): return f"{s.mean():.0%}" if s.notna().any() else "n/a"
    def med(s, fmt="{:.0f}"): return fmt.format(s.median()) if s.notna().any() else "n/a"
    W, C = cc[cc.winner == 1], cc[cc.winner == 0]
    for lab, col, kind in [("twitter at launch", "has_twitter", "pct"),
                           ("telegram at launch", "has_telegram", "pct"),
                           ("website at launch", "has_website", "pct"),
                           ("any social at launch", None, "anysoc"),
                           ("description length (chars, median)", "desc_len", "med"),
                           ("name length (median)", "name_len", "med"),
                           ("creator has other listed coins", None, "serial"),
                           ("graduated", "graduated", "pct"),
                           ("minutes to king-of-the-hill (median)", "min_to_koth", "med"),
                           ("minutes to graduation (median)", "min_to_graduation", "med"),
                           ("weekend launch", None, "weekend"),
                           ("SOL/USD at launch (median)", "sol_usd_created", "med")]:
        if kind == "pct":
            P(f"| {lab} | {pct(W[col])} | {pct(C[col])} | launch-time |")
        elif kind == "med":
            P(f"| {lab} | {med(W[col])} | {med(C[col])} | |")
        elif kind == "anysoc":
            P(f"| {lab} | {pct(W.n_socials > 0)} | {pct(C.n_socials > 0)} | launch-time |")
        elif kind == "serial":
            P(f"| {lab} | {pct(W.creator_listed_coins > 1)} | {pct(C.creator_listed_coins > 1)} | listed coins only |")
        elif kind == "weekend":
            P(f"| {lab} | {pct(W.weekday >= 5)} | {pct(C.weekday >= 5)} | |")
    for k in NARRATIVE:
        P(f"| narrative: {k} | {pct(W[f'kw_{k}'])} | {pct(C[f'kw_{k}'])} | name/symbol/description keywords |")
    P("")

    # ---- winner rate by bucket (with Wilson CI) -------------------------- #
    P("## Winner rate by launch-time bucket (95 % Wilson CI)\n")
    cc["socials_bucket"] = cc.n_socials.map({0: "0", 1: "1", 2: "2", 3: "3"})
    cc["koth_bucket"] = bucket(cc.min_to_koth, [-1, 5, 30, 180, 1440, 1e9],
                               ["<5 min", "5-30 min", "0.5-3 h", "3-24 h", ">24 h"])
    cc["grad_bucket"] = bucket(cc.min_to_graduation, [-1, 30, 180, 1440, 10080, 1e9],
                               ["<30 min", "0.5-3 h", "3-24 h", "1-7 d", ">7 d"])
    cc["hour_bucket"] = bucket(cc.hour_utc, [-1, 5, 11, 17, 23], ["00-05", "06-11", "12-17", "18-23"])
    tables = []
    for col in ("socials_bucket", "koth_bucket", "grad_bucket", "hour_bucket", "venue"):
        tables += rate_table(cc, col)
    P("| feature | value | n | winners | winner rate | 95 % CI |")
    P("|---|---|---|---|---|---|")
    for t in tables:
        P(f"| {t['feature']} | {t['value']} | {t['n']} | {t['winners']} | "
          f"{t['winner_rate']:.0%} | {t['ci_lo']:.0%}-{t['ci_hi']:.0%} |")
    P("")

    # ---- regime: when were the winners born / when did they peak --------- #
    P("## Regime: winners by creation month and by ATH month\n")
    wm = winners.dropna(subset=["created"]).groupby(winners.created.dt.strftime("%Y-%m")).size()
    am = winners.groupby(winners.ath_date.dt.strftime("%Y-%m")).size()
    cm = controls.dropna(subset=["created"]).groupby(controls.created.dt.strftime("%Y-%m")).size()
    months = sorted(set(wm.index) | set(am.index) | set(cm.index))
    P("| month | winners created | controls created | winner share of listed launches | winners peaking (ATH) |")
    P("|---|---|---|---|---|")
    for m in months:
        w_, c_ = int(wm.get(m, 0)), int(cm.get(m, 0))
        share = f"{w_ / (w_ + c_):.0%}" if (w_ + c_) else "-"
        P(f"| {m} | {w_} | {c_} | {share} | {int(am.get(m, 0))} |")
    P("")
    P("_The 'winner share' column is among CoinGecko-listed launchpad tokens only; "
      "it shows regime dependence, not absolute odds._\n")

    # ---- ML: winners vs controls ---------------------------------------- #
    ml = {}
    feats_t0 = ["has_twitter", "has_telegram", "has_website", "n_socials", "desc_len",
                "name_len", "symbol_len", "symbol_is_upper", "name_non_ascii", "name_words",
                "weekday", "hour_utc", "sol_usd_created", "creator_listed_coins"] + \
               [f"kw_{k}" for k in NARRATIVE]
    feats_early = feats_t0 + ["graduated", "min_to_koth", "min_to_graduation"]
    pf_cc = cc[cc.venue == "pumpfun"].copy()
    P("## Classifier: 1000x winner vs. listed control (pump.fun-born, grouped CV)\n")
    if pf_cc.winner.sum() >= ns.min_winners and (pf_cc.winner == 0).sum() >= ns.min_winners:
        from sklearn.model_selection import GroupKFold
        from sklearn.metrics import roc_auc_score, average_precision_score
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        from sklearn.pipeline import make_pipeline
        from sklearn.impute import SimpleImputer
        from xgboost import XGBClassifier
        y = pf_cc.winner.to_numpy()
        groups = pf_cc.created.dt.strftime("%Y-%m").fillna("unknown").to_numpy()
        gkf = GroupKFold(n_splits=min(5, len(set(groups))))
        for name, feats in (("launch-time only", feats_t0), ("launch-time + early-life", feats_early)):
            X = pf_cc[feats].apply(pd.to_numeric, errors="coerce")
            oof = np.full(len(y), np.nan)
            oof_lr = np.full(len(y), np.nan)
            imps = []
            for tr, va in gkf.split(X, y, groups):
                if len(set(y[tr])) < 2:
                    continue
                spw = float(np.clip((y[tr] == 0).sum() / max((y[tr] == 1).sum(), 1), 1, 30))
                m = XGBClassifier(n_estimators=300, max_depth=3, learning_rate=0.05,
                                  subsample=0.8, colsample_bytree=0.8, min_child_weight=5,
                                  reg_lambda=5.0, scale_pos_weight=spw, tree_method="hist",
                                  random_state=ns.seed, n_jobs=4)
                m.fit(X.iloc[tr], y[tr])
                oof[va] = m.predict_proba(X.iloc[va])[:, 1]
                imp = m.get_booster().get_score(importance_type="gain")
                tot = sum(imp.values()) or 1.0
                imps.append({k: v / tot for k, v in imp.items()})
                lr = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                                   LogisticRegression(max_iter=2000, C=0.5, class_weight="balanced"))
                lr.fit(X.iloc[tr], y[tr])
                oof_lr[va] = lr.predict_proba(X.iloc[va])[:, 1]
            ok = ~np.isnan(oof)
            auc = roc_auc_score(y[ok], oof[ok]); pr = average_precision_score(y[ok], oof[ok])
            auc_lr = roc_auc_score(y[ok], oof_lr[ok])
            gain = pd.DataFrame(imps).mean().sort_values(ascending=False)
            # signed effects from a full-data logistic regression
            lr_full = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                                    LogisticRegression(max_iter=2000, C=0.5, class_weight="balanced"))
            lr_full.fit(X, y)
            coef = pd.Series(lr_full[-1].coef_[0], index=feats).sort_values()
            ml[name] = {"n": int(len(y)), "n_winners": int(y.sum()), "auc_xgb_oof": auc,
                        "pr_auc_xgb_oof": pr, "auc_logreg_oof": auc_lr,
                        "gain_share": gain.head(12).to_dict(),
                        "logreg_coef_std": coef.to_dict()}
            P(f"### {name}\n")
            P(f"n = {len(y)} (winners {int(y.sum())}), base rate {y.mean():.1%}, "
              f"grouped by creation month ({gkf.get_n_splits()} folds)")
            P(f"- XGBoost out-of-fold ROC-AUC **{auc:.3f}**, PR-AUC {pr:.3f} (base {y.mean():.3f})")
            P(f"- Logistic regression out-of-fold ROC-AUC {auc_lr:.3f}\n")
            P("| feature | XGB gain share | logreg coef (std, + = more likely 1000x) |")
            P("|---|---|---|")
            for k in gain.head(12).index:
                P(f"| {k} | {gain[k]:.0%} | {coef.get(k, np.nan):+.2f} |")
            P("")
    else:
        P(f"_Not enough labelled pump.fun tokens yet (winners {int(pf_cc.winner.sum())}, "
          f"controls {int((pf_cc.winner == 0).sum())}; need >= {ns.min_winners} each)._\n")

    # ---- price path of winners ------------------------------------------ #
    P("## Price path of the winners (pump.fun 12-h candles)\n")
    wp = winners[winners.path_full == 1]
    P(f"Winners whose candle series starts at launch (full path): **{len(wp)}** of "
      f"{len(winners)} (the rest were created before ~May 2025; only their later path is available).\n")
    if len(wp):
        def q(s, f="{:.1f}"):
            s = s.dropna()
            return (f.format(s.quantile(0.25)) + " / " + f.format(s.median()) + " / " + f.format(s.quantile(0.75))) if len(s) else "n/a"
        P("| metric (p25 / median / p75) | winners with full path |")
        P("|---|---|")
        P(f"| days to 10x from first candle | {q(wp.days_to_10x)} |")
        P(f"| days to 100x | {q(wp.days_to_100x)} |")
        P(f"| days to 1000x | {q(wp.days_to_1000x)} (reached by {int(wp.days_to_1000x.notna().sum())}) |")
        P(f"| days to peak | {q(wp.days_to_peak)} |")
        P(f"| peak multiple on the candle path | {q(wp.peak_mult_path, '{:,.0f}x')} |")
        P(f"| largest drawdown BEFORE the ATH (low vs previous bars' peak; optimistic) | {q(wp.max_dd_pre_ath, '{:.0%}')} |")
        P(f"| largest drawdown BEFORE the ATH (low vs running peak incl. own bar; pessimistic) | {q(wp.max_dd_pre_ath_pess, '{:.0%}')} |")
        P(f"| number of >= 50 % drawdowns before the ATH | {q(wp.n_dd50_pre_ath, '{:.0f}')} |")
        P(f"| drawdown from ATH to now | {q(wp.dd_post_ath, '{:.0%}')} |")
        P("")
        P("### Would a trailing stop have held a 1000x? (stop tested on 12-h lows from the first candle)\n")
        P("| trailing stop | still holding at the ATH (optimistic / pessimistic bar order) | median exit multiple (opt / pess) | p25 - p75 exit multiple (opt) |")
        P("|---|---|---|---|")
        for s_ in (30, 50, 70, 90):
            so, sp = wp[f"trail{s_}_survived"].mean(), wp[f"trail{s_}_survived_pess"].mean()
            eo, ep = wp[f"trail{s_}_exit_mult"].dropna(), wp[f"trail{s_}_exit_mult_pess"].dropna()
            P(f"| {s_} % | {so:.0%} / {sp:.0%} | {eo.median():,.0f}x / {ep.median():,.0f}x | "
              f"{eo.quantile(0.25):,.0f}x - {eo.quantile(0.75):,.0f}x |")
        P("")
        P("_Bounds from 12-h bars: 'optimistic' assumes each bar's low came before its high, "
          "'pessimistic' the reverse; the truth lies between them and intrabar wicks are "
          "invisible at this resolution._\n")

    # ---- interpretation -------------------------------------------------- #
    P("## Reading the results honestly\n")
    P("1. **Survivorship.** Every token here was listed on CoinGecko.  A launch-time "
      "attribute that separates 1000x winners from listed controls is a *necessary-but-"
      "not-sufficient* signal: it does not tell you the odds among the ~700k launches "
      "that were never listed.  The RED-PUMP-2026 launch population is the fix.")
    P("2. **What the launch itself can carry.** Socials at creation, a real description, "
      "a non-serial creator and a fast king-of-the-hill are the only things knowable in "
      "the first hour; the classifier's AUC above is the ceiling of what they explain.  "
      "The remainder -- narrative timing, KOL/CEX attention, the macro SOL regime -- is "
      "exogenous and arrives *after* the launch window.")
    P("3. **Exits.** The drawdown block is the part that transfers directly to the bot: "
      "if most 1000x paths contained a >= 50 % drawdown before the ATH, no trailing stop "
      "of 30-50 % can hold a 1000x, and only a cost-recovered moonbag (or a ladder) keeps "
      "any exposure to that tail.")
    P("")

    Path("winners_study_report.md").write_text("\n".join(rep), encoding="utf-8")
    cols = ["symbol", "name", "mint", "venue", "created_day", "ath_date", "ath_mcap_usd",
            "ath_mcap_sol", "mult_final", "mult_source", "mult_launch", "mult_cg_lb",
            "cg_ath_suspect", "days_to_ath", "retention",
            "has_twitter", "has_telegram", "has_website", "desc_len", "min_to_koth",
            "min_to_graduation", "creator", "creator_listed_coins", "reply_count",
            "path_full", "peak_mult_path", "days_to_10x", "days_to_100x", "days_to_1000x",
            "max_dd_pre_ath", "n_dd50_pre_ath", "trail30_survived", "trail50_survived",
            "trail70_survived", "trail90_survived"] + [f"kw_{k}" for k in NARRATIVE]
    winners[cols].to_csv("winners_1000x.csv", index=False)
    lp.to_csv("winners_launchpad_all.csv", index=False)
    Path("winners_study.json").write_text(json.dumps({
        "n_raw": len(raw), "n_era": int(len(df)), "n_launchpad": int(len(lp)),
        "n_winners": int(len(winners)), "n_controls": int(len(controls)),
        "n_other_lb": int(len(other_lb)), "rate_tables": tables, "ml": ml,
        "winners": winners[cols].astype(str).to_dict("records")},
        indent=1, default=str), encoding="utf-8")
    print("\n".join(rep))
    print(f"\n[ok] wrote winners_study_report.md, winners_1000x.csv, "
          f"winners_launchpad_all.csv, winners_study.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
