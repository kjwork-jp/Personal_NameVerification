# 88_large_data_performance_review_20260525.md

## Purpose

This document defines the repeatable large-data performance review plan for NameVerification.

It does not start UAT or release preparation. It only fixes the performance review scope, commands, and observation points.

## Scope

| Area | Target |
|---|---|
| Data generation | `scripts/generate_sample_data.py` bulk mode |
| Search | search result rendering and detail/related lookup behavior |
| Tables | large list rendering and selection behavior |
| Import/Export | CSV/JSON/SQL export time, import preview diagnostics, and import runtime |
| Packaging | portable layout smoke compatibility after large DB placement |

## Baseline commands

Small smoke dataset:

```powershell
python .\scripts\generate_sample_data.py --format sqlite --output tmp\sample_smoke.db --names 1000 --titles 1000 --subtitles-per-title 3 --links-per-name 2
```

Medium performance dataset:

```powershell
python .\scripts\generate_sample_data.py --format sqlite --output tmp\sample_medium.db --names 100000 --titles 10000 --subtitles-per-title 3 --links-per-name 2
```

Large performance dataset:

```powershell
python .\scripts\generate_sample_data.py --format sqlite --output tmp\sample_large.db --names 1000000 --titles 100000 --subtitles-per-title 3 --links-per-name 2
```

CSV large export/import source:

```powershell
python .\scripts\generate_sample_data.py --format csv --output tmp\sample_large_csv --names 1000000 --titles 100000 --subtitles-per-title 3 --links-per-name 2
```

## Review checklist

| Check | Expected observation |
|---|---|
| DB generation | Completes without committing generated DB to git |
| Search tab initial load | Does not freeze unacceptably on realistic dataset |
| Search query | Query latency is recorded with dataset size and query term |
| Detail lookup | Selecting a row updates related details predictably |
| Import preview | CSV/JSON preview reports counts without mutating target DB |
| Export | Full export and sanitized export behavior are distinguishable |
| SQL dump | Treated as protected full DB dump |
| Memory | Peak memory is recorded manually during large scenario |
| UI behavior | Tables remain usable or limitations are explicitly captured |

## Known risk

Current UI tables are direct `QTableWidget` renderers. Very large unbounded result sets may require future pagination, query limit controls, or model/view refactoring.

## Future implementation candidates

| ID | Candidate |
|---|---|
| V050-PERF-002 | Add explicit UI search result limit control |
| V050-PERF-003 | Add paging or model/view table rendering for large result sets |
| V050-PERF-004 | Add optional command-line performance benchmark script |
| V050-PERF-005 | Record performance results in a dedicated benchmark ledger |

## Non-goals

- Do not publish a release.
- Do not start formal UAT.
- Do not commit generated sample DB/CSV data.
- Do not change production data handling without separate implementation task.
