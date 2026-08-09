import contextlib
import io
import subprocess
import sys
import unittest
from decimal import Decimal
from pathlib import Path

from tools import financial_rigor


ROOT = Path(__file__).resolve().parents[1]


class FinancialRigorTests(unittest.TestCase):
    def quiet_call(self, func, *args, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return func(*args, **kwargs)

    def test_exact_calc_keeps_decimal_precision(self):
        result = self.quiet_call(financial_rigor.exact_calc, "1 / 7")
        self.assertIsInstance(result, Decimal)
        self.assertEqual(result, Decimal("0.1428571428571428571428571429"))

    def test_exact_calc_rejects_non_arithmetic_ast(self):
        result = self.quiet_call(financial_rigor.exact_calc, "__import__('os')")
        self.assertIsNone(result)

    def test_exact_calc_handles_division_by_zero_without_traceback(self):
        result = self.quiet_call(financial_rigor.exact_calc, "1 / 0")
        self.assertIsNone(result)

    def test_cross_validate_negative_values_uses_absolute_denominator(self):
        result = self.quiet_call(
            financial_rigor.cross_validate,
            "loss",
            {"source-a": -100, "source-b": -200},
        )
        self.assertFalse(result["all_consistent"])
        self.assertEqual(result["consensus"], Decimal("-150"))

    def test_cross_validate_requires_two_sources(self):
        with self.assertRaises(ValueError):
            self.quiet_call(financial_rigor.cross_validate, "revenue", {"only": 1})

    def test_nonzero_market_cap_cannot_match_zero_reported_cap(self):
        result = self.quiet_call(financial_rigor.verify_market_cap, 10, 100, 0)
        self.assertFalse(result)

    def test_failed_market_cap_check_has_nonzero_cli_exit(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools/financial_rigor.py"),
                "verify-market-cap",
                "--price",
                "10",
                "--shares",
                "10",
                "--reported",
                "1",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
