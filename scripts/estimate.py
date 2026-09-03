#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
estimate.py — AI 应用公司估值引擎（确定性计算，无 LLM）

用法:
    python estimate.py --arr 100 --arr-type total --tier 3 --growth 0.8 --quality 8.5 [--corr vertical1.5] [--corr founder80]

职责:
    输入判断性字段（档位/增速/质量分/修正），输出估值区间 + 完整推导。
    所有算术由本脚本完成，LLM 只负责填输入和解释——防算数幻觉。

矩阵数据（2026-08 核验版，刷新流程见 references/anchor-calibration.md §2）:
    档位 × 增速 → PS 区间
    修正系数: 垂直赛道 ×1.5-2 / 创始人溢价(上沿 80x) / 中国溢价等

输出:
    最低/中位/最高估值 + 每一步推导 + 超限告警
"""
import argparse
import json
import sys
from matrix_data import MATRIX, HK_MATRIX_TIER1, GROWTH_BANDS, TIER_NAMES


# 增速档判定
def growth_band(growth: float) -> str:
    """growth: 0-1 的小数（0.8 = 80%）"""
    if growth is None:
        return "g1"  # 未知按保守
    if growth < 0.15:
        return "g1"
    if growth < 0.30:
        return "g2"
    if growth < 0.60:
        return "g3"
    return "g4"

# 质量分调节: ≥8 上沿 / 6-8 中带 / <6 下沿
def quality_adjust(quality: float, lo: float, hi: float):
    """返回 (倍数下限, 倍数上限)"""
    span = hi - lo
    if quality >= 8.0:
        return (hi - span * 0.25, hi)          # 上沿
    if quality >= 6.0:
        return (lo + span * 0.25, hi - span * 0.25)  # 中带
    return (lo, lo + span * 0.25)              # 下沿

# 档内增速插值（v1.7）：增速在增速档内的相对位置决定倍数区间偏移（最多 ±区间宽度 25%）
# 30% 增速与 60% 增速不能同格同价——增速越高，区间整体上移（质量分调节之前做）
def growth_interpolate(growth: float, band: str, lo: float, hi: float):
    """返回 (插值后 lo, hi, 说明文本)"""
    b_lo, b_hi = GROWTH_BANDS[band]
    pos = (growth - b_lo) / (b_hi - b_lo)
    pos = max(0.0, min(1.0, pos))
    span = hi - lo
    offset = (pos - 0.5) * span * 0.5  # 最多 ±区间宽度的 25%
    new_lo, new_hi = lo + offset, hi + offset
    note = (f"档内增速插值: {growth*100:.0f}% 在 {band} 带内位置 {pos*100:.0f}% "
            f"→ 区间偏移 {offset:+.2f}x → {new_lo:.1f}-{new_hi:.1f}x")
    return new_lo, new_hi, note

# 修正系数（叠加到倍数上限；垂直赛道×1.5-2 乘下限上限，创始人溢价=上限提到 80x 特例）
KNOWN_CORR = {
    "vertical1.5": "垂直赛道溢价 ×1.5",
    "vertical2.0": "垂直赛道溢价 ×2.0",
    "founder80": "创始人/战略溢价（上沿 80x，极少数）",
    "china_sub": "中国订阅稀缺溢价（如金山办公类）",
    "ai_narrative": "AI 叙事溢价 ×1.5-2（CRWD/NET 类）",
    "margin_soft": "毛利 <40%（服务级，×0.7——范式智能实证）",
    "margin_mid": "毛利 40-55%（混合，×1.0）",
    "margin_high": "毛利 55%+（软件级，×1.3）",
    "asset_heavy": "算力段·重资产自持（5-10x 国内校准：优刻得 7.57x/首都在线 7.69x/并行 4.45x；折旧吃利润，增速期权≈0）",
    "asset_light": "算力段·轻资产纳管/调度（15-25x 推断格，软件属性；Nebius 46.1x 是软件厚度例外）",
}

def apply_corr(lo, hi, corr_key):
    """返回 (新lo, 新hi, 说明)"""
    if corr_key == "vertical1.5":
        return lo * 1.5, hi * 1.5, "垂直赛道溢价 ×1.5"
    if corr_key == "vertical2.0":
        return lo * 2.0, hi * 2.0, "垂直赛道溢价 ×2.0"
    if corr_key == "founder80":
        # v1.15.1：SKILL「上沿 80x」= 上限封顶 80x，下限不高于上限（原实现在乘法系数之后应用会出现下限>上限）
        return min(lo, 80.0), 80.0, "创始人/战略溢价：上限封顶 80x（Sierra 级，极少数）"
    if corr_key == "china_sub":
        return lo * 1.5, hi * 1.5, "中国订阅稀缺溢价 ×1.5（金山办公类）"
    if corr_key == "ai_narrative":
        return lo * 1.5, hi * 1.5, "AI 叙事溢价 ×1.5（CRWD/NET 类）"
    if corr_key == "margin_soft":
        return lo * 0.7, hi * 0.7, "毛利 <40%（服务级，×0.7——范式智能 34.8% 市场只给 1.87x）"
    if corr_key == "margin_mid":
        return lo, hi, "毛利 40-55%（混合，×1.0）"
    if corr_key == "margin_high":
        return lo * 1.3, hi * 1.3, "毛利 55%+（软件级，×1.3）"
    if corr_key == "asset_heavy":
        return lo, hi, "算力段·重资产自持 5-10x（国内校准，增速期权≈0）"
    if corr_key == "asset_light":
        return 15.0, 25.0, "算力段·轻资产纳管 15-25x（软件属性，推断格——Nebius 46.1x 软件厚度例外）"
    return lo, hi, f"未知修正({corr_key})，忽略"

def main():
    ap = argparse.ArgumentParser(description="AI 应用公司估值引擎（确定性）")
    ap.add_argument("--arr", type=float, required=True, help="ARR（百万美元）")
    ap.add_argument("--arr-type", choices=["total", "b2b", "agentic"], default="total",
                    help="ARR 口径（Cursor 教训：total 15x vs B2B 23x）")
    ap.add_argument("--tier", choices=list(TIER_NAMES.keys()), required=True, help="档位")
    ap.add_argument("--growth", type=float, default=None, help="增速（0.8 = 80%%）")
    ap.add_argument("--quality", type=float, default=6.0, help="质量分 0-10")
    ap.add_argument("--corr", action="append", default=[], help="修正系数（可多个）")
    ap.add_argument("--market", choices=["us", "hk"], default="hk", help="市场锚带：默认 hk（中国 AI 应用默认港股锚带，v1.9.0）；仅明确美股公司传 us")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args()
    if not (0.0 <= args.quality <= 10.0):
        ap.error(f"--quality 必须在 0-10 之间（收到 {args.quality}）")
    growth_txt = "未知（按 g1 保守）" if args.growth is None else f"{args.growth*100:.0f}%"

    band = growth_band(args.growth)
    cell = MATRIX[args.tier].get(band)
    if cell is None:
        print(f"⚠️ 档位 {TIER_NAMES[args.tier]} × 增速档 {band} 无样本（少见组合）——建议重估档位或增速。")
        if args.json:
            print(json.dumps({"error": "no_sample"}, ensure_ascii=False))
        sys.exit(1)

    lo, hi = cell
    # 港股锚带覆盖（v1.7.12 双轨制：仅 tier1 一档有 8 家实证；其他档位港股待实测）
    market_note = ""
    if args.market == "hk" and args.tier == "tier1":
        hk_cell = HK_MATRIX_TIER1.get(band)
        if hk_cell:
            lo, hi = hk_cell
            market_note = f"港股锚带 {lo:.1f}-{hi:.1f}x（v1.7.12 双轨制：中国 AI 应用默认港股框架）"
        else:
            market_note = f"港股锚带：tier1×{band} 无实证，用美股带"
    elif args.market == "hk":
        market_note = f"⚠️ 港股 {TIER_NAMES[args.tier]} 待实测（仅 tier1 有 8 家锚），暂用美股带"
    base_lo, base_hi = lo, hi
    steps = []
    steps.append(f"增速 {growth_txt} → 增速档 {band}（<15/15-30/30-60/>60）")
    steps.append(f"矩阵格子: {TIER_NAMES[args.tier]} × {band} = {lo:.1f}-{hi:.1f}x")
    if market_note:
        steps.append(market_note)

    # 档内增速插值（v1.7）：增速在档内位置决定区间偏移（30% 与 60% 不同价）
    # ⚠️ infra 段跳过（v1.10.0）：算力段增速期权≈0——重资产公用事业化定价，折旧吃利润，增速不转化为倍数（优刻得 +117% 只给 4.45x）
    # ⚠️ tier3 g4 宽格跳过（v1.13.4 bug 修复）：15-50x 跨度本身靠质量分定位（质量<7 下沿 15-25x / ≥8 上沿 40-50x），
    #    增速已含在跨度定价内（Harvey 80% 增速 → 44x 上沿无需再 +8.75x 插值）；叠加插值会撑爆区间（15-50 → 23.8-58.8）
    if args.tier == "infra":
        steps.append("infra 段跳过档内增速插值（算力段增速期权≈0，重资产公用事业化定价）")
    elif args.tier == "tier3" and band == "g4":
        steps.append("tier3 g4 宽格跳过增速插值（15-50x 跨度已含增速定价，靠质量分定位上下沿）")
    elif args.growth is None:
        steps.append("增速未知，跳过档内增速插值（按 g1 保守取格）")
    else:
        lo, hi, note = growth_interpolate(args.growth, band, lo, hi)
        steps.append(note)

    # 质量分调节
    # ⚠️ tier3 g4 独立规则（v1.13.4）：该格 15-50x 是「下沿自研/入口 vs 上沿收智慧租」的双锚结构，
    #    注释语义「质量<7 下沿 15-25x / 质量≥8 上沿 40-50x / 7-8 中带 25-40x」——
    #    与全局 ≥6 中带规则冲突，需按档内双判据（飞轮闭环+高切换成本）定位：
    #    <7 = 无飞轮/低切换（Cursor 15x/ElevenLabs 22x 类）→ 15-25x
    #    7-8 = 有飞轮缺切换成本或反之 → 25-40x
    #    ≥8 = 飞轮闭环+高切换（Harvey/Perplexity/Palantir 类）→ 40-50x
    if args.tier == "tier3" and band == "g4":
        if args.quality >= 8.0:
            q_lo, q_hi = 40.0, 50.0
            q_label = "上沿·收智慧租（飞轮闭环+高切换成本）"
        elif args.quality >= 7.0:
            q_lo, q_hi = 25.0, 40.0
            q_label = "中带（飞轮或切换成本单缺）"
        else:
            q_lo, q_hi = 15.0, 25.0
            q_label = "下沿·自研/入口无飞轮（Cursor 15x/ElevenLabs 22x）"
        steps.append(f"质量分 {args.quality:.1f} → {q_label} {q_lo:.1f}-{q_hi:.1f}x")
    else:
        q_lo, q_hi = quality_adjust(args.quality, lo, hi)
        steps.append(f"质量分 {args.quality:.1f} → {'上沿' if args.quality>=8 else '中带' if args.quality>=6 else '下沿'} {q_lo:.1f}-{q_hi:.1f}x")
    lo, hi = q_lo, q_hi

    # 修正系数（v1.15.1：应用顺序固定，与命令行顺序无关——原实现按命令行顺序叠加，
    #   founder80 先于 vertical1.5 得上限 120x、反序得 80x）
    #   ① asset_light 换带：算力段轻资产 15-25x 是基准格切换，先换带再叠乘法修正，超限阈值随之按 25x 计
    #      （原实现 asset_light 后仍按重资产格 10x×2 判超限，每次必触发告警）
    #   ② 乘法类（vertical/china_sub/ai_narrative/margin_*）——可交换
    #   ③ founder80 封顶：最后应用
    CORR_FIRST, CORR_LAST = ("asset_light",), ("founder80",)
    ordered = ([c for c in args.corr if c in CORR_FIRST]
               + [c for c in args.corr if c not in CORR_FIRST and c not in CORR_LAST]
               + [c for c in args.corr if c in CORR_LAST])
    corr_notes = []
    peak_hi = hi  # 修正链中出现过的最高上限（founder80 封顶前）——超限告警按它判，封顶不掩盖叠加过度
    for c in ordered:
        if c == "asset_light" and args.tier != "infra":
            corr_notes.append("asset_light 仅算力段（--tier infra）有效，忽略")
            continue
        lo, hi, note = apply_corr(lo, hi, c)
        if c == "asset_light":
            base_lo, base_hi = lo, hi
        peak_hi = max(peak_hi, hi)
        corr_notes.append(note)
    if corr_notes:
        steps.append("修正叠加: " + " + ".join(corr_notes))

    # ARR 口径说明
    arr_type_note = {
        "total": "total 口径（总 ARR）",
        "b2b": "B2B 口径（企业收入）",
        "agentic": "agentic 口径（AI 业务段）",
    }[args.arr_type]

    # 估值
    val_lo = args.arr * lo
    val_mid = args.arr * (lo + hi) / 2
    val_hi = args.arr * hi

    # 超限告警：倍数上限超过档位格子的 2 倍（修正过度）
    max_sane = base_hi * 2.0
    warning = ""
    if peak_hi > max_sane:
        warning = (f"\n⚠️ 超限告警: 修正链中倍数上限达 {peak_hi:.0f}x，超过档位格子上限（{base_hi:.0f}x）的 2 倍——"
                   f"检查: ①档位判定是否过高 ②修正系数是否叠加过度 ③增速是否虚报。")

    # 锚点校准提示
    anchor_hint = {
        "tier0": "锚: 中软国际 0.5x / 埃森哲 1.7x / Cognizant 1.3x / EPAM 1.0x / 范式 1.87x（g3 硬锚）——g4 推断格 2.5-3.5x 无硬锚，项目制增速期权≈0",
        "tier1": "锚: 港股 g1-g4 2.5-6x（金蝶 3.55/美图 4.44/迈富时 4.88/联易融 5-6x）｜美股 g1-g4 4.6-25x（CRM/NOW/SNOW/PLTR 溢价）",
        "tier2": "锚: Liblib 6.7x（2026-08 IPO 前 $3B/$300M，36氪/彭博）——转售增速期权≈0",
        "tier3": "锚: 下沿自研/入口 15-25x（Cursor 15x 收购价含溢价/ElevenLabs 22x/Suno 18x/Replit 17.1x/Lovable 26.6x）｜上沿收智慧租 30-50x（Harvey 44-52x/Perplexity 40-51x/Palantir 70x）——档内飞轮+切换成本插值，来源 comps-source.md",
        "infra": "锚: 重资产自持 5-10x（优刻得 7.57x/首都在线 7.69x/并行 4.45x，CoreWeave 10.3x 海外参考）｜轻资产纳管 15-25x（推断格，Nebius 46.1x 软件厚度例外）——SOTP 单列不入应用矩阵",
    }[args.tier]

    out = {
        "输入": {"ARR": f"${args.arr}M", "口径": arr_type_note, "档位": TIER_NAMES[args.tier],
                 "增速": growth_txt, "质量分": args.quality, "修正": args.corr},
        "推导": steps,
        "倍数": {"低": round(lo, 1), "中位": round((lo+hi)/2, 1), "高": round(hi, 1)},
        "估值": {"低": f"${val_lo:.0f}M", "中位": f"${val_mid:.0f}M", "高": f"${val_hi:.0f}M"},
        "锚点": anchor_hint,
        "告警": warning.strip() if warning else None,
        "口径纪律": "倍数必须带口径（total/B2B/agentic）——Cursor 15x(total) vs 23x(B2B)",
        "置信度": "🟡 中确信（矩阵为时点数据，标注刷新日期）",
    }

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    print("=" * 60)
    print(f"AI 应用公司估值 · {TIER_NAMES[args.tier]} · {arr_type_note}")
    print("=" * 60)
    print(f"输入: ARR ${args.arr:.0f}M | 档位 {TIER_NAMES[args.tier]} | 增速 {growth_txt} | 质量分 {args.quality:.1f}")
    print()
    for s in steps:
        print(f"→ {s}")
    print()
    print(f"倍数区间: {lo:.1f}-{hi:.1f}x")
    print(f"估值区间: ${val_lo:.0f}M - ${val_mid:.0f}M - ${val_hi:.0f}M（低/中位/高）")
    if warning:
        print(warning)
    print()
    print(f"锚点参照: {anchor_hint}")
    print(f"置信度: 🟡 中确信（矩阵数据截至 refresh 日期，AI 估值半年一变）")

if __name__ == "__main__":
    main()
