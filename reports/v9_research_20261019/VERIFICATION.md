# v9 build — independent verification report

> **Public-repository note.** This report was written while the paper-trading engine was still
> part of the project; references to engine files, run directories and documents
> (`run_paper_segment_v9.ps1`, `docs/V9_GRADUATION_SEGMENT.md`, `tmp/`, `strategy_runs/`) are
> historical — those files are not included in this research-only edition. The research numbers
> and findings below are unchanged.

**Verifier:** v9-verifier (independent of the builder; every claim below was re-derived, not copied)
**Date:** 2026-10-19 (UTC 04:45–05:15) · repo `<repo>` · HEAD `de18ed3`
**Scope:** the v9 build per `tmp/v9_team/SPEC.md` (§3 engine, §4 launcher, §5 acceptance, §7 pilot, §8 write scope) + `task-4`.
**Verdict: READY WITH CAVEATS** (see §13). The full v9 segment may be started with the command in §14. All caveats are about measurement conditions / pre-existing test debt, not about v9 correctness or v8 safety.

**Hard invariants held throughout:** v8 PID 24828 (+9712) was never stopped, restarted, or written to; its dashboard stayed HTTP 200; its `run_policy.json`, launcher and run directory were not modified; the only real-feed run was the one allowed ~9-minute pilot, on its own run dir/DB/port (`tmp/v9_smoke_20261019`, `tmp/v9_smoke.sqlite3`, `:8791`).

---

## 1. Method and commands

Everything was re-run from the repo root with `.\.venv\Scripts\python.exe -X utf8 -B`:

| # | check | command | result |
|---|---|---|---|
| 1 | diff review | `git status` / `git diff` + full read of all changed files & new files | no correctness/regression bug found (§3) |
| 2 | new tests | `python -m unittest discover -s tests -p "test_v9_graduation_entry.py"` and `…test_run_policy_compat.py` | 53 + 12 = **65 OK** (§4) |
| 3 | full suite | `python run_tests.py` (log `tmp/v9_verify/full_suite.log`) | `Ran 1673 … FAILED (failures=3, skipped=7)` — same 3 live-DB failures as the builder, **independently proven pre-existing** (§4) |
| 4 | policy compat (critical) | `python tmp\v9_verify\verify_policy_compat.py` | **31/31 PASS** (§5) |
| 5 | cross-build hash | `python tmp\v9_verify\verify_default_hash.py` | **8/8 PASS** (§6) |
| 6 | launcher ↔ argparse | `python tmp\v9_verify\verify_launcher_flags.py` | **29/29 PASS** (§7) |
| 7 | CSV header migration | `python tmp\v9_verify\verify_csv_migration.py` | **10/10 PASS** on a byte-copy of v8's live log (§8) |
| 8 | offline smokes | `live_paper_trader.py --simulate …` default vs v9 flags | both exit 0; default = v8 behaviour, v9 flags drop launch venues (§9) |
| 9 | v8 health before/after | `python tmp\v9_verify\v8_health.py …` (JSON snapshots) | before 04:54:07Z, after 05:03:58Z, after2 05:07:27Z; v8 advanced throughout (§11) |
| 10 | ONE live pilot (SPEC §7) | `powershell -NoProfile -ExecutionPolicy Bypass -File .\run_paper_segment_v9.ps1 -RunDirectory tmp\v9_smoke_20261019 -SqlDb tmp\v9_smoke.sqlite3 -HttpPort 8791 -PilotSeconds 540` | **clean: exit 0, up 00:09:00, 5 pumpswap adoptions, 2 decisions, dashboard 200 then closed** (§10) |
| 11 | post-pilot evidence | `python tmp\v9_verify\analyze_pilot.py` | pin reproduced from launcher flags; decisions/SQL/safety evidence collected (§10, §12) |

Independent artifacts are all under `tmp/v9_verify/` (scripts + logs + JSON snapshots); the builder's `tmp/v9_build/` was read only. The builder's UTF‑16 diff exports were re-generated as UTF‑8 diffs in `tmp/v9_verify/diff_*.txt` and reviewed against the real files.

---

## 2. Change inventory (what was reviewed)

`git status` on the build (v8's own append-only logs excluded — those are the running process writing):

| file | line delta | disposition |
|---|---|---|
| `entry_validation.py` | +144 | new pure predicates: `parse_venue_list`, `graduation_error`, `market_cap_error`, `GRADUATED_CURVE_STATUS`, `MIN_MARKET_CAP_USD` |
| `live_paper_trader.py` | +498/−33 | policy-guard compat, 3 `PaperConfig` fields + CLI, `PoolQuote` cap parse, discovery venue filter, 2 admission gates, 3 decision columns, 4 shadow labels, banner/dashboard/summary counters |
| `run_paper_segment_v9.ps1` | new (244 lines) | v9 launcher: own run dir / SQL / port 8790 / `-PilotSeconds`, SPEC §4 pinned flags |
| `docs/V9_GRADUATION_SEGMENT.md` | new (326 lines) | design + 69k caveat + limitations + runbook + acceptance/kill + falsification |
| `tests/test_v9_graduation_entry.py` | new (688 lines) | 53 tests: predicates, config, discovery filter, both gates on the real `_decide_watcher`, quote parse, schema, policy hash |
| `tests/test_run_policy_compat.py` | new (313 lines) | 12 tests: every compat branch + the real v8 pin (read-only) |
| `tests/test_decision_measurement.py` | +10/−1 | **scope-extension (see §13.1)**: adds the 4 new default-off refusal reasons to the *completeness* expected-set; no assertion weakened |

`run_paper_segment_v8.ps1`, `strategy_runs/paper_segment_v8_20261017/run_policy.json`, the model artifacts and every existing report are **byte-identical/untouched** (`git diff HEAD -- run_paper_segment_v8.ps1` empty; v8 pin sha256 unchanged).

---

## 3. Diff review — findings

Verified against SPEC §3 by reading the actual code (not the builder's claims):

**Policy-hash compatibility (§3.1) — correct.**
- `_run_policy(fields=None)` hashes an explicit field sequence; default still `RUN_POLICY_FIELDS` (51). Values are normalised to declared types before hashing; `dm.fingerprint` is `json.dumps(sort_keys=True)`, so a *rebuild over pinned names in JSON order* is order-insensitive.
- `_policy_field_types()` now resolves types for **every** `PaperConfig` field (70), so an old pinned field set still normalises.
- `_guard_run_policy()`: pinned key set == current → old behaviour exactly (full digest, moved fields named). Else: refuse a pinned name missing from `PaperConfig` (rename/removal must not silently drop out of the hash); refuse if any field added since the pin is non-default (naming the field, stating the pin predates it, telling the operator to start a new run dir / restore the default); else rebuild the digest over the pinned names and compare with the pinned `policy_sha256`. On success it logs one line naming the held-at-default fields and **keeps the book's own pinned policy body and digest** (the sizing block refresh preserves them — verified in practice, §5). A new book still pins all 51 fields + full digest.

**Default-off semantics (§3.2) — inert by default, and the pre-v9 hash is unchanged.**
- `entry_venue_allow=""`, `graduated_venues=""`, `min_market_cap_usd=0.0`; `__post_init__` canonicalises the two venue strings (trim/lower/sort/dedupe) and rejects a separator-only list (`","` must not silently disable a gate) and a negative/non-finite floor.
- Cross-build proof (§6): a default config's 48-field digest under this build equals git-HEAD's digest, and the only raw default differences are the two module-relative model-path strings (snapshot location, not a rule change).
- `_venue_admitted()` returns True for an empty allowlist; for a non-empty one, an unnamed venue is **not** admitted (unknown ≠ pass).

**Gate order (§3.4) — as specified.**
- Graduation gate runs immediately after the curve-state read and **before** `progress_error`; v9 pins `--min-curve-progress 0` so the v8 floor is off. `migrated` curve **or** entry venue in `graduated_venues` passes; `curve_status=="ok"` refuses `entry_not_graduated`; any unreadable/absent/disabled/error curve on a non-graduated venue refuses `entry_graduation_unknown`. Admission basis recorded (`migrated`|`venue`).
- Market-cap gate runs **after `_capture_entry_quote()` returns True and before Gate 1**, so a cap-refused ticket is never logged as a model rejection. Known cap below floor → `entry_market_cap_low`; missing/0/non-finite cap → `entry_market_cap_unknown` (unknown is never a pass). Refusals are priced off the tape (`entry_mark` cleared, `counterfactual_mark` set) and shadow-registered under `skip_graduation`/`skip_market_cap`.
- Model gates 0.60/0.40, exits, friction, sizing and shadow contract are untouched by the diff (no hunks in those code paths; launcher token diff confirms identical flags, §7).

**Discovery filter placement — correct.** The venue allowlist is applied to the discovered list **before** `_adopt_pool`, so a launch pool never enters `_seen_tokens` and never consumes a watch slot/tape call; `n_skipped_venue` counts the drops and `_log_scan_status` names the allowlist plus the venues the feed actually offered (with a distinct "policy working, not a quiet market" message). Verified live in the pilot (§10) and offline (§9).

**Counters/schema — correct.** `n_skipped_venue`, `n_rejects_not_graduated`, `n_rejects_market_cap` are initialised in `__init__`, exposed in the dashboard `counts` (`venue_skipped`, `rej_not_graduated`, `rej_market_cap`), the rich-terminal "Rejected" row, and the end-of-session summary. The three decision columns are appended to `DECISION_COLS` (`entry_market_cap_usd` `%.2f`-or-empty, `entry_market_cap_basis`, `entry_graduation`), are unique, and are written on every row. `SHADOW_SKIP_LABELS` gained the 4 reasons; the map-completeness test was updated accordingly. The live run's CSV proved the schema (83 columns) and the migration is loss-free (§8).

**Non-issues / observations** (recorded, not defects):
- In `--observe-only` mode the market-cap gate is not reached (the `research_only` branch returns before it); v9 does not use that mode, and capturing the gate verdict is arguably right for an observation run.
- The market-cap columns are empty on tickets refused *before* the admission gates by the quote-stage checks (depth/dev-dump/participation) because the cap is recorded on `_capture_entry_quote` success — exactly SPEC §3.4's contract.
- `graduation_error` recomputes `parse_venue_list` per call (trivial CPU; no correctness impact).
- Theoretical: if a feed ever supplied a NaN cap, `market_cap_error` refuses it as unknown but the CSV formatter would write `nan` rather than empty. Cannot arise from the actual `LiveSource` path (`fdv_usd`/`market_cap_usd` are only accepted when >0); noted for completeness only.

---

## 4. Test results

**New tests (this build):**
```
tests/test_v9_graduation_entry.py   Ran 53 tests in 0.709s   OK
tests/test_run_policy_compat.py     Ran 12 tests in 0.065s   OK
```
**Full suite (my own run, final files, v8 still running):**
```
Ran 1673 tests in 238.842s
FAILED (failures=3, skipped=7)
```
- 1673 = 1608 pre-existing + 65 new (matches the builder's count and the HEAD-baseline arithmetic).
- The 3 failures are **only** `test_return_denominator.TheDenominatorInconsistencyTests`: `test_the_denominator_is_uniform`, `test_the_cost_column_is_NOT_uniform`, `test_the_cost_column_disagrees_with_the_denominator_on_some_rows`.
- The 7 skips are optional-research artifacts absent on this machine (`pinned training artifacts not present` ×4, `feature frame or raw melt corpus` / `corpus tapes not present` in `test_research_hand_reconciliation`) — same class as the HEAD baseline's skips; none is v9-related.

**Pre-existing proof (confirming, not trusting, the builder).** These tests grade the **live** `coin_database.sqlite3`, which is written by the running v8 process and is not versioned. I extracted `git archive HEAD` into `tmp/v9_verify/head_snapshot` (48 policy fields, no v9 fields — confirmed by introspection), took a consistent read-only snapshot of the live DB via the SQLite backup API, and ran only that test module against HEAD code:
```
Ran 14 tests in 0.742s
FAILED (failures=3)      # the same three test ids
```
The current live book state explains it without any code change: 289 graded positions, `realized_pnl_pct` denominators `{0.0101, 0.011}` (the tests expect the single older denominator `0.011`), stored costs `{0.01, 0.0101, 0.011}` (the new `0.0101` rows come from alloc 0.010 + the 0.0001 priority fee in later runs), disagreeing fraction 0.1626 (the test's live-drift band is 0.30–0.70; its own docstring says the fraction drifts with the live book). The v9 diff does not touch position/trade cost accounting, and the DB rows were written by the v8 process running HEAD code. **Confirmed: pre-existing data-drift failures, not a v9 regression.** (They will keep failing until the live book is rebuilt / the fixtures updated — tracked in §13.)

Targeted `tests.test_decision_measurement` also passed (100 tests OK) — the scope-extension change is sound.

---

## 5. v8 resume compatibility (the critical proof) — 31/31 PASS

Script: `tmp/v9_verify/verify_policy_compat.py` (my own; it does **not** reuse the builder's script). It byte-copies the **real** `strategy_runs/paper_segment_v8_20261017/run_policy.json` into `tmp/v9_verify/`, reconstructs the v8/v9 configs from **the launchers' own flag text** via `lp._parse_args` + `lp.main`'s real arg→config mapping (trader class stubbed only to capture the config), and drives the real `_guard_run_policy()`.

```
[PASS] v8 pin copy is byte-identical to the live pin  (7f534aea0fcf456e..)
[PASS] v8 pin has the pre-v9 48 policy fields  (pinned=48 current=51)
[PASS] the only fields added since the pin are the three v9 admissions
[PASS] v8 launcher flags parse and build a PaperConfig under this build
[PASS] the new v9 fields are at their defaults in the v8 launcher config  ('', '', 0.0)
[PASS] rebuilt 48-field digest reproduces the pinned policy_sha256  (1b0159fbb61f..4afd6009)
[PASS] every pinned field value reproduces exactly (type-normalised)  (mismatches=[])
[PASS] the REAL v8 pin RESUMES under this build (guard does not raise)  (None)
[PASS] resume logs the new fields it is holding at their defaults
[PASS] resume does NOT rewrite the pinned policy body  (fields=48)
[PASS] resume does NOT change the pinned policy_sha256  (1b0159fbb61f..4afd6009)
[PASS] a second resume over the old pin still resumes (it re-logs the held-defaults line …)
[PASS] changed OLD field (rug_gate_p 0.60->0.61) is REFUSED   -> names rug_gate_p + --run-directory
[PASS] changed OLD exit rule (tp_mult 4.0->3.0) is REFUSED    -> names tp_mult
[PASS] non-default NEW field min_market_cap_usd=69000.0 REFUSED against the old pin
[PASS] non-default NEW field entry_venue_allow='pumpswap' REFUSED
[PASS] non-default NEW field graduated_venues='pumpswap' REFUSED
[PASS] pin naming an unknown/removed field is REFUSED (captured verbatim)
[PASS] v9 launcher flags parse and build a PaperConfig
[PASS] v9 config carries the pinned admission policy  ('pumpswap','pumpswap',69000.0,0.0)
[PASS] v9 moves exactly the intended old-field values (min_curve_progress, sql_db_path)
[PASS] first start pins ALL current policy fields (51)
[PASS] the fresh pin records the v9 admission values
[PASS] the fresh pin's digest matches its own policy body
[PASS] a second start over the fresh v9 pin is silent (resumes normally)
[PASS] a NEW v9 book refuses a changed admission field   -> names min_market_cap_usd
[PASS] v9 admission flags leave the 48-field (v8) policy digest unchanged
[PASS] policy types resolve for EVERY config field (70 fields)
[PASS] the three new fields resolve to str/str/float
...
31/31 checks PASSED
```
Key outcome: **the running v8's pinned policy re-hashes to exactly `1b0159fbb61fc5c9a935d405effee1cd3990d5fae6aa86500ea136da4afd6009` under this build and resumes; the v9 admission flags are refused against that pin.** The failed-shape check (unknown field, changed old field, non-default new field) all refuse with `ExecutionStateError`.

The digest reproduction was also shown independently from two directions in `tmp/v9_build/replay_v8_pin.py` (builder) and in my §6 cross-build check; and `tests/test_run_policy_compat.py` re-runs against the real pin read-only.

---

## 6. Cross-build default-hash check — 8/8 PASS

Script: `tmp/v9_verify/verify_default_hash.py`; HEAD snapshot in `tmp/v9_verify/head_snapshot` (`git archive HEAD`), driven in a separate interpreter.
```
[PASS] HEAD snapshot really is the pre-v9 build (48 fields, no v9 fields)
[PASS] current build hashes 51 fields (48 + the three v9 admissions)
[PASS] current OLD field set == HEAD's field set (nothing renamed/removed)
[PASS] the ONLY raw default-policy differences are the two module-relative model-path defaults
[PASS] DEFAULT-off config: current 48-field digest == HEAD's digest  (70aabd179e3bf80a..)
[PASS] DEFAULT-off config: EVERY old field value is identical to HEAD's
[PASS] v8 launcher config: HEAD code, current code and the pinned digest all agree (1b0159fb…)
8/8 checks PASSED
```
i.e. adding the three fields with their defaults is **hash-inert for a v8-shaped book**, and the v8 pin reproduces under HEAD, under the current build, and matches the file on disk.

---

## 7. Launcher ↔ argparse verification — 29/29 PASS

Script: `tmp/v9_verify/verify_launcher_flags.py` (parses both `.ps1` files' engine invocation, no hand-copied list).
- Defaults: run dir `strategy_runs/paper_segment_v9_20261019`, SQL `coin_database_v9.sqlite3` (separate file), port **8790** (:8791 reserved for the pilot), `-PilotSeconds` wired to `--seconds` exactly like v8, `$PSScriptRoot` + venv resolution + fatal check + `exit $LASTEXITCODE`; header documents PAPER ONLY, the 69k/‑$43k SOL caveat (+60 % momentum filter), the weak-venue-probability limitation, the BOOST confounder, the concurrent-v8 quota caveat, acceptance/kill criteria, and the frozen-policy rule.
- Token diff v8 → v9: the only added flags are `--entry-venue-allow pumpswap`, `--graduated-venues pumpswap`, `--min-market-cap-usd 69000`; the only pinned value changed is `--min-curve-progress 0.03 → 0`.
- argparse accepts **every** v9 launcher flag (81 tokens); mapping verified: allowlists parse to `pumpswap`, cap to `69000.0` float, progress floor `0.0`, `--trailing-stop off → None`, and model gates/exits/friction/sizing flags equal v8's (0.60/0.40; TP 4.0x/100 %, hold 5400 s, idle 600 s, 2 × 0.0001/0.010 = 2.0 %, 1.0 SOL balance, 0.010 alloc, 10 positions).
- `python live_paper_trader.py --help` independently shows the three new flags registered.

---

## 8. CSV header migration — 10/10 PASS

Script: `tmp/v9_verify/verify_csv_migration.py`, on a **copy** of v8's live `decisions_log.csv` (1,769 data rows, old 80-column header; v8's file untouched — `_migrate_csv_header` is the machinery a later v8 restart will trigger):
```
[PASS] v8 live decisions log has the PRE-v9 header (no v9 columns)  (1769 rows, 80 cols)
[PASS] migration produced exactly DECISION_COLS as the header  (83 cols)
[PASS] header columns are unique
[PASS] the three v9 columns are present
[PASS] no row was lost or added by the migration
[PASS] the migration logged which file it upgraded
[PASS] EVERY old row keeps every old column value (name-mapped)  ([])
[PASS] old rows get EMPTY (unknown) values in the three new columns
[PASS] a post-migration append aligns (cap column = 69000.00)
[PASS] the file keeps its row count + 1 and no other row changed
10/10 checks PASSED
```
No misalignment hazard: name-mapped rebuild, old values preserved, new columns empty on old rows, new-format appends align.

---

## 9. Offline simulate smokes (no network)

`--simulate --speed 60 --seconds 20 --no-dashboard` in `tmp/v9_verify/sim_default` and `tmp/v9_verify/sim_v9`; both **exit 0**.

* **Default config → v8 behaviour:** banner `venue allowlist: all venues (v8 behaviour)`, `graduation gate: off (v8 behaviour)`, `market-cap admission: off (v8 behaviour)`; 14 decision rows with the 3 new columns present but **all empty** (0 rows carry a value); `run_policy.json` pins 51 fields with the three defaults; `buys: 4`.
* **v9 flags:** banner `venue allowlist: pumpswap`, `graduation gate: migrated curve OR entry venue in pumpswap`, `market-cap admission: entry quote cap >= $69,000, unknown refused`; every emulated pool dropped before adoption and the diagnostic names the reason: `VENUE ALLOWLIST: dropped all 1 offered pool(s); nothing matched 'pumpswap'. Feed venues: pumpfun x1 - 0 adopted. This is the policy working, not a quiet market.`; summary: `venue allowlist: pumpswap (18 offered pool(s) dropped before adoption)`; run pin correctly records `entry_venue_allow=pumpswap`, `graduated_venues=pumpswap`, `min_market_cap_usd=69000.0`, `min_curve_progress=0.0`.

---

## 10. The ONE allowed live pilot (real GeckoTerminal feed)

Command (exactly SPEC §7, run once; stdout+stderr → `tmp/v9_verify/smoke.out.txt`):
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_paper_segment_v9.ps1 `
  -RunDirectory tmp\v9_smoke_20261019 -SqlDb tmp\v9_smoke.sqlite3 `
  -HttpPort 8791 -PilotSeconds 540
```
**Startup (all verified):** launcher banner (v9 population/admission/69k caveat/limitations/quota caveat); engine banner with the three v9 lines; `run policy pinned: 180e354bcf2c..`; `SQL mirror active -> tmp\v9_smoke.sqlite3`; `discovery ledger active`; dashboard `http://127.0.0.1:8791/` returned **HTTP 200** while running (and `/api/book` JSON served).
**Policy pin (independently reproduced):** `run_policy.json` has **51 fields**, sha256 `180e354bcf2cb1999b5456688efe48adc488e59e85bd2611fa89c666ab849b4e`, `entry_venue_allow=pumpswap`, `graduated_venues=pumpswap`, `min_market_cap_usd=69000.0`, `min_curve_progress=0.0`. `analyze_pilot.py` rebuilt the config from the launcher flags and recomputed the hash → **match, moved fields = []**.
**Venue allowlist, live:** 6 scans logged `VENUE ALLOWLIST: dropped all 6 offered pool(s); nothing matched 'pumpswap'. Feed venues: pump-fun x6` (and `pump-fun x5, meteora-damm-v2 x1`); final summary `venue allowlist: pumpswap (49 offered pool(s) dropped before adoption)`.
**Adoptions (5, all pumpswap — zero non-pumpswap):**
```
[04:55:16] NEW POOL: BTC … (pumpswap) age=74s
[04:59:20] NEW POOL: LIAMECHO … (pumpswap) age=95s
[04:59:20] NEW POOL: CLAW … (pumpswap) age=109s
[05:01:20] NEW POOL: Gemini … (pumpswap) age=158s
[05:02:20] NEW POOL: LEGITCOIN … (pumpswap) age=150s
```
**Decisions logged: 2 (both dex=pumpswap; new schema present; 83 columns).**
```
wall_time 04:59:07Z  BTC   pumpswap age=305  action=skip reason=tape_incomplete
                    entry_quote_status=not_requested  entry_graduation=''  cap=''
wall_time 05:02:59Z  CLAW  pumpswap age=317  action=skip reason=entry_dev_unknown
                    entry_quote_status=ok (geckoterminal)  entry_mark=0
                    entry_graduation='venue'   counterfactual_mark=3.127515667e-07
                    curve_status=unreadable
```
The CLAW row is live evidence of the v9 mechanics that *were* reachable in the window: the venue allowlist admitted a pumpswap pool, the **graduation gate passed via the venue proof and recorded `entry_graduation=venue`** (curve unreadable — the documented weak-venue case), an entry quote was obtained, and the refusal (dev-dump gate: `entry_dev_unknown`) was priced off the tape and shadow-registered (`skip_quote`, the pre-existing default label for that gate).
**Honest limitation:** no ticket reached the **market-cap gate** (both decisions were refused before/at the quote stage — one tape-saturated, one dev-dump), so the $69k admission and the model-gate routing were **not exercised live in this window**. They are proven offline by the 53 new tests on the real `_decide_watcher` (migrated pass, venue pass, live-curve refuse, unknown refuse, known-low cap refuse, unknown cap refuse, cap-before-model-gates, graduated+cap together). The pilot was quiet — 2 decisions in 540 s accepted 5 adopted pools; this is reported as a quiet window, not as a sample.
**SQL mirror:** `tmp/v9_smoke.sqlite3` created fresh — 18 tables; `runs=1`, `discoveries=5`, `coins=2`, `decisions=2`, `positions=0`, `trades=0`.
**Shutdown / errors:** `--seconds 540` produced a clean `===== SESSION END (… up 00:09:00) =====` with the v9 summary lines (`venue allowlist: pumpswap (49 dropped)`, `graduation rejects: 0`, `market-cap rejects: 0`, `discovered: 5`, `buys: 0`, tape attempts 6 / 0 failed / 100 % available); **no `Traceback`, no `DISCOVERY ERROR`, no 429 / rate-limit line**; exit code **0** (observed in the job output; `:8791` closed afterwards, run-dir mtimes froze at shutdown).
**Write discipline:** the pilot wrote only `tmp/v9_smoke_20261019/**` and `tmp/v9_smoke.sqlite3`; `strategy_runs/paper_segment_v9_20261019` and `coin_database_v9.sqlite3` do **not** exist; nothing under v8's run dir was written by the pilot.

---

## 11. v8 control-book health before / during / after the pilot

v8 PID 24828 + 9712 alive at every snapshot; dashboard `http://127.0.0.1:8789/` HTTP 200 and `/api/book` OK at every snapshot.

| snapshot (UTC) | PID alive | dashboard | `decisions_logged` | `decided` | `buys` | decisions CSV rows | last decision wall_time | SQL positions/trades |
|---|---|---|---|---|---|---|---|---|
| before 04:54:07 | 24828+9712 | 200 / OK | 1697 | 1140 | 57 | 1773 | 04:53:39 | 296 / 746 |
| during 04:56:37 | yes | 200 | 1698 | 1140 | 57 | — | — | — |
| during 04:59:03 | yes | 200 | 1701 | 1142 | 57 | — | — | — |
| after 05:03:58 | 24828+9712 | 200 / OK | 1705 | 1145 | 58 | 1781 | 05:03:13 | 297 / 747 |
| after2 05:07:27 | 24828+9712 | 200 / OK | 1710 | 1149 | 58 | 1786 | 05:07:07 | 297 / 747 |

**v8 was not starved or degraded by the pilot:** across the 9-minute pilot it logged **+8 decision rows, +5 model-scored decisions, +1 buy**, and its last decision timestamp advanced from 04:53:39 to 05:03:13 (and kept advancing to 05:07:07 after the pilot). `feed_fail` stayed 2, `gt_min_interval_s` stayed 13.0 s, `gt_penalised` stayed 1 (no new 429 penalty), `shadow_done` stayed 67, `api=OK`, state continued. The dashboard was never degraded (both books served 200 concurrently; the pilot used its own port 8791).
**Safety evidence:** v8 `run_policy.json` sha256 `7F534AEA…F189` and mtime 2026-10-17 18:10:58 unchanged; `git diff HEAD -- run_paper_segment_v8.ps1` empty; `git status` for the v8 pin clean; the only v8-dir diffs are its own append-only logs (the running process).

---

## 12. Safety / write-scope compliance

- Write scope respected: all my artifacts are under `tmp/v9_verify/**` plus this one report; I did not edit the engine, tests, launcher, docs, v8 files, or the other agents' research reports (`ONLINE_RESEARCH.md` untouched; `LOCAL_EVIDENCE.md` not present when this was written).
- No process/port/DB collision: pilot on `:8791` + `tmp\v9_smoke.sqlite3`; v8 stayed on `:8789` + `coin_database.sqlite3`; no listener on 8790 after verification; no `coin_database_v9.sqlite3`; no `strategy_runs/paper_segment_v9_20261019`.
- Only one real-feed run was made (the §7 pilot). Everything else was offline/tests/simulate.

---

## 13. Issues, caveats, residual risks

1. **Scope deviation (needs Lead acknowledgement, not a defect):** `tests/test_decision_measurement.py` is modified (+10/−1) although SPEC §8's engine-v9 list does not include it. The builder's report calls it a Lead-approved scope extension. The change only adds the 4 new default-off refusal reasons to the *completeness* expected-set — it is **required** because that test asserts `emitted == set(SHADOW_SKIP_LABELS)`, and it weakens nothing (both sides can still fail). I verified the file's actual diff; recommend the Lead confirm the approval is recorded.
2. **Full suite is not green — 3 pre-existing live-DB failures.** Independently proven to predate this build (§4): the same 3 tests fail under git-HEAD code against a snapshot of the live book, and they grade rows written by the running v8 process. Not a v9 regression and not a blocker, but "full suite green" cannot be quoted for this build until the live-book fixtures are reviewed (the tests' own docstring says the fraction is a live measurement).
3. **Pilot was quiet / admission gates not exercised live.** 2 decisions in 9 minutes, both refused before the gates (tape saturation; dev-dump unknown). Proof-of-life (launcher, pin, dashboard, venue allowlist, graduation-gate `venue` basis, quote, decision schema, SQL mirror, clean shutdown) is established; the $69k admission + model routing are proven offline only. Do not describe the pilot as a strategy sample.
4. **Concurrent-v8 GeckoTerminal quota (must be stated to the operator).** Key-less GT is one per-IP budget (~4–4.6 calls/min measured). v8 keeps running as the control book, so v9 will *split* that budget: expect displaced discovery/tape throughput and possible 429 cooldowns in **both** books. The pilot added a modest load and v8 did not degrade in 9 minutes, but a full v9 segment runs much longer. Never "fix" this by stopping v8; the launcher/docs already carry this caveat, and the segment's own infrastructure-kill criterion (quote coverage < 50 % for two consecutive days) exists precisely for it.
5. **Venue = pumpswap is weak proof of graduation** (~1 in 10 PumpSwap pools per the cited public data). The design records the basis (`migrated` vs `venue`) and relies on the $69k cap as the real discriminator; this is documented in the launcher, the doc and this report. The research report must state it too.
6. **69k ≠ migration.** At measured SOL ≈ $104–105 the curve graduates at ≈ $43k; `--min-market-cap-usd 69000` is a +~60 % post-migration momentum filter (≈657 SOL FDV). The research task must quantify both cohorts at the measured SOL price; the launcher/doc state this.
7. **Old-pin resume logs one line per start** ("new fields held at defaults") and refreshes only the non-hashed sizing evidence block; the pinned policy body/digest is preserved. That is the specified behaviour (SPEC §3.1) and was verified against the real pin, but it means a v8 restart after this change will emit that yellow log line — expected, not an error.
8. The full v9 segment will pin **two old fields to different values than v8's book** (`min_curve_progress` 0.03→0 and a separate `sql_db_path`); this is the intended policy-change family and forces a distinct hash/run dir (verified).
9. Theoretical NaN-cap formatting edge (§3) — no action needed for this build.

---

## 14. Verdict and the exact command to start the full v9 segment

**READY WITH CAVEATS.** No correctness, regression or v8-resume defect was found; the policy guard preserves the running v8; the launcher is correct against argparse and the SPEC; default-off behaviour is v8-identical (including the hash); the pilot proved the plumbing end-to-end on the real feed and v8 kept advancing. The caveats are: (i) the 3 full-suite failures are pre-existing live-DB drift (not green), (ii) the pilot never admitted a ticket so the $69k gate has offline proof only, and (iii) the shared GeckoTerminal quota with v8 is a real measurement risk for the long run.

**Start the segment** (from `<repo>`; defaults = `strategy_runs/paper_segment_v9_20261019`, `coin_database_v9.sqlite3`, dashboard `http://127.0.0.1:8790/`):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_paper_segment_v9.ps1
```

Operational notes:
- **PAPER ONLY.** v8 keeps running; do not stop it — it is the control book and the quota is shared (expect displacement/429s in both logs; that is the documented caveat, not a v9 defect).
- The policy is frozen by hash: changing any pinned flag requires a **new** `--run-directory`; do not delete `run_policy.json` to get past a refusal. A restart with the same flags resumes the same book.
- Acceptance/kill criteria (pre-registered in the launcher and `docs/V9_GRADUATION_SEGMENT.md`): ≥100 pumpswap decisions/day; quote coverage ≥70 % (infra kill at <50 % two consecutive days); ≥5 buys/day admitted by the graduation+MC gates; edge pass at shadow peak p50 ≥1.05× and ≥20 % ≥1.5× within 1 h, net-of-fee bootstrap lower bound >0 on ≥60 closed tickets; kill after ~150 admitted tickets or 7 days if the cohort is flat/negative. Always compare with v8's concurrent launch book.
- If you want a *new* pilot later, use a fresh run directory/SQL/port; `tmp/v9_smoke_20261019` is now a completed pilot book.

---

## 15. Evidence index (`tmp/v9_verify/`)

| file | what |
|---|---|
| `verify_policy_compat.py` + `policy_compat_out.txt` | the 31/31 v8-resume/refusal rehearsal (drives the real pin) |
| `verify_default_hash.py` + `default_hash_out.txt` + `head_snapshot/` + `head_default_digest.json` | git-HEAD snapshot; cross-build default-hash proof (8/8) |
| `verify_launcher_flags.py` + `launcher_flags_out.txt` | launcher ↔ argparse/SPEC (29/29) |
| `verify_csv_migration.py` + `csv_migration_out.txt` | loss-free decisions-header migration on a copy of v8's live log (10/10) |
| `v8_health.py` + `v8_health_{before,after,after2}.json` | v8 control-book health snapshots |
| `smoke.out.txt` (pilot console, UTF‑16), `pilot_analysis.py/…json`, `analyze_pilot.py` + `pilot_analysis_out.txt`, `inspect_sql.py` | the live pilot's full evidence |
| `full_suite.log`, `new_v9_tests.log`, `new_compat_tests.log`, `test_decision_measurement.log` | my test runs |
| `head_return_denominator_verify.log` | HEAD-code rerun of the 3 live-DB failures (pre-existing proof) |
| `sim_default/`, `sim_v9/`, `*.log` | offline simulate smokes |
| `diff_*.txt`, `v8_policy_copy.json`, `v8_pin_fields.txt` | review inputs |
