#!/usr/bin/env python3
"""Financial Rigor Toolkit for AI Berkshire.

Command-line tool for verifying financial data accuracy during investment research.
Automatically called by Claude Code Skills at critical validation checkpoints.

Zero external dependencies — uses only Python stdlib (decimal, json, math, argparse).
Requires Python >= 3.7.

Usage (called automatically by Skills, no manual execution needed):
    python3 tools/financial_rigor.py verify-market-cap --price 510 --shares 9.11e9 --reported 4.65e12 --currency HKD
    python3 tools/financial_rigor.py verify-valuation --price 510 --eps 23.5 --bvps 120 --fcf-per-share 18 --dividend 2.4
    python3 tools/financial_rigor.py cross-validate --field revenue --values '{"年报": 7518, "Yahoo": 7500, "StockAnalysis": 7520}' --unit 亿
    python3 tools/financial_rigor.py benford --values '[1234, 2345, 3456, ...]'
    python3 tools/financial_rigor.py calc --expr '510 * 9.11e9'
"""

import argparse
import ast
import json
import math
import operator
import sys
from decimal import Decimal, Context, ROUND_HALF_EVEN, DecimalException

# ---------------------------------------------------------------------------
# Exact Decimal Engine (no floating-point drift)
# ---------------------------------------------------------------------------

_CTX = Context(prec=28, rounding=ROUND_HALF_EVEN)


def exact(value) -> Decimal:
    """Convert any numeric to exact Decimal, avoiding float traps."""
    if isinstance(value, Decimal):
        return value
    if isinstance(value, float):
        return Decimal(str(value))
    return Decimal(str(value))


def decimal_arg(value: str) -> Decimal:
    """Argparse adapter that reports invalid decimals as normal CLI errors."""
    try:
        parsed = exact(value)
    except DecimalException as exc:
        raise argparse.ArgumentTypeError(f"invalid decimal: {value}") from exc
    if not parsed.is_finite():
        raise argparse.ArgumentTypeError("decimal values must be finite")
    return parsed


def fmt_number(d: Decimal, unit: str = "") -> str:
    """Format large numbers in human-readable form (亿/万亿/B/T)."""
    d = exact(d)
    abs_v = abs(d)
    if unit in ("亿", "亿元", "亿港元", "亿美元"):
        if abs_v >= Decimal("10000"):
            scaled = _CTX.divide(d, Decimal("10000"))
            return f"{scaled:.2f}万亿{unit[1:] if len(unit) > 1 else ''}"
        return f"{d:.2f}{unit}"
    if abs_v >= Decimal("1e12"):
        return f"{_CTX.divide(d, Decimal('1e12')):.2f}T"
    if abs_v >= Decimal("1e9"):
        return f"{_CTX.divide(d, Decimal('1e9')):.2f}B"
    if abs_v >= Decimal("1e6"):
        return f"{_CTX.divide(d, Decimal('1e6')):.2f}M"
    return f"{d:,.2f}"


def relative_deviation(value, reference) -> Decimal:
    """Return an absolute percentage deviation without zero/sign errors."""
    value = exact(value)
    reference = exact(reference)
    if reference == 0:
        return Decimal("0") if value == 0 else Decimal("Infinity")
    return _CTX.multiply(
        _CTX.divide(abs(value - reference), abs(reference)), Decimal("100")
    )


# ---------------------------------------------------------------------------
# 1. Market Cap Verification (股价×总股本 vs 报告市值)
# ---------------------------------------------------------------------------

def verify_market_cap(price, shares, reported_cap, currency=""):
    """Verify market cap = price × shares, compare with reported value."""
    p = exact(price)
    s = exact(shares)
    r = exact(reported_cap)
    if p < 0 or s < 0 or r < 0:
        raise ValueError("price, shares, and reported market cap must be non-negative")

    calculated = _CTX.multiply(p, s)
    deviation = relative_deviation(calculated, r)

    print("=" * 60)
    print("市值验算 (Market Cap Verification)")
    print("=" * 60)
    print(f"  股价 (Price):       {p} {currency}")
    print(f"  总股本 (Shares):    {fmt_number(s)}")
    print(f"  计算市值:           {fmt_number(calculated)} {currency}")
    print(f"  报告市值:           {fmt_number(r)} {currency}")
    print(f"  偏差:               {deviation:.2f}%")
    print()

    if deviation > 5:
        print(f"  ❌ 警告: 偏差 {deviation:.1f}% > 5%, 请检查:")
        print(f"     - 股本是否为最新（回购/增发）?")
        print(f"     - 单位是否一致（港币 vs 人民币 vs 美元）?")
        print(f"     - 股价是否为最新?")
        return False
    elif deviation > 1:
        print(f"  ⚠️  偏差 {deviation:.1f}% 在可接受范围, 可能因股价波动/股本变化")
        return True
    else:
        print(f"  ✅ 验证通过, 偏差仅 {deviation:.2f}%")
        return True


# ---------------------------------------------------------------------------
# 2. Valuation Metrics Verification (估值指标验算)
# ---------------------------------------------------------------------------

def verify_valuation(price, eps=None, bvps=None, fcf_per_share=None,
                     dividend=None, revenue_per_share=None):
    """Calculate and verify key valuation ratios from raw inputs."""
    p = exact(price)
    if p <= 0:
        raise ValueError("price must be greater than zero")

    print("=" * 60)
    print("估值指标验算 (Valuation Verification)")
    print("=" * 60)
    print(f"  当前股价: {p}")
    print()

    results = {}

    if eps is not None:
        e = exact(eps)
        if e != 0:
            pe = _CTX.divide(p, e)
            print(f"  PE (TTM):  {p} / {e} = {pe:.2f}x")
            results["PE"] = float(pe)
            # Earnings yield
            ey = _CTX.divide(e, p) * 100
            print(f"  盈利收益率: {ey:.2f}%")
        else:
            print(f"  PE: EPS为0, 无法计算")

    if bvps is not None:
        b = exact(bvps)
        if b != 0:
            pb = _CTX.divide(p, b)
            print(f"  PB:        {p} / {b} = {pb:.2f}x")
            results["PB"] = float(pb)
            if eps is not None and float(exact(eps)) != 0:
                roe = _CTX.divide(exact(eps), b) * 100
                print(f"  ROE:       {exact(eps)} / {b} = {roe:.2f}%")
                results["ROE"] = float(roe)

    if fcf_per_share is not None:
        f = exact(fcf_per_share)
        if f != 0:
            fcf_yield = _CTX.divide(f, p) * 100
            pfcf = _CTX.divide(p, f)
            print(f"  P/FCF:     {p} / {f} = {pfcf:.2f}x")
            print(f"  FCF Yield: {fcf_yield:.2f}%")
            results["P_FCF"] = float(pfcf)
            results["FCF_Yield"] = float(fcf_yield)

    if dividend is not None:
        d = exact(dividend)
        if p != 0:
            div_yield = _CTX.divide(d, p) * 100
            print(f"  股息率:    {d} / {p} = {div_yield:.2f}%")
            results["Dividend_Yield"] = float(div_yield)

    if revenue_per_share is not None:
        r = exact(revenue_per_share)
        if r != 0:
            ps = _CTX.divide(p, r)
            print(f"  PS:        {p} / {r} = {ps:.2f}x")
            results["PS"] = float(ps)

    print()
    print("  ✅ 以上指标均使用精确十进制计算, 无浮点误差")
    return results


# ---------------------------------------------------------------------------
# 3. Cross-Source Data Validation (多源交叉验证)
# ---------------------------------------------------------------------------

def cross_validate(field_name, source_values: dict, unit="", tolerance_pct=2.0):
    """Compare a data point across multiple sources, flag discrepancies."""
    if not isinstance(source_values, dict) or len(source_values) < 2:
        raise ValueError("cross-validation requires at least two sources")
    tolerance = exact(tolerance_pct)
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")

    print("=" * 60)
    print(f"交叉验证: {field_name} (Cross-Validation)")
    print("=" * 60)

    values = {k: exact(v) for k, v in source_values.items()}
    sources = list(values.keys())
    nums = list(values.values())

    # Find median as reference
    sorted_vals = sorted(nums)
    n = len(sorted_vals)
    median = (
        sorted_vals[n // 2]
        if n % 2 == 1
        else _CTX.divide(sorted_vals[n // 2 - 1] + sorted_vals[n // 2], Decimal("2"))
    )

    print(f"  数据来源数: {len(sources)}")
    print(f"  参考中位数: {fmt_number(exact(median))} {unit}")
    print()

    all_ok = True
    for src, val in values.items():
        dev = relative_deviation(val, median)
        status = "✅" if dev <= tolerance else "❌"
        if dev > tolerance:
            all_ok = False
        print(f"  {status} {src:20s}: {fmt_number(val)} {unit}  (偏差 {dev:.2f}%)")

    print()
    if all_ok:
        print(f"  ✅ 所有来源偏差 ≤ {tolerance}%, 数据一致")
    else:
        print(f"  ⚠️  存在来源偏差 > {tolerance}%, 请核实差异原因")
        print(f"     建议: 优先采用公司年报/交易所数据")

    # Consensus value
    consensus = median
    print(f"\n  共识值 (加权中位数): {fmt_number(exact(consensus))} {unit}")
    return {"consensus": consensus, "all_consistent": all_ok}


# ---------------------------------------------------------------------------
# 4. Benford's Law Quick Check (财务数据造假检测)
# ---------------------------------------------------------------------------

_BENFORD = {d: math.log10(1 + 1/d) for d in range(1, 10)}


def benford_check(values: list):
    """Quick Benford's Law check on a list of financial values."""
    print("=" * 60)
    print("Benford定律检测 (Financial Data Fabrication Check)")
    print("=" * 60)

    # Extract leading digits
    digits = []
    for v in values:
        v = abs(float(v))
        if v > 0:
            sig = 10 ** (math.log10(v) - math.floor(math.log10(v)))
            d = int(sig)
            if 1 <= d <= 9:
                digits.append(d)

    n = len(digits)
    if n < 50:
        print(f"  ⚠️  样本量不足: {n} < 50, Benford分析不可靠")
        return None

    # Observed distribution
    counts = {}
    for d in digits:
        counts[d] = counts.get(d, 0) + 1
    observed = {d: counts.get(d, 0) / n for d in range(1, 10)}

    # MAD (Nigrini's Mean Absolute Deviation)
    mad = sum(abs(observed.get(d, 0) - _BENFORD[d]) for d in range(1, 10)) / 9

    # Chi-square
    chi2 = sum((counts.get(d, 0) - _BENFORD[d] * n) ** 2 / (_BENFORD[d] * n) for d in range(1, 10))

    # Conformity
    if mad < 0.006:
        conformity = "Close (高度符合)"
    elif mad < 0.012:
        conformity = "Acceptable (可接受)"
    elif mad < 0.015:
        conformity = "Marginally Acceptable (边缘)"
    else:
        conformity = "Nonconforming (不符合 ⚠️)"

    print(f"  样本量:    {n}")
    print(f"  MAD:       {mad:.6f}")
    print(f"  Chi-sq:    {chi2:.2f}")
    print(f"  符合度:    {conformity}")
    print()

    # Digit distribution table
    print(f"  {'首位数':>6} {'观测':>8} {'Benford期望':>12} {'偏差':>8}")
    print(f"  {'-'*6} {'-'*8} {'-'*12} {'-'*8}")
    for d in range(1, 10):
        obs = observed.get(d, 0)
        exp = _BENFORD[d]
        dev = obs - exp
        flag = " ⚠️" if abs(dev) > 0.03 else ""
        print(f"  {d:>6d} {obs:>8.3f} {exp:>12.3f} {dev:>+8.3f}{flag}")

    print()
    is_ok = mad < 0.015
    if is_ok:
        print("  ✅ 数据首位数字分布符合Benford定律")
    else:
        print("  ❌ 数据首位数字分布异常, 可能存在人为调整")
        print("     提示: 不符合Benford定律不一定是造假, 但值得进一步调查")

    return {"mad": mad, "chi2": chi2, "conformity": conformity, "is_conforming": is_ok}


# ---------------------------------------------------------------------------
# 5. Exact Calculator (精确计算器)
# ---------------------------------------------------------------------------

_BINARY_OPERATIONS = {
    ast.Add: _CTX.add,
    ast.Sub: _CTX.subtract,
    ast.Mult: _CTX.multiply,
    ast.Div: _CTX.divide,
}
_UNARY_OPERATIONS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _eval_decimal(node: ast.AST, expression: str) -> Decimal:
    """Evaluate the supported arithmetic AST directly as Decimal values."""
    if isinstance(node, ast.Expression):
        return _eval_decimal(node.body, expression)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        if isinstance(node.value, bool):
            raise ValueError("booleans are not valid financial numbers")
        literal = ast.get_source_segment(expression, node)
        return exact((literal or str(node.value)).replace("_", ""))
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATIONS:
        left = _eval_decimal(node.left, expression)
        right = _eval_decimal(node.right, expression)
        return _BINARY_OPERATIONS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATIONS:
        return _UNARY_OPERATIONS[type(node.op)](_eval_decimal(node.operand, expression))
    raise ValueError("only numbers, +, -, *, /, and parentheses are supported")


def exact_calc(expr: str):
    """Evaluate a financial expression with exact decimal arithmetic.

    Supports: +, -, *, /, (), numbers (including scientific notation).
    """
    print("=" * 60)
    print("精确计算 (Exact Calculator)")
    print("=" * 60)

    try:
        tree = ast.parse(expr, mode="eval")
        d_result = _eval_decimal(tree, expr)
        print(f"  表达式: {expr}")
        print(f"  结果:   {fmt_number(d_result)}")
        print(f"  精确值: {d_result}")
        return d_result
    except (SyntaxError, ValueError, DecimalException, ZeroDivisionError) as e:
        print(f"  ❌ 计算错误: {e}")
        return None


# ---------------------------------------------------------------------------
# 6. Three-Scenario Valuation (三情景估值)
# ---------------------------------------------------------------------------

def three_scenario_valuation(current_price, current_eps, shares_billion,
                             growth_optimistic, growth_neutral, growth_pessimistic,
                             pe_optimistic, pe_neutral, pe_pessimistic,
                             years=3, currency=""):
    """Calculate three-scenario target prices with exact arithmetic."""
    print("=" * 60)
    print("三情景估值模型 (Three-Scenario Valuation)")
    print("=" * 60)

    p = exact(current_price)
    eps = exact(current_eps)
    shares = exact(shares_billion)
    if p <= 0:
        raise ValueError("current price must be greater than zero")
    if shares <= 0:
        raise ValueError("shares must be greater than zero")
    if years < 0:
        raise ValueError("years must be non-negative")

    scenarios = [
        ("乐观 (Bull)", growth_optimistic, pe_optimistic),
        ("中性 (Base)", growth_neutral, pe_neutral),
        ("悲观 (Bear)", growth_pessimistic, pe_pessimistic),
    ]

    print(f"  当前股价: {p} {currency}")
    print(f"  当前EPS:  {eps}")
    print(f"  预测期:   {years}年")
    print()
    print(f"  {'情景':12} {'年增速':>8} {'目标PE':>8} {'目标EPS':>10} {'目标股价':>10} {'涨跌幅':>8}")
    print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*10} {'-'*10} {'-'*8}")

    results = []
    for name, growth, pe in scenarios:
        g = exact(growth)
        target_pe = exact(pe)
        if g < Decimal("-1"):
            raise ValueError("growth cannot be less than -100%")
        if target_pe < 0:
            raise ValueError("target PE must be non-negative")
        # Future EPS = current EPS × (1 + growth)^years
        future_eps = eps
        for _ in range(years):
            future_eps = _CTX.multiply(future_eps, _CTX.add(Decimal("1"), g))
        target_price = _CTX.multiply(future_eps, target_pe)
        change = _CTX.multiply(_CTX.divide(target_price - p, p), Decimal("100"))
        target_market_cap = _CTX.multiply(target_price, shares)

        growth_pct = _CTX.multiply(g, Decimal("100"))
        print(f"  {name:12} {growth_pct:>7.0f}% {target_pe:>7.0f}x "
              f"{future_eps:>10.2f} {target_price:>9.1f} {change:>+7.1f}%")
        results.append({
            "scenario": name,
            "future_eps": future_eps,
            "target_price": target_price,
            "target_market_cap_billion": target_market_cap,
            "change_pct": change,
        })

    print()
    print("  ✅ 所有计算使用精确十进制, 结果可审计复现")
    return results


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Financial Rigor Toolkit — 金融数据严谨性验证工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s verify-market-cap --price 510 --shares 9.11e9 --reported 4.65e12 --currency HKD
  %(prog)s verify-valuation --price 510 --eps 23.5 --bvps 120
  %(prog)s cross-validate --field revenue --values '{"年报": 7518, "Yahoo": 7500}' --unit 亿
  %(prog)s benford --values '[1234, 2345, 3456, ...]'
  %(prog)s calc --expr '510 * 9.11e9'
        """)

    sub = parser.add_subparsers(dest="command", required=True)

    # verify-market-cap
    mc = sub.add_parser("verify-market-cap", help="验算市值 = 股价 × 总股本")
    mc.add_argument("--price", type=decimal_arg, required=True)
    mc.add_argument("--shares", type=decimal_arg, required=True, help="总股本")
    mc.add_argument("--reported", type=decimal_arg, required=True, help="报告市值")
    mc.add_argument("--currency", default="", help="币种")

    # verify-valuation
    val = sub.add_parser("verify-valuation", help="验算估值指标")
    val.add_argument("--price", type=decimal_arg, required=True)
    val.add_argument("--eps", type=decimal_arg, default=None)
    val.add_argument("--bvps", type=decimal_arg, default=None, help="每股净资产")
    val.add_argument("--fcf-per-share", type=decimal_arg, default=None)
    val.add_argument("--dividend", type=decimal_arg, default=None, help="每股股息")
    val.add_argument("--revenue-per-share", type=decimal_arg, default=None)

    # cross-validate
    cv = sub.add_parser("cross-validate", help="多源交叉验证")
    cv.add_argument("--field", required=True, help="数据字段名")
    cv.add_argument("--values", required=True, help="JSON: {来源: 数值}")
    cv.add_argument("--unit", default="")
    cv.add_argument("--tolerance", type=decimal_arg, default=Decimal("2.0"), help="容差百分比")

    # benford
    bf = sub.add_parser("benford", help="Benford定律检测")
    bf.add_argument("--values", required=True, help="JSON数组")

    # calc
    ca = sub.add_parser("calc", help="精确计算")
    ca.add_argument("--expr", required=True, help="算术表达式")

    # three-scenario
    ts = sub.add_parser("three-scenario", help="三情景估值")
    ts.add_argument("--price", type=decimal_arg, required=True)
    ts.add_argument("--eps", type=decimal_arg, required=True)
    ts.add_argument("--shares", type=decimal_arg, required=True, help="总股本(亿)")
    ts.add_argument("--growth", nargs=3, type=decimal_arg, required=True,
                    help="三情景年增速 (乐观 中性 悲观), 如 0.15 0.08 0.0")
    ts.add_argument("--pe", nargs=3, type=decimal_arg, required=True,
                    help="三情景目标PE, 如 25 20 15")
    ts.add_argument("--years", type=int, default=3)
    ts.add_argument("--currency", default="")

    args = parser.parse_args()

    try:
        if args.command == "verify-market-cap":
            return 0 if verify_market_cap(
                args.price, args.shares, args.reported, args.currency
            ) else 1
        if args.command == "verify-valuation":
            verify_valuation(args.price, args.eps, args.bvps, args.fcf_per_share,
                             args.dividend, args.revenue_per_share)
            return 0
        if args.command == "cross-validate":
            result = cross_validate(
                args.field, json.loads(args.values), args.unit, args.tolerance
            )
            return 0 if result["all_consistent"] else 1
        if args.command == "benford":
            result = benford_check(json.loads(args.values))
            return 0 if result is None or result["is_conforming"] else 1
        if args.command == "calc":
            return 0 if exact_calc(args.expr) is not None else 1
        if args.command == "three-scenario":
            three_scenario_valuation(
                args.price, args.eps, args.shares,
                args.growth[0], args.growth[1], args.growth[2],
                args.pe[0], args.pe[1], args.pe[2],
                args.years, args.currency)
            return 0
    except (DecimalException, ValueError, ZeroDivisionError, json.JSONDecodeError) as exc:
        print(f"❌ 输入错误: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
