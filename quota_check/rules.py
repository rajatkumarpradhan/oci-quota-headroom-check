"""Headroom rules over a synthetic OCI service-limit export."""

from .model import utilization

RANK = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}


class Finding:
    def __init__(self, rule, severity, message):
        self.rule = rule
        self.severity = severity
        self.message = message

    def line(self):
        return "[%-8s] %s %s" % (self.severity, self.rule, self.message)


def check(limits):
    findings = []
    for item in limits:
        label = "%s/%s (%s scope)" % (item["service"], item["name"], item["scope"])
        util = utilization(item)
        if util is None:
            if item["used"] > 0:
                findings.append(Finding("QHC004", "LOW",
                    "%s shows usage %g against a limit of 0; a quota increase "
                    "looks pending or the usage is mis-scoped" % (label, item["used"])))
            continue
        pct = util * 100
        if util >= 1.0:
            findings.append(Finding("QHC001", "CRITICAL",
                "%s is at %.0f%% of its limit (%g/%g); new resources will fail "
                "until a limit increase lands" % (label, pct, item["used"], item["limit"])))
        elif util >= 0.90:
            findings.append(Finding("QHC002", "HIGH",
                "%s is at %.0f%% of its limit (%g/%g); request a limit increase "
                "now" % (label, pct, item["used"], item["limit"])))
        elif util >= 0.80:
            findings.append(Finding("QHC003", "MEDIUM",
                "%s is at %.0f%% of its limit (%g/%g); start the limit-increase "
                "paperwork" % (label, pct, item["used"], item["limit"])))
    return findings


def sort_key(f):
    return (RANK[f.severity], f.rule, f.message)


def run_all(limits):
    findings = check(limits)
    findings.sort(key=sort_key)
    return findings
