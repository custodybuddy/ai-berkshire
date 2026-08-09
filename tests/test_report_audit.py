import contextlib
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path

from tools import report_audit

ROOT = Path(__file__).resolve().parents[1]


class ReportAuditTests(unittest.TestCase):
    def verdict(self, results):
        with contextlib.redirect_stdout(io.StringIO()):
            return report_audit.render_verdict(results)

    def test_single_mismatched_source_fails(self):
        outcome = self.verdict([
            {
                "id": 1,
                "label": "Revenue",
                "reported_value": 100,
                "fetched_value": 50,
                "fetched_source": "filing",
            }
        ])
        self.assertEqual(outcome["verdict"], "FAIL")
        self.assertEqual(outcome["fail_count"], 1)

    def test_empty_or_unverified_results_fail(self):
        self.assertEqual(self.verdict([])["verdict"], "FAIL")
        self.assertEqual(
            self.verdict([
                {"id": 1, "label": "Revenue", "reported_value": 100}
            ])["verdict"],
            "FAIL",
        )

    def test_disagreeing_sources_warn_without_false_failure(self):
        outcome = self.verdict([
            {
                "id": 1,
                "label": "Revenue",
                "reported_value": 100,
                "fetched_value": 100,
                "fetched_source": "filing",
                "fetched_value2": 80,
                "fetched_source2": "aggregator",
            }
        ])
        self.assertEqual(outcome["verdict"], "PASS")
        self.assertEqual(outcome["warn_count"], 1)

    def test_extracts_signed_and_zero_values(self):
        points = report_audit.extract_data_points(
            "净利润：-10亿元\n毛利率：-5%\n自由现金流：0亿元"
        )
        values = {point["label"]: point["reported_value"] for point in points}
        self.assertEqual(values["净利润"], -10)
        self.assertEqual(values["毛利率"], -5)
        self.assertEqual(values["自由现金流"], 0)

    def test_table_parser_preserves_internal_empty_cells(self):
        points = report_audit.extract_data_points(
            "| metric | 2024 | 2025 | 2026 |\n"
            "|---|---:|---:|---:|\n"
            "| Revenue | 100 | | 300 |"
        )
        labels = {point["label"] for point in points}
        self.assertIn("Revenue · 2024", labels)
        self.assertIn("Revenue · 2026", labels)
        self.assertNotIn("Revenue · 2025", labels)

    def test_ignores_tables_inside_code_fences(self):
        points = report_audit.extract_data_points(
            "```markdown\n| metric | 2025 |\n|---|---:|\n| Revenue | 100 |\n```"
        )
        self.assertEqual(points, [])

    def test_sampling_ratio_is_validated(self):
        with self.assertRaises(ValueError):
            report_audit.sample_points([], ratio=0)
        with self.assertRaises(ValueError):
            report_audit.sample_points([], ratio=1.1)

    def test_output_json_is_machine_readable(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools/report_audit.py"),
                "verdict",
                "--results",
                '[{"id":1,"label":"Revenue","reported_value":100,'
                '"fetched_value":100,"fetched_source":"filing"}]',
                "--output-json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["verdict"], "PASS")


if __name__ == "__main__":
    unittest.main()
