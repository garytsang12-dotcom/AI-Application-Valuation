#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_estimate.py — estimate.py 全档位回归测试（v1.12.0 新增）
=============================================================
覆盖：4 档 + infra × 4 增速带 × 质量分边界，断言：
  1. 倍数落在矩阵格子范围内（允许档内插值 ±25% 偏移）
  2. tier2 转售不倒挂（g3 ≥ g4 或接近，增速期权≈0）
  3. 增速越高倍数越高（同档内单调，tier2 允许持平）
  4. 质量分调节方向正确（质量 8.5 ≥ 质量 5）
  5. 港股 vs 美股锚带差异（tier1 港股 g4 < 美股 g4）
  6. 超限告警触发（tier2 高速 + 高质量不应超 8x 上沿太多）

用法: python scripts/test_estimate.py
改动 estimate.py 后必跑防回归。
"""
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "estimate.py"

# 矩阵格子（与 estimate.py MATRIX 同步，测试时以脚本实际输出为准）
# 这里只存「预期带」用于断言，漂移检测靠 range 检查
EXPECTED_BANDS = {
    "tier0": {"g1": (0.5, 1.5), "g2": (1.5, 2.0), "g3": (1.5, 2.5), "g4": (2.5, 3.5)},
    # tier1 默认港股锚带（v1.9.0 --market 默认 hk）；美股带 g2-g4 更高（6-25x）
    "tier1": {"g1": (2.5, 4.0), "g2": (3.0, 5.0), "g3": (3.5, 6.0), "g4": (4.0, 6.0)},
    "tier2": {"g1": (3.0, 5.0), "g2": (5.0, 8.0), "g3": (5.0, 8.0), "g4": (5.0, 8.0)},
    "tier3": {"g1": (5.0, 8.0), "g2": (8.0, 15.0), "g3": (15.0, 25.0), "g4": (15.0, 50.0)},
    "infra": {"g1": (5.0, 10.0), "g2": (5.0, 10.0), "g3": (5.0, 10.0), "g4": (5.0, 10.0)},
}

# 增速代表值（g1=8%, g2=22%, g3=45%, g4=80%）
GROWTH_SAMPLES = {"g1": 0.08, "g2": 0.22, "g3": 0.45, "g4": 0.80}

pass_count = 0
fail_count = 0
failures = []


def run_estimate(tier, growth, quality, market="hk", corr=None):
    cmd = [sys.executable, str(SCRIPT), "--arr", "100", "--tier", tier,
           "--growth", str(growth), "--quality", str(quality), "--json"]
    if market:
        cmd += ["--market", market]
    if corr:
        cmd += ["--corr", corr]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def check(name, cond, detail=""):
    global pass_count, fail_count
    if cond:
        pass_count += 1
        print(f"  ✅ {name}")
    else:
        fail_count += 1
        failures.append(f"{name}: {detail}")
        print(f"  ❌ {name}: {detail}")


def main():
    print("=" * 60)
    print("test_estimate: 全档位回归")
    print("=" * 60)

    # ---- 1. 每档每增速：倍数在矩阵带内（含插值偏移容差） ----
    print("\n[1] 矩阵格范围检查（4 档 + infra × 4 增速）")
    for tier, bands in EXPECTED_BANDS.items():
        for g, growth in GROWTH_SAMPLES.items():
            lo, hi = bands[g]
            # 插值可能使结果略低于 lo（档内低增速位）——容差 15%
            tol_lo = lo * 0.75
            tol_hi = hi * 1.25
            out = run_estimate(tier, growth, 6.5, market="hk")
            if out is None:
                check(f"{tier} {g}", False, "estimate.py 调用失败")
                continue
            mid = out["倍数"]["中位"]
            ok = tol_lo <= mid <= tol_hi
            check(f"{tier} {g}（预期 {lo}-{hi}x，实际中位 {mid}x）", ok,
                  f"中位 {mid}x 超出容差 [{tol_lo:.1f}, {tol_hi:.1f}]")

    # ---- 2. tier2 不倒挂：g3 ≥ g4（或接近，增速期权≈0） ----
    print("\n[2] tier2 转售不倒挂检查")
    g3 = run_estimate("tier2", GROWTH_SAMPLES["g3"], 6.5)
    g4 = run_estimate("tier2", GROWTH_SAMPLES["g4"], 6.5)
    if g3 and g4:
        m3, m4 = g3["倍数"]["中位"], g4["倍数"]["中位"]
        check("tier2 g3 中位 >= g4 中位（不倒挂）", m3 >= m4 * 0.98,
              f"g3={m3}x g4={m4}x 倒挂")
    else:
        check("tier2 g3/g4 调用", False, "调用失败")

    # ---- 3. 增速单调性：同档内 g4 ≥ g1（tier2 允许持平） ----
    print("\n[3] 增速单调性（g4 中位 >= g1 中位，tier2 允许接近）")
    for tier in ["tier0", "tier1", "tier2", "tier3", "infra"]:
        g1 = run_estimate(tier, GROWTH_SAMPLES["g1"], 6.5)
        g4 = run_estimate(tier, GROWTH_SAMPLES["g4"], 6.5)
        if g1 and g4:
            m1, m4 = g1["倍数"]["中位"], g4["倍数"]["中位"]
            # tier2/infra 允许持平（增速期权≈0），其余必须 g4 > g1
            if tier in ("tier2", "infra"):
                ok = m4 >= m1 * 0.95
                desc = f"g1={m1}x g4={m4}x（允许持平）"
            else:
                ok = m4 > m1
                desc = f"g1={m1}x g4={m4}x（必须递增）"
            check(f"{tier} g4>=g1", ok, desc)
        else:
            check(f"{tier} g4>=g1", False, "调用失败")

    # ---- 4. 质量分调节方向 ----
    print("\n[4] 质量分调节方向（质量 8.5 中位 >= 质量 5 中位）")
    for tier in ["tier1", "tier3"]:
        q5 = run_estimate(tier, 0.45, 5.0)
        q85 = run_estimate(tier, 0.45, 8.5)
        if q5 and q85:
            m5, m85 = q5["倍数"]["中位"], q85["倍数"]["中位"]
            check(f"{tier} 质量8.5>=质量5", m85 >= m5,
                  f"质量5={m5}x 质量8.5={m85}x")
        else:
            check(f"{tier} 质量调节", False, "调用失败")

    # ---- 5. 港股 vs 美股锚带差异（tier1 g4 港股 < 美股） ----
    print("\n[5] 港股/美股双轨锚带（tier1 g4）")
    hk = run_estimate("tier1", 0.80, 6.5, market="hk")
    us = run_estimate("tier1", 0.80, 6.5, market="us")
    if hk and us:
        mh, mu = hk["倍数"]["中位"], us["倍数"]["中位"]
        check("港股 g4 < 美股 g4", mh < mu, f"港股={mh}x 美股={mu}x")
    else:
        check("港股/美股 g4", False, "调用失败")

    # ---- 6. 超限告警（tier2 g4 高质量不应给转售档 8x 以上） ----
    print("\n[6] 超限告警（tier2 增速 80% + 质量 9 不应突破 10x）")
    out = run_estimate("tier2", 0.80, 9.0)
    if out:
        hi = out["倍数"]["高"]
        check("tier2 高速高质量高值 <= 10x", hi <= 10.0, f"高值 {hi}x")
    else:
        check("tier2 告警", False, "调用失败")

    # ---- 7. infra 重/轻资产区分 ----
    print("\n[7] infra 重/轻资产区分")
    heavy = run_estimate("infra", 0.45, 6.5, corr="asset_heavy")
    light = run_estimate("infra", 0.45, 6.5, corr="asset_light")
    if heavy and light:
        mh, ml = heavy["倍数"]["中位"], light["倍数"]["中位"]
        check("infra 轻资产 > 重资产", ml > mh, f"重={mh}x 轻={ml}x")
    else:
        check("infra 轻重", False, "调用失败")

    # ---- 8. tier3 g4 宽格质量分层（v1.13.4 bug 修复回归）----
    print("\n[8] tier3 g4 宽格质量分层（15-50x 双锚定位）")
    q5 = run_estimate("tier3", 1.0, 5.0)
    q7 = run_estimate("tier3", 1.0, 7.0)
    q85 = run_estimate("tier3", 1.0, 8.5)
    if q5 and q7 and q85:
        m5, m7, m85 = q5["倍数"]["中位"], q7["倍数"]["中位"], q85["倍数"]["中位"]
        check("质量5 下沿（<=25x）", m5 <= 25.0, f"质量5中位={m5}x 应<=25")
        check("质量7 中带（25-40x）", 25.0 <= m7 <= 40.0, f"质量7中位={m7}x 应在[25,40]")
        check("质量8.5 上沿（>=40x）", m85 >= 40.0, f"质量8.5中位={m85}x 应>=40")
        check("质量分层单调（5<7<8.5）", m5 < m7 < m85, f"{m5}<{m7}<{m85}")
    else:
        check("tier3 g4 质量分层", False, "调用失败")

    # ---- 汇总 ----
    print("\n" + "=" * 60)
    print(f"结果: {pass_count} 通过, {fail_count} 失败")
    if failures:
        print("\n失败明细:")
        for f in failures:
            print(f"  - {f}")
    print("=" * 60)
    sys.exit(1 if fail_count else 0)


if __name__ == "__main__":
    main()
