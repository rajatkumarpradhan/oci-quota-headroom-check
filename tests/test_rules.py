import os
import unittest

from quota_check import model, rules

EX = os.path.join(os.path.dirname(__file__), "..", "examples")


class TestMessy(unittest.TestCase):
    def setUp(self):
        limits = model.load(os.path.join(EX, "limits_messy.json"))
        self.findings = rules.run_all(limits)

    def test_at_cap_is_critical(self):
        f = [x for x in self.findings if x.rule == "QHC001"]
        self.assertEqual(len(f), 1)
        self.assertEqual(f[0].severity, "CRITICAL")
        self.assertIn("vm-standard-e5-core-count", f[0].message)

    def test_ninety_percent_is_high(self):
        f = [x for x in self.findings if x.rule == "QHC002"]
        self.assertEqual(len(f), 1)
        self.assertIn("total-storage-gb", f[0].message)

    def test_eighty_percent_is_medium(self):
        f = [x for x in self.findings if x.rule == "QHC003"]
        self.assertEqual(len(f), 1)
        self.assertIn("lb-count", f[0].message)

    def test_zero_limit_with_usage_is_low(self):
        f = [x for x in self.findings if x.rule == "QHC004"]
        self.assertEqual(len(f), 1)
        self.assertEqual(f[0].severity, "LOW")

    def test_quiet_limits_not_flagged(self):
        self.assertFalse(any("bucket-count" in f.message for f in self.findings))
        self.assertFalse(any("adb-ocpu-count" in f.message for f in self.findings))

    def test_sorted_critical_first(self):
        ranks = [rules.RANK[f.severity] for f in self.findings]
        self.assertEqual(ranks, sorted(ranks))

    def test_total_count(self):
        self.assertEqual(len(self.findings), 4)


class TestBoundaries(unittest.TestCase):
    def _check(self, limit, used):
        items = [{"service": "s", "name": "n", "scope": "region",
                  "limit": limit, "used": used}]
        return rules.run_all(items)

    def test_just_below_80_quiet(self):
        self.assertEqual(self._check(100, 79), [])

    def test_zero_limit_zero_used_quiet(self):
        self.assertEqual(self._check(0, 0), [])

    def test_over_cap_still_critical(self):
        f = self._check(8, 9)
        self.assertEqual(f[0].rule, "QHC001")


class TestClean(unittest.TestCase):
    def test_clean_export_has_no_findings(self):
        limits = model.load(os.path.join(EX, "limits_clean.json"))
        self.assertEqual(rules.run_all(limits), [])


if __name__ == "__main__":
    unittest.main()
