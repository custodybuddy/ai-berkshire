#!/usr/bin/env bash
# 记录用户指令到日志文件
# 由 user_prompt_submit hook 调用，stdin 接收用户输入

set -euo pipefail

TOOLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${AI_BERKSHIRE_LOG_DIR:-$TOOLS_DIR/../logs}"

exec python3 "$TOOLS_DIR/log_command.py" --log-dir "$LOG_DIR"
