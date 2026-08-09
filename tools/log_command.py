#!/usr/bin/env python3
"""Safely append prompt-hook input to the local JSONL command log."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def record_prompt(prompt: str, log_dir: Path) -> int:
    """Record one prompt and return the new count, or zero for empty input."""
    if not prompt:
        return 0

    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "command-log.jsonl"
    counter_file = log_dir / ".counter"
    short_prompt = prompt[:200].replace("\r", " ").replace("\n", " ")

    # The counter lock serializes both files, keeping counts and entries aligned.
    with counter_file.open("a+", encoding="utf-8") as counter:
        os.chmod(counter_file, 0o600)
        fcntl.flock(counter.fileno(), fcntl.LOCK_EX)
        counter.seek(0)
        raw_count = counter.read().strip()
        try:
            count = int(raw_count) + 1
        except ValueError:
            count = 1

        flags = os.O_APPEND | os.O_CREAT | os.O_WRONLY
        fd = os.open(log_file, flags, 0o600)
        os.chmod(log_file, 0o600)
        try:
            with os.fdopen(fd, "a", encoding="utf-8") as handle:
                entry = {
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "prompt": short_prompt,
                }
                handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
        except Exception:
            # os.fdopen owns fd once constructed; only close a still-open raw fd.
            try:
                os.close(fd)
            except OSError:
                pass
            raise

        counter.seek(0)
        counter.truncate()
        counter.write(str(count))
        counter.flush()
        os.fsync(counter.fileno())
        return count


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default_dir = Path(__file__).resolve().parents[1] / "logs"
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=Path(os.environ.get("AI_BERKSHIRE_LOG_DIR", default_dir)),
    )
    args = parser.parse_args(argv)
    count = record_prompt(sys.stdin.read(), args.log_dir)
    if count and count % 10 == 0:
        print(
            f"[指令日志] 已累计记录 {count} 条指令。"
            "建议运行 /command-log 补充近期指令的背景摘要。"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
