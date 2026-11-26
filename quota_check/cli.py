"""CLI: audit service-limit headroom. Exit 0 clean, 2 findings, 3 error."""
import sys

from . import model, rules

USAGE = "usage: python -m quota_check run-all LIMITS_JSON"


def run_all(path, out=None):
    out = out or sys.stdout
    limits = model.load(path)
    findings = rules.run_all(limits)
    print("Quota headroom check - %d service limit(s)" % len(limits), file=out)
    for finding in findings:
        print(finding.line(), file=out)
    bad = sum(1 for f in findings if f.severity in ("CRITICAL", "HIGH"))
    if findings:
        print("RESULT: check failed - %d CRITICAL/HIGH / %d total finding(s) "
              "(exit code 2)" % (bad, len(findings)), file=out)
        return 2
    print("RESULT: headroom check clean (exit code 0)", file=out)
    return 0


def main(argv):
    if len(argv) == 2 and argv[0] == "run-all":
        try:
            return run_all(argv[1])
        except model.LoadError as exc:
            print("error: %s" % exc, file=sys.stderr)
            return 3
    print(USAGE, file=sys.stderr)
    return 3
