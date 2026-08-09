import contextlib
import asyncio
import io
import json
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools import log_command
from tools import morningstar_fair_value
from tools import ashare_data
from tools import stock_screener
from tools import xueqiu_scraper

ROOT = Path(__file__).resolve().parents[1]


class SupportToolTests(unittest.TestCase):
    def test_command_log_is_valid_json_and_unicode_safe(self):
        with tempfile.TemporaryDirectory() as directory:
            prompt = '-n "quoted" \\ slash\n' + ('你' * 250)
            count = log_command.record_prompt(prompt, Path(directory))
            self.assertEqual(count, 1)
            line = (Path(directory) / "command-log.jsonl").read_text(
                encoding="utf-8"
            )
            entry = json.loads(line)
            self.assertEqual(len(entry["prompt"]), 200)
            self.assertTrue(entry["prompt"].startswith('-n "quoted" \\ slash '))
            mode = stat.S_IMODE((Path(directory) / "command-log.jsonl").stat().st_mode)
            self.assertEqual(mode, 0o600)

    def test_two_quarters_do_not_count_as_continuous_margin_improvement(self):
        fundamentals = {
            "TEST": {
                "quarters": {
                    "2025-01-01": {
                        "label": "Q1",
                        "rev_yoy": 0,
                        "gm": 46,
                        "eps_beat": 0,
                    },
                    "2025-04-01": {
                        "label": "Q2",
                        "rev_yoy": 0,
                        "gm": 47,
                        "eps_beat": 0,
                    },
                }
            }
        }
        with mock.patch.object(
            stock_screener, "load_fundamentals", return_value=fundamentals
        ):
            result = stock_screener.check_value("TEST")
        self.assertFalse(result["checks"]["毛利连续改善"])
        self.assertFalse(result["independent_pass"])

    def test_recent_breakout_always_uses_full_sixty_day_window(self):
        prices = [
            {"date": str(i), "close": 10, "high": 10, "volume": 100}
            for i in range(61)
        ]
        prices[-1]["close"] = 11
        prices[-1]["volume"] = 1000
        with contextlib.redirect_stdout(io.StringIO()):
            result = stock_screener.check_momentum(prices)
        self.assertTrue(result["is_60d_high"])

    def test_stock_screener_help_is_a_real_cli_option(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/stock_screener.py"), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout)

    def test_morningstar_empty_response_does_not_divide_by_zero(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
            morningstar_fair_value, "OUTPUT_DIR", directory
        ), mock.patch.object(
            morningstar_fair_value,
            "fetch_page",
            return_value={"total": 0, "rows": []},
        ), contextlib.redirect_stdout(io.StringIO()):
            morningstar_fair_value.main()

    def test_beijing_financials_use_beijing_market_code(self):
        filters = []

        def fake_json(url, params=None):
            filters.append(params["filter"])
            return {"result": {"data": []}}

        with mock.patch.object(ashare_data, "_curl", return_value=""), mock.patch.object(
            ashare_data, "_curl_json", side_effect=fake_json
        ), contextlib.redirect_stdout(io.StringIO()):
            ashare_data.cmd_financials("832000")
        self.assertTrue(filters)
        self.assertTrue(all("832000.BJ" in value for value in filters))


class ScraperTests(unittest.IsolatedAsyncioTestCase):
    async def test_timeline_retries_same_page_before_advancing(self):
        first_page = {
            "maxPage": 2,
            "total": 2,
            "statuses": [
                {"id": 1, "created_at": 0, "text": "keyword first"}
            ],
        }
        second_page = {
            "statuses": [
                {"id": 2, "created_at": 0, "text": "keyword second"}
            ]
        }
        responses = [first_page, None, second_page]
        calls = []

        async def fake_fetch(page, url, timeout_s=15):
            calls.append(url)
            return responses.pop(0)

        async def no_sleep(_):
            return None

        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
            xueqiu_scraper, "browser_fetch_json", side_effect=fake_fetch
        ), mock.patch.object(
            asyncio, "sleep", side_effect=no_sleep
        ), contextlib.redirect_stdout(io.StringIO()):
            collected = await xueqiu_scraper.fetch_all_timeline(
                object(),
                123,
                ["keyword"],
                str(Path(directory) / "progress.json"),
            )
        self.assertEqual(set(collected), {"1", "2"})
        page_two_calls = [url for url in calls if "page=2" in url]
        self.assertEqual(len(page_two_calls), 2)


if __name__ == "__main__":
    unittest.main()
