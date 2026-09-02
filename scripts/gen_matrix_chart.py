#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_matrix_chart.py — 生成估值矩阵信息图（PNG）
用法: python gen_matrix_chart.py [--out 输出路径]

风格: 深蓝黑底（公众号视觉规范），账本意象，一图流转发物
v1.15.0 重写：矩阵数据从 matrix_data.py 单一权威源 import（原 ROWS 是 v1.7 旧版——6 行旧结构/30-50x 残留已废弃）
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

from matrix_data import MATRIX, HK_MATRIX_TIER1, TIER_NAMES

# 中文字体：Windows → macOS → Linux 依次兜底（v1.15.1：frontmatter 声明三平台，原列表非 Windows 环境仅 Arial Unicode MS 一项）
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "SimSun", "PingFang SC", "Hiragino Sans GB", "Arial Unicode MS", "Noto Sans CJK SC", "Source Han Sans SC", "WenQuanYi Micro Hei"]
matplotlib.rcParams["axes.unicode_minus"] = False

COLS = ["<15%", "15-30%", "30-60%", ">60%"]

# 展示用行（tier0-3 + infra；港股一档单独列——美股带对中国公司不适用场景多，主图用港股一档更实用）
def build_rows():
    """从 matrix_data 构造图表行（档位名, [g1..g4 文本], 着色中值）"""
    def fmt(t):
        return f"{t[0]:.1f}-{t[1]:.1f}x"
    rows = [
        ("第零档 · 项目制（含沉淀）", [fmt(MATRIX["tier0"][g]) for g in ["g1", "g2", "g3", "g4"]], 0),
        ("一档 · 订阅（港股带）", [fmt(HK_MATRIX_TIER1[g]) for g in ["g1", "g2", "g3", "g4"]], 1),
        ("一档 · 订阅（美股带）", [fmt(MATRIX["tier1"][g]) for g in ["g1", "g2", "g3", "g4"]], 2),
        ("二档 · 转售智能", [fmt(MATRIX["tier2"][g]) for g in ["g1", "g2", "g3", "g4"]], 3),
        ("三档 · 自研智能", [fmt(MATRIX["tier3"][g]) for g in ["g1", "g2", "g3", "g4"]], 4),
        ("算力 / Infra（重资产）", [fmt(MATRIX["infra"][g]) for g in ["g1", "g2", "g3", "g4"]], 5),
    ]
    return rows

ROWS = build_rows()

# 每个格子中值（热力着色用）——港股带/美股带同一档用两者混合可读
def mid(v):
    return (v[0] + v[1]) / 2

VALUES = [
    [mid(MATRIX["tier0"]["g1"]), mid(MATRIX["tier0"]["g2"]), mid(MATRIX["tier0"]["g3"]), mid(MATRIX["tier0"]["g4"])],
    [mid(HK_MATRIX_TIER1["g1"]), mid(HK_MATRIX_TIER1["g2"]), mid(HK_MATRIX_TIER1["g3"]), mid(HK_MATRIX_TIER1["g4"])],
    [mid(MATRIX["tier1"]["g1"]), mid(MATRIX["tier1"]["g2"]), mid(MATRIX["tier1"]["g3"]), mid(MATRIX["tier1"]["g4"])],
    [mid(MATRIX["tier2"]["g1"]), mid(MATRIX["tier2"]["g2"]), mid(MATRIX["tier2"]["g3"]), mid(MATRIX["tier2"]["g4"])],
    [mid(MATRIX["tier3"]["g1"]), mid(MATRIX["tier3"]["g2"]), mid(MATRIX["tier3"]["g3"]), mid(MATRIX["tier3"]["g4"])],
    [mid(MATRIX["infra"]["g1"]), mid(MATRIX["infra"]["g2"]), mid(MATRIX["infra"]["g3"]), mid(MATRIX["infra"]["g4"])],
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_path = args.out or os.path.join(skill_dir, "assets", "valuation-matrix.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 6.8), dpi=160)
    fig.patch.set_facecolor("#0d1b2a")  # 深蓝黑
    ax.set_facecolor("#0d1b2a")

    # 热力着色（金色渐变，账本意象）
    norm = mcolors.Normalize(vmin=0, vmax=45)
    cmap = matplotlib.colormaps["YlOrBr"]

    n_rows, n_cols = len(ROWS), len(COLS)
    for i in range(n_rows):
        for j in range(n_cols):
            val = VALUES[i][j]
            color = cmap(norm(val)) if val > 0 else "#1b2a41"
            rect = plt.Rectangle((j, n_rows - 1 - i), 1, 1, facecolor=color, edgecolor="#0d1b2a", linewidth=2)
            ax.add_patch(rect)
            text_color = "#ffffff" if norm(val) > 0.55 else "#f0d9a8"
            txt = ROWS[i][1][j]
            ax.text(j + 0.5, n_rows - 1 - i + 0.5, txt, ha="center", va="center",
                    fontsize=11, fontweight="bold", color=text_color, linespacing=1.4)

    # 轴标签
    ax.set_xticks([i + 0.5 for i in range(n_cols)])
    ax.set_xticklabels([f"增速 {c}" for c in COLS], fontsize=12, color="#f0d9a8")
    ax.set_yticks([n_rows - 1 - i + 0.5 for i in range(n_rows)])
    ax.set_yticklabels([r[0] for r in ROWS], fontsize=11.5, color="#f0d9a8")

    # 标题
    ax.set_title("AI 应用公司估值矩阵\nPS × 增速（Wind S 级校准 v1.15.0）", fontsize=17, color="#ffffff",
                 fontweight="bold", pad=18)
    ax.text(0.5, -0.09, "档位决定天花板 · 增速决定同档内位置 · 港股一档扁平 2.5-6x（增速期权≈0）· 转售毛利锁死（Liblib 6.7x 实证）",
            transform=ax.transAxes, ha="center", fontsize=10, color="#c9a86a")

    # 修正系数注脚
    ax.text(0.5, -0.15,
            "修正：垂直赛道 ×1.5-2｜毛利 <40%×0.7 / 40-55%×1.0 / 55%+×1.3｜质量 ≥8 上沿 / <6 下沿｜近零增长 <3%×0.65",
            transform=ax.transAxes, ha="center", fontsize=9, color="#8a9ab5")

    ax.set_xlim(0, n_cols)
    ax.set_ylim(0, n_rows)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"✅ 矩阵图已生成: {out_path}")


if __name__ == "__main__":
    main()
