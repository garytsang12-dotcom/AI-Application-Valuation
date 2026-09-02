#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""matrix_data.py — 估值矩阵单一权威源（v1.15.0 合并：estimate/validate/chart 从此 import，改矩阵只动此文件）

背景（v1.15.0 脚本合并审计——主人「检查效验和计算脚本全局，有无合并空间」）：
    估值矩阵数据原本散落 estimate.py(MATRIX/HK_MATRIX_TIER1/GROWTH_BANDS/TIER_NAMES) +
    validate.py(TIER_RANGE/MATRIX_REF) + gen_matrix_chart.py(ROWS)，改一个倍数要动 3-4 个文件，
    且 validate 的 MATRIX_REF 文档注释已过期（残留 v1.7.10 废弃的 30-50x）——「五源同步」事故根源。

    v1.15.0 合并：本文件 = 唯一矩阵数据源；estimate.py/validate.py/gen_matrix_chart.py 全部从这里 import。
    MATRIX_REF 过期注释已删（用 MATRIX 派生校验范围，不再维护第二份文档）。
"""

# ═══════════════ 档位 × 增速 估值矩阵（v1.14.2 Wind S 级校准）═══════════════

# 档位×增速矩阵（倍数 PS，增速 g1-g4）。档位分类与完整定义见 SKILL.md / references/definitions.md §10。
MATRIX = {
    "tier0": {"g1": (0.5, 1.5), "g2": (1.5, 2.0), "g3": (1.5, 2.5), "g4": (2.5, 3.5)},  # 项目制（含沉淀定性）：g1-g3 硬锚（服务公司 0.5-2.5x / 范式 1.87x）；g4 ⚠️推断格无硬锚——项目制增速期权≈0（高增速不复利），取区间下沿
    # (tier0s 已合并入 tier0，v1.8.5——沉淀定性见质量分数据回流/归因资产化)
    "tier1": {"g1": (3.0, 5.0), "g2": (6.0, 10.0), "g3": (15.0, 25.0), "g4": (15.0, 25.0)},  # 海外（v1.14.2 Wind S 级校准 2026-09-01：g1 锚 4.4-4.8x 密集 Salesforce/Adobe/Intuit/Workday——原区间正确；g2 锚 Atlassian 7.2/ServiceNow 10.6——Datadog 21.9x 质量溢价例外不拉高整格；g3 锚 Snowflake 22.0/Cloudflare 43.6x AI 溢价剔除；废弃 30-50x 见 v1.7.10；中国走港股锚带 HK_MATRIX_TIER1）,
    "tier2": {"g1": (3.0, 5.0), "g2": (5.0, 8.0), "g3": (5.0, 8.0), "g4": (5.0, 8.0)},  # 转售智能：Liblib 6.7x 铁锚（2026-08 IPO 前 $3B/$300M，36氪/彭博）——增速期权≈0；v1.12 修正倒挂：g3/g4 对齐（转售增速带内无区分，Liblib +3000% 仍 6.7x）
    "tier3": {"g1": (5.0, 8.0), "g2": (8.0, 15.0), "g3": (15.0, 25.0), "g4": (15.0, 50.0)},  # 自研智能（v1.9.0 并 tier2s）：g4 跨度 15-50x 靠质量分定位——质量<7 下沿 15-25x（自研无飞轮：Cursor 15x/ElevenLabs 22x），质量≥8 上沿 40-50x（收智慧租：Harvey 44x/Perplexity 40x/Palantir 70x）；档内飞轮闭环+高切换成本判据,
    # 算力/Infra 段（v1.10.0 加 --tier infra，2026-09-01 主人要求——definitions.md §9 锚点入引擎）：
    #   重资产自持 5-10x（国内校准：优刻得 7.57x / 首都在线 7.69x / 并行 4.45x / CoreWeave 10.3x 海外上限参考）——用 --corr asset_heavy
    #   轻资产纳管/调度 15-25x（推断格，Nebius 46.1x 是软件厚度例外）——用 --corr asset_light
    #   判据（全部满足才算算力段）：自持/纳管算力 + Token 按量计费 + 异构调度技术；非应用层转售（Liblib/OpenRouter 锚不适用）
    "infra": {"g1": (5.0, 10.0), "g2": (5.0, 10.0), "g3": (5.0, 10.0), "g4": (5.0, 10.0)},  # 默认重资产带 5-10x；轻资产用 --corr asset_light 切换 15-25x（增速不敏感，重资产公用事业化定价）
}

# 港股一档锚带（v1.7.12 主人校准——市值>50亿全谱系实测，增速期权在港股基本不存在）
# 实证：金蝶 3.55x(+13.6%)/金山 2.98x(+6.1%)/涂鸦 3.38x(+12.3%)/美图 4.44x(+21.5%)/阜博 2.47x(+24%)/联易融 3.81x(+54.6%)/迈富时 4.88x(+100%)
# 规则：中国 AI 应用公司默认港股框架（数据敏感去不了美股，A 股不欢迎）
HK_MATRIX_TIER1 = {
    "g1": (2.5, 4.0), "g2": (3.0, 5.0), "g3": (3.5, 6.0), "g4": (4.0, 6.0),
}

# 增速档边界（供档内插值）
GROWTH_BANDS = {
    "g1": (0.0, 0.15),
    "g2": (0.15, 0.30),
    "g3": (0.30, 0.60),
    "g4": (0.60, 1.00),
}

TIER_NAMES = {
    "tier0": "第零档·项目制（含沉淀定性）",
    "tier1": "一档·订阅/租功能",
    "tier2": "二档·转售智能（无自研/弱自研）",
    "tier3": "三档·自研智能（自研/入口下沿，飞轮/切换成本上沿）",
    "infra": "算力/Infra 段（自持/纳管算力+Token 按量+异构调度——SOTP 单列，不入应用层矩阵）",
}

# ── C1 校验用档位允许范围（v1.15.0 由 MATRIX 派生——不再是第二份人工维护数据）──────────
# 每档取 MATRIX 各增速格的下限 min / 上限 max 作为「档位允许区间」；历史档别名映射保留（报告用中文档名）
TIER_RANGE = {
    "第零档": (min(g[0] for g in MATRIX["tier0"].values()), max(g[1] for g in MATRIX["tier0"].values())),
    "项目制": (min(g[0] for g in MATRIX["tier0"].values()), max(g[1] for g in MATRIX["tier0"].values())),
    "tier0": (min(g[0] for g in MATRIX["tier0"].values()), max(g[1] for g in MATRIX["tier0"].values())),
    "tier0s": (min(g[0] for g in MATRIX["tier0"].values()), max(g[1] for g in MATRIX["tier0"].values())),  # tier0s 已并入 tier0（v1.8.5）
    "有沉淀": (min(g[0] for g in MATRIX["tier0"].values()), max(g[1] for g in MATRIX["tier0"].values())),
    "纯验收单": (min(g[0] for g in MATRIX["tier0"].values()), max(g[1] for g in MATRIX["tier0"].values())),
    "一档": (min(min(g[0] for g in MATRIX["tier1"].values()), min(g[0] for g in HK_MATRIX_TIER1.values())), max(g[1] for g in MATRIX["tier1"].values())),
    "订阅": (min(min(g[0] for g in MATRIX["tier1"].values()), min(g[0] for g in HK_MATRIX_TIER1.values())), max(g[1] for g in MATRIX["tier1"].values())),
    "租功能": (min(min(g[0] for g in MATRIX["tier1"].values()), min(g[0] for g in HK_MATRIX_TIER1.values())), max(g[1] for g in MATRIX["tier1"].values())),
    "tier1": (min(min(g[0] for g in MATRIX["tier1"].values()), min(g[0] for g in HK_MATRIX_TIER1.values())), max(g[1] for g in MATRIX["tier1"].values())),
    "二档": (min(g[0] for g in MATRIX["tier2"].values()), max(g[1] for g in MATRIX["tier2"].values())),
    "纯转售": (min(g[0] for g in MATRIX["tier2"].values()), max(g[1] for g in MATRIX["tier2"].values())),
    "转售智能": (min(g[0] for g in MATRIX["tier2"].values()), max(g[1] for g in MATRIX["tier2"].values())),
    "tier2a": (min(g[0] for g in MATRIX["tier2"].values()), max(g[1] for g in MATRIX["tier2"].values())),
    "tier2b": (min(g[0] for g in MATRIX["tier2"].values()), max(g[1] for g in MATRIX["tier2"].values())),
    "自研型": (min(g[0] for g in MATRIX["tier2"].values()), max(g[1] for g in MATRIX["tier2"].values())),
    "三档": (min(g[0] for g in MATRIX["tier3"].values()), max(g[1] for g in MATRIX["tier3"].values())),
    "收智慧租": (min(g[0] for g in MATRIX["tier3"].values()), max(g[1] for g in MATRIX["tier3"].values())),
    "tier3": (min(g[0] for g in MATRIX["tier3"].values()), max(g[1] for g in MATRIX["tier3"].values())),
}
# 注：v1.13.5 一档下限曾放宽到 2.5（港股 g1 实际锚带 2.5-4x）——该放宽属于「负增长/近零折扣后豁免」场景，
# 由 C1 折扣上下文豁免处理（见 validate.py C1 逻辑），TIER_RANGE 保持 MATRIX 原值。
# 二档上限历史曾到 20（tier2s 自研型），v1.9.0 并入 tier3 后二档=转售智能 5-8x 封顶——派生自动正确。
