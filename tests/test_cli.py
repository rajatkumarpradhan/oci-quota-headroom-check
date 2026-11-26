import io
import os
import unittest

from quota_check import cli

EX = os.path.join(os.path.dirname(__file__), "..", "examples")


class TestCli(unittest.TestCase):
    def test_messy_exit_2(self):
        out = io.StringIO()
        code = cli.run_all(os.path.join(EX, "limits_messy.json"), out=out)
        self.assertEqual(code, 2)
        self.assertIn("check failed", out.getvalue())

    def test_clean_exit_0(self):
        out = io.StringIO()
        code = cli.run_all(os.path.join(EX, "limits_clean.json"), out=out)
        self.assertEqual(code, 0)
        self.assertIn("clean", out.getvalue())

    def test_error_exit_3(self):
        self.assertEqual(cli.main(["run-all", "/no/such.json"]), 3)

    def test_usage_exit_3(self):
        self.assertEqual(cli.main([]), 3)
        self.assertEqual(cli.main(["bogus"]), 3)


if __name__ == "__main__":
    unittest.main()
