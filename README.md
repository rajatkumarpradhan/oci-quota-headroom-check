# oci-quota-headroom-check

**Category: custom portfolio tool.** This is NOT an out-of-the-box OCI service
wiring; it is a standalone Python CLI I wrote. Its problem: OCI service
limits fail workloads silently-ish - a scale-out, a new instance, a bigger
volume just errors at the worst time. Teams discover their quota headroom
only when a deployment breaks. This tool audits a service-limit usage export
and fails the pipeline when headroom gets thin.

## What it does

- Loads a synthetic Limits service usage export (`limits.json`).
- Computes utilization per limit and applies four rules:

| Rule | Severity | Fires when |
| --- | --- | --- |
| QHC001 | CRITICAL | usage is at or over 100% of the limit |
| QHC002 | HIGH | usage is 90-99% of the limit (request an increase now) |
| QHC003 | MEDIUM | usage is 80-89% (start the limit-increase paperwork) |
| QHC004 | LOW | usage exists against a limit of 0 (quota increase pending / mis-scoped usage) |

- Prints findings sorted CRITICAL first, then a RESULT line.
- Exit codes: `0` clean, `2` findings present, `3` usage/input error.

## What actually ran vs template-only

- Everything in `quota_check/` is custom Python (stdlib only, no OCI SDK
  calls) and ran locally and in GitHub Actions CI (see Actions tab).
- The `examples/` JSON files are SYNTHETIC exports in the shape of OCI
  Limits usage listings. No live OCI tenancy was queried; nothing here
  talks to OCI. A live version would pull from the Limits API per region.

## Run it

```
python -m quota_check run-all examples/limits_messy.json
# -> 4 findings (1 CRITICAL at cap, 1 HIGH at 92%, 1 MEDIUM at 80%, 1 LOW), exit 2

python -m quota_check run-all examples/limits_clean.json
# -> clean, exit 0
```

## Test it

```
python -m unittest discover -s tests -v
```

22 tests cover loading/validation, all four rules, the 80%/cap boundaries,
sort order, and CLI exit codes. CI runs the tests on Python 3.10/3.11/3.12
plus both demo commands (messy must exit 2, clean must exit 0).
