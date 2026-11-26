import os
import tempfile
import unittest

from quota_check import model

EX = os.path.join(os.path.dirname(__file__), "..", "examples")


class TestLoad(unittest.TestCase):
    def _write(self, text):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as fh:
            fh.write(text)
        self.addCleanup(os.unlink, path)
        return path

    def test_load_ok(self):
        limits = model.load(os.path.join(EX, "limits_messy.json"))
        self.assertEqual(len(limits), 6)

    def test_rejects_bad_json(self):
        with self.assertRaises(model.LoadError):
            model.load(self._write("{nope"))

    def test_rejects_missing_file(self):
        with self.assertRaises(model.LoadError):
            model.load("/no/such/file.json")

    def test_rejects_missing_field(self):
        bad = self._write('{"limits": [{"service": "compute"}]}')
        with self.assertRaises(model.LoadError):
            model.load(bad)

    def test_rejects_unknown_scope(self):
        bad = self._write(
            '{"limits": [{"service": "s", "name": "n", "scope": "az",'
            ' "limit": 1, "used": 0}]}')
        with self.assertRaises(model.LoadError):
            model.load(bad)

    def test_rejects_negative_number(self):
        bad = self._write(
            '{"limits": [{"service": "s", "name": "n", "scope": "region",'
            ' "limit": -1, "used": 0}]}')
        with self.assertRaises(model.LoadError):
            model.load(bad)

    def test_utilization(self):
        self.assertEqual(model.utilization({"limit": 8, "used": 4}), 0.5)
        self.assertIsNone(model.utilization({"limit": 0, "used": 4}))


if __name__ == "__main__":
    unittest.main()
