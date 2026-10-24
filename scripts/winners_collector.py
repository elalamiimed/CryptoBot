"""
winners_collector.py  -- assemble the 2025-2026 Solana memecoin universe
=========================================================================
Key-less, resumable collector behind winners_study.py.  Builds ONE record per
token from four public sources and checkpoints after every token:

  1. CoinGecko  /coins/markets  for the categories `solana-meme-coins` and
     `pump-fun` (all pages): ATH / ATH date / ATL / supply / current mcap.
     CoinGecko keeps dead coins, so tokens that ran and died are included.
  2. CoinGecko  /coins/list?include_platform=true : Solana mint per coin.
  3. pump.fun   frontend-api-v3 /coins/{mint} : LAUNCH-TIME metadata for
     pump.fun-born tokens -- created_timestamp, socials present at creation,
     description, king-of-the-hill time, graduation flag, creator wallet.
  4. DexScreener /token-pairs/v1/solana/{mint} : earliest pool (venue +
     graduation time), pair count, current liquidity.
  5. pump.fun   swap-api  12-h candles (latest 1000 = ~500 days) : the whole
     life path for anything created after ~May 2025 (first candle = launch),
     the post-May-2025 path otherwise.  Used for time-to-ATH, drawdowns.
  6. CoinGecko  SOL/USD daily (365 d) + an approximate monthly table for
     earlier dates: converts ATH market cap to SOL so the "1000x" test can be
     made against the bonding-curve launch cap (28 SOL virtual start).

Why these and not the swap tape: GeckoTerminal's public API serves only the
last 180 days and only the newest ~300 swaps per pool; DexScreener no longer
lists the bonding-curve pool of graduated tokens.  Per-wallet launch tapes of
2025 tokens are not recoverable without a paid indexer.

Usage:  python winners_collector.py [--max-tokens N] [--out winners_raw.json]
        (re-run to resume; --refresh-universe rebuilds the CoinGecko list)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = {"User-Agent": "Mozilla/5.0 (research; CryptoBot winners study)",
      "Accept": "application/json"}
CG = "https://api.coingecko.com/api/v3"
PF = "https://frontend-api-v3.pump.fun"
PF_SWAP = "https://swap-api.pump.fun/v1/coins/{mint}/candles"
DS_PAIRS = "https://api.dexscreener.com/token-pairs/v1/solana/{mint}"
CATEGORIES = ("solana-meme-coins", "pump-fun")
ERA_START = "2025-01-01"

# Approximate monthly SOL/USD averages for dates older than CoinGecko's
# key-less 365-day window (only used to convert ATH mcap to SOL for 2024/
# early-2025 ATHs; +-20 % error moves a 1000x call only at the margin).
SOL_MONTHLY_USD = {
    "2024-01": 95, "2024-02": 105, "2024-03": 175, "2024-04": 160,
    "2024-05": 165, "2024-06": 150, "2024-07": 160, "2024-08": 150,
    "2024-09": 140, "2024-10": 160, "2024-11": 220, "2024-12": 215,
    "2025-01": 230, "2025-02": 175, "2025-03": 135, "2025-04": 130,
    "2025-05": 165, "2025-06": 150, "2025-07": 170, "2025-08": 190,
    "2025-09": 220,
}


class Http:
    """Paced GET with a per-source lock (safe to share across worker threads)."""

    def __init__(self, spacing: float) -> None:
        self.spacing = spacing
        self._last = 0.0
        self._lock = threading.Lock()
        self.n = 0
        self.n_fail = 0

    def _pace(self) -> None:
        with self._lock:
            dt = self.spacing - (time.monotonic() - self._last)
            if dt > 0:
                time.sleep(dt)
            self._last = time.monotonic()
            self.n += 1

    def get(self, url: str, params: Optional[dict] = None, retries: int = 3,
            ok404: bool = False):
        for attempt in range(retries + 1):
            self._pace()
            try:
                r = requests.get(url, params=params, headers=UA, timeout=30)
            except requests.RequestException:
                r = None
            if r is not None and r.status_code == 200:
                try:
                    return r.json()
                except ValueError:
                    return None
            if r is not None and r.status_code == 404 and ok404:
                return {"__404__": True}
            wait = 2.0 * (2 ** attempt)
            if r is not None and r.status_code == 429:
                ra = r.headers.get("Retry-After")
                try:
                    wait = max(wait, float(ra))
                except (TypeError, ValueError):
                    wait = max(wait, 20.0)
            time.sleep(min(wait, 90.0))
        self.n_fail += 1
        return None


def iso_day(ts_ms: Optional[float]) -> str:
    if not ts_ms:
        return ""
    return datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc).strftime("%Y-%m-%d")


# --------------------------------------------------------------------------- #
# 1-2. universe from CoinGecko
# --------------------------------------------------------------------------- #
def build_universe(cg: Http, out: Path) -> Dict[str, dict]:
    coins: Dict[str, dict] = {}
    for cat in CATEGORIES:
        for page in range(1, 20):
            data = cg.get(f"{CG}/coins/markets",
                          params={"vs_currency": "usd", "category": cat,
                                  "order": "market_cap_desc", "per_page": 250,
                                  "page": page, "sparkline": "false"})
            if not data:
                break
            for c in data:
                cid = c.get("id")
                if not cid:
                    continue
                rec = coins.setdefault(cid, {"cg_id": cid, "categories": []})
                if cat not in rec["categories"]:
                    rec["categories"].append(cat)
                rec.update({
                    "symbol": c.get("symbol"), "name": c.get("name"),
                    "market_cap": c.get("market_cap"),
                    "fdv": c.get("fully_diluted_valuation"),
                    "total_supply": c.get("total_supply"),
                    "max_supply": c.get("max_supply"),
                    "circulating_supply": c.get("circulating_supply"),
                    "current_price": c.get("current_price"),
                    "ath": c.get("ath"), "ath_date": c.get("ath_date"),
                    "atl": c.get("atl"), "atl_date": c.get("atl_date"),
                    "total_volume": c.get("total_volume"),
                })
            print(f"  [cg] {cat} page {page}: {len(data)} coins "
                  f"(universe {len(coins)})", flush=True)
            if len(data) < 250:
                break
    print("  [cg] resolving Solana mints via /coins/list ...", flush=True)
    lst = cg.get(f"{CG}/coins/list", params={"include_platform": "true"}) or []
    mint_of = {x["id"]: (x.get("platforms") or {}).get("solana")
               for x in lst if isinstance(x, dict)}
    for cid, rec in coins.items():
        rec["mint"] = mint_of.get(cid) or ""
    n_mint = sum(1 for r in coins.values() if r["mint"])
    print(f"  [cg] universe {len(coins)} coins, {n_mint} with a Solana mint",
          flush=True)
    out.write_text(json.dumps(coins, indent=1), encoding="utf-8")
    return coins


def sol_prices(cg: Http) -> Dict[str, float]:
    data = cg.get(f"{CG}/coins/solana/market_chart",
                  params={"vs_currency": "usd", "days": "365", "interval": "daily"})
    out = {}
    for ts_ms, px in (data or {}).get("prices", []):
        out[iso_day(ts_ms)] = float(px)
    return out


def sol_usd_on(day: str, daily: Dict[str, float]) -> Optional[float]:
    if not day:
        return None
    if day in daily:
        return daily[day]
    # nearest earlier daily point within 7 days
    try:
        d = datetime.strptime(day, "%Y-%m-%d")
    except ValueError:
        return None
    for k in range(1, 8):
        dd = (d - __import__("datetime").timedelta(days=k)).strftime("%Y-%m-%d")
        if dd in daily:
            return daily[dd]
    return SOL_MONTHLY_USD.get(day[:7])


# --------------------------------------------------------------------------- #
# 3-5. per-token enrichment
# --------------------------------------------------------------------------- #
def pumpfun_meta(pf: Http, mint: str) -> Optional[dict]:
    d = pf.get(f"{PF}/coins/{mint}", ok404=True)
    if not d or d.get("__404__"):
        return None
    keep = ("name", "symbol", "description", "created_timestamp",
            "king_of_the_hill_timestamp", "complete", "raydium_pool",
            "pump_swap_pool", "twitter", "telegram", "website", "reply_count",
            "creator", "usd_market_cap", "market_cap", "last_trade_timestamp",
            "total_supply", "is_currently_live", "nsfw", "show_name",
            "image_uri", "metadata_uri")
    return {k: d.get(k) for k in keep if k in d}


def dexscreener_pairs(ds: Http, mint: str) -> dict:
    pairs = ds.get(DS_PAIRS.format(mint=mint)) or []
    if not isinstance(pairs, list):
        pairs = []
    pairs = [p for p in pairs if isinstance(p, dict)]
    with_created = sorted([p for p in pairs if p.get("pairCreatedAt")],
                          key=lambda p: p["pairCreatedAt"])
    first = with_created[0] if with_created else (pairs[0] if pairs else {})
    liq = max((float((p.get("liquidity") or {}).get("usd") or 0.0) for p in pairs),
              default=0.0)
    socials = []
    websites = []
    for p in pairs:
        info = p.get("info") or {}
        for s_ in info.get("socials") or []:
            t = s_.get("type") or s_.get("platform")
            if t and t not in socials:
                socials.append(t)
        for w in info.get("websites") or []:
            u = w.get("url") if isinstance(w, dict) else w
            if u and u not in websites:
                websites.append(u)
    return {"n_pairs": len(pairs),
            "first_pair_created": first.get("pairCreatedAt"),
            "first_pair_dex": first.get("dexId"),
            "first_pair_address": first.get("pairAddress"),
            "dexes": sorted({p.get("dexId") for p in pairs if p.get("dexId")}),
            "liquidity_usd_max": liq,
            "fdv_ds": max((float(p.get("fdv") or 0) for p in pairs), default=0.0),
            "socials_now": socials, "websites_now": websites,
            "boosts": max((int((p.get("boosts") or {}).get("active") or 0)
                           for p in pairs), default=0)}


def candles_12h(sw: Http, mint: str, created_ms: Optional[float]) -> List[list]:
    params = {"interval": "12h", "limit": 1000}
    if created_ms:
        params["createdTs"] = int(created_ms)
    d = sw.get(PF_SWAP.format(mint=mint), params=params)
    if not isinstance(d, list):
        return []
    out = []
    for c in d:
        try:
            out.append([int(c["timestamp"]), float(c["open"]), float(c["high"]),
                        float(c["low"]), float(c["close"]), float(c.get("volume") or 0)])
        except (KeyError, TypeError, ValueError):
            continue
    out.sort(key=lambda x: x[0])
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", default="winners_raw.json")
    ap.add_argument("--universe", default="winners_universe.json")
    ap.add_argument("--candles", default="winners_candles_12h.jsonl")
    ap.add_argument("--max-tokens", type=int, default=0)
    ap.add_argument("--refresh-universe", action="store_true")
    ap.add_argument("--era-start", default=ERA_START,
                    help="keep coins with ATH date >= this (default 2025-01-01)")
    ap.add_argument("--min-est-ath-mcap", type=float, default=3_000_000.0,
                    help="enrich every coin above this estimated ATH mcap")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--control-sample", type=int, default=500,
                    help="random sample of smaller coins enriched as controls")
    ns = ap.parse_args(argv)

    cg = Http(spacing=2.6)       # key-less CoinGecko ~ 20-30/min
    pf = Http(spacing=0.35)
    ds = Http(spacing=0.25)
    sw = Http(spacing=0.4)

    upath, opath, cpath = Path(ns.universe), Path(ns.out), Path(ns.candles)
    if upath.exists() and not ns.refresh_universe:
        universe = json.loads(upath.read_text(encoding="utf-8"))
        print(f"[i] universe loaded: {len(universe)} coins")
    else:
        print("[i] building universe from CoinGecko ...")
        universe = build_universe(cg, upath)

    raw: Dict[str, dict] = (json.loads(opath.read_text(encoding="utf-8"))
                            if opath.exists() else {})
    done_candles = set()
    if cpath.exists():
        for line in cpath.read_text(encoding="utf-8").splitlines():
            try:
                done_candles.add(json.loads(line)["mint"])
            except (ValueError, KeyError):
                continue

    print("[i] SOL/USD daily (365 d) ...")
    sol_daily = sol_prices(cg)
    print(f"    {len(sol_daily)} days")

    import random
    todo = [c for c in universe.values()
            if c.get("mint") and (c.get("ath_date") or "") >= ns.era_start
            and c["mint"] not in raw]

    # Robust ATH-mcap estimate: current circulating mcap scaled by ATH/price
    # (immune to junk total_supply values); fall back to ath x supply.
    def _ath_mcap(c):
        mc, px, ath = float(c.get("market_cap") or 0), float(c.get("current_price") or 0), float(c.get("ath") or 0)
        if mc > 0 and px > 0 and ath > 0:
            return mc * ath / px
        sup = c.get("total_supply") or c.get("max_supply") or c.get("circulating_supply") or 0
        return ath * float(sup or 0)
    for c in todo:
        c["est_ath_mcap"] = _ath_mcap(c)
    # every plausible winner (>= $500k est. ATH mcap) + a random control sample
    big = [c for c in todo if c["est_ath_mcap"] >= ns.min_est_ath_mcap]
    small = [c for c in todo if c["est_ath_mcap"] < ns.min_est_ath_mcap]
    random.Random(42).shuffle(small)
    todo = sorted(big, key=lambda c: -c["est_ath_mcap"]) + small[: ns.control_sample]
    print(f"[i] enriching {len(big)} plausible winners (est. ATH mcap >= "
          f"${ns.min_est_ath_mcap:,.0f}) + {min(len(small), ns.control_sample)} sampled controls")
    print(f"[i] {len(todo)} tokens to enrich (ATH >= {ns.era_start}, not yet done)")
    if ns.max_tokens:
        todo = todo[: ns.max_tokens]

    t0 = time.time()
    write_lock = threading.Lock()

    def enrich(c: dict) -> dict:
        mint = c["mint"]
        rec = dict(c)
        rec["pumpfun"] = pumpfun_meta(pf, mint)
        rec["dexscreener"] = dexscreener_pairs(ds, mint)
        created_ms = (rec["pumpfun"] or {}).get("created_timestamp") \
            or rec["dexscreener"].get("first_pair_created")
        rec["created_ms"] = created_ms
        rec["created_day"] = iso_day(created_ms)
        ath_day = (c.get("ath_date") or "")[:10]
        rec["sol_usd_ath"] = sol_usd_on(ath_day, sol_daily)
        rec["sol_usd_created"] = sol_usd_on(rec["created_day"], sol_daily)
        if rec["pumpfun"] is not None and mint not in done_candles:
            cds = candles_12h(sw, mint, created_ms)
            with write_lock:
                with cpath.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps({"mint": mint, "candles": cds}) + "\n")
                done_candles.add(mint)
            rec["n_candles_12h"] = len(cds)
        return rec

    # tokens run concurrently; each SOURCE is still paced by its own lock
    with ThreadPoolExecutor(max_workers=ns.workers) as ex:
        futs = {ex.submit(enrich, c): c for c in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            c = futs[fut]
            try:
                rec = fut.result()
            except Exception as exc:          # never lose the run to one token
                print(f"  [!] {c.get('symbol')}: {type(exc).__name__}: {exc}", flush=True)
                continue
            with write_lock:
                raw[rec["mint"]] = rec
                if i % 25 == 0 or i == len(todo):
                    opath.write_text(json.dumps(raw), encoding="utf-8")
                    el = time.time() - t0
                    print(f"  [{i}/{len(todo)}] {str(c.get('symbol')).encode('ascii','replace').decode():<10} "
                          f"pump={'y' if rec['pumpfun'] else 'n'} "
                          f"pairs={rec['dexscreener']['n_pairs']:<3} "
                          f"created={rec['created_day']}  ({el / 60:.1f} min, "
                          f"http fails {cg.n_fail + pf.n_fail + ds.n_fail + sw.n_fail})",
                          flush=True)
    opath.write_text(json.dumps(raw), encoding="utf-8")
    print(f"[ok] {len(raw)} tokens in {opath}; candles in {cpath}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
